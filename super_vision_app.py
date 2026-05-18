import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Super Vision",
    page_icon="👁️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@700;900&family=Nunito:wght@400;600;700&display=swap');
:root {
  --mg:#e91e8c; --mg2:#c01070; --bg:#0d0d0d;
  --card:#1a1a1a; --text:#f0f0f0; --muted:#888;
}
html,body,[class*="css"]{font-family:'Nunito',sans-serif!important;background:var(--bg)!important;color:var(--text)!important;}
.block-container{padding-top:1rem!important;padding-bottom:3rem!important;}
[data-testid="stSidebar"]{background:#120810!important;}
.stButton>button{background:linear-gradient(135deg,#e91e8c,#c01070)!important;color:white!important;border:none!important;border-radius:12px!important;font-family:'Exo 2',sans-serif!important;font-weight:700!important;width:100%!important;padding:0.55rem 1rem!important;margin-bottom:0.3rem!important;}
.stButton>button:hover{opacity:.9!important;}
.metric-grid{display:grid;grid-template-columns:1fr 1fr;gap:.7rem;margin-bottom:1.2rem;}
.mc{background:var(--card);border:1px solid #2a2a2a;border-radius:14px;padding:1rem .5rem;text-align:center;}
.mc .val{font-family:'Exo 2',sans-serif;font-size:1.8rem;font-weight:900;color:#e91e8c;line-height:1.1;}
.mc .lbl{font-size:.72rem;color:var(--muted);margin-top:.2rem;}
.sv-hdr{background:linear-gradient(135deg,#e91e8c,#9c27b0);border-radius:10px;padding:.5rem 1rem;font-family:'Exo 2',sans-serif;font-weight:700;font-size:.95rem;margin:.8rem 0 .6rem;color:white;}
.sv-hdr-green{background:linear-gradient(135deg,#1b5e20,#2e7d32);border-radius:10px;padding:.5rem 1rem;font-family:'Exo 2',sans-serif;font-weight:700;font-size:.95rem;margin:.8rem 0 .6rem;color:white;}
.lcard{background:var(--card);border:1px solid #2a2a2a;border-radius:14px;padding:.9rem 1rem;margin-bottom:.6rem;}
.lcard .nm{font-family:'Exo 2',sans-serif;font-weight:700;font-size:1rem;color:#e91e8c;}
.lcard .sub{font-size:.8rem;color:var(--muted);margin-top:.1rem;}
.badge{display:inline-block;padding:2px 10px;border-radius:20px;font-size:.72rem;font-weight:700;}
.b-pending{background:#3e2300;color:#ff9800;} .b-proceed{background:#1a3a1a;color:#4caf50;}
.b-disbursed{background:#0d2a40;color:#29b6f6;} .b-cancel{background:#3a1a1a;color:#ef5350;}
.b-letter{background:#2a1a3a;color:#ab47bc;}
.ai-danger{background:#1a0000;border:1px solid #ef5350;border-radius:10px;padding:.7rem;color:#ef5350;font-size:.85rem;margin-top:.5rem;}
.ai-warn{background:#1a1000;border:1px solid #ff9800;border-radius:10px;padding:.7rem;color:#ff9800;font-size:.85rem;margin-top:.5rem;}
.ai-ok{background:#001a00;border:1px solid #4caf50;border-radius:10px;padding:.7rem;color:#4caf50;font-size:.85rem;margin-top:.5rem;}
input,textarea,[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stTextArea"] textarea{background:#242424!important;color:#f0f0f0!important;border-color:#333!important;border-radius:10px!important;}
div[data-testid="stForm"]{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:14px;padding:1rem;}
.stTabs [aria-selected="true"]{color:#e91e8c!important;border-bottom-color:#e91e8c!important;}
</style>
""", unsafe_allow_html=True)

# ── Data helpers ──────────────────────────────────────────────────────────────
DATA_DIR = "sv_data"
os.makedirs(DATA_DIR, exist_ok=True)

def _load(fname, default):
    p = os.path.join(DATA_DIR, fname)
    return json.load(open(p)) if os.path.exists(p) else default

def _save(fname, data):
    with open(os.path.join(DATA_DIR, fname), "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_officers():  return _load("officers.json", [])
def save_officers(d): _save("officers.json", d)
def load_loans():     return _load("loans.json", [])
def save_loans(d):    _save("loans.json", d)
def nid(lst):         return max((x.get("id",0) for x in lst), default=0)+1

def calc_risk(loan):
    s  = {"A Grade":10,"B Grade":20,"C Grade":30,"D Grade":40}.get(loan.get("borrower_grade",""),30)
    s += {"Good":5,"Average":15,"Poor":25}.get(loan.get("family_status",""),15)
    s += {"Regular":5,"Irregular":20,"New Member":10}.get(loan.get("repayment_history",""),10)
    s += {"Regular":5,"Irregular":15}.get(loan.get("savings_habit",""),10)
    amt = loan.get("applied_loan_amt",0) or 0
    if amt>200000: s+=20
    elif amt>100000: s+=10
    if s<=30:   return s,"Low Risk","Loan looks safe to approve.","ai-ok"
    elif s<=55: return s,"Medium Risk","Review carefully before approving.","ai-warn"
    else:       return s,"High Risk","The Loan is very Risky. Do not Approve the Loan.","ai-danger"

# ── Session nav ───────────────────────────────────────────────────────────────
if "page" not in st.session_state: st.session_state.page = "dashboard"
def goto(p): st.session_state.page=p; st.rerun()

# ── Sidebar nav ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style='text-align:center;padding:.5rem 0 1rem'>
      <div style='font-family:Exo 2,sans-serif;font-size:1.5rem;font-weight:900;
        background:linear-gradient(135deg,#e91e8c,#00bcd4);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent'>
        👁️ Super Vision</div></div>""", unsafe_allow_html=True)
    if st.button("🏠  Dashboard"):      goto("dashboard")
    if st.button("👤  CO Profiles"):    goto("profiles")
    if st.button("➕  Add Loan Visit"): goto("add_loan")
    if st.button("📋  Loan List"):      goto("loan_list")
    if st.button("📊  Report"):         goto("report")

officers = load_officers()
loans    = load_loans()
page     = st.session_state.page
BC = {"Pending":"b-pending","Proceed":"b-proceed","Disbursed":"b-disbursed",
      "Cancel":"b-cancel","Disburse Letter":"b-letter"}

# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if page == "dashboard":
    st.markdown("""<div style='font-family:Exo 2,sans-serif;font-size:2rem;font-weight:900;
      background:linear-gradient(135deg,#e91e8c,#00bcd4);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:1rem'>
      👁️ Super Vision</div>""", unsafe_allow_html=True)

    tot_amt  = sum(l.get("applied_loan_amt",0) or 0 for l in loans)
    pending  = sum(1 for l in loans if l.get("loan_status")=="Pending")
    disbursed= sum(1 for l in loans if l.get("loan_status")=="Disbursed")

    # 2x2 grid — মোবাইলে সুন্দর
    st.markdown(f"""
    <div class="metric-grid">
      <div class="mc"><div class="val">{len(officers)}</div><div class="lbl">Credit Officers</div></div>
      <div class="mc"><div class="val">{len(loans)}</div><div class="lbl">Total Loan Visits</div></div>
      <div class="mc"><div class="val">{pending}</div><div class="lbl">Pending</div></div>
      <div class="mc"><div class="val">{disbursed}</div><div class="lbl">Disbursed</div></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div class='sv-hdr'>📌 Quick Links</div>", unsafe_allow_html=True)
    if st.button("👤  Profile (CO List)"):  goto("profiles")
    if st.button("📋  Visited Loan List"):  goto("loan_list")
    if st.button("➕  Add New Loan Visit"): goto("add_loan")
    if st.button("📊  Loan Visit Report"):  goto("report")

    if loans:
        st.markdown("<div class='sv-hdr'>📈 Recent Visits</div>", unsafe_allow_html=True)
        for lv in reversed(loans[-5:]):
            bc = BC.get(lv.get("loan_status",""),"b-pending")
            st.markdown(f"""<div class='lcard'>
              <div class='nm'>{lv['member_name']}</div>
              <div class='sub'>{lv.get('village','—')} &nbsp;·&nbsp; {lv.get('visit_date','')}
                &nbsp;<span class='badge {bc}'>{lv.get('loan_status','')}</span></div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CO PROFILES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "profiles":
    st.markdown("<h2 style='font-family:Exo 2,sans-serif;color:#e91e8c'>👤 Profile</h2>",
                unsafe_allow_html=True)
    search = st.text_input("🔍 Search", placeholder="নাম বা পদবি")

    with st.expander("➕ নতুন Officer যোগ করুন"):
        with st.form("add_off"):
            name  = st.text_input("পূর্ণ নাম *")
            desig = st.selectbox("পদবি", [
                "Senior Credit Officer (Progoti)",
                "Credit Officer (Progoti)",
                "Trainee Credit Officer (Progoti)",
                "Assistant Area Manager (Progoti)",
                "Area Manager (Progoti)",
            ])
            branch = st.text_input("Branch")
            mobile = st.text_input("Mobile No")
            if st.form_submit_button("✅ যোগ করুন"):
                if name.strip():
                    officers.append({"id":nid(officers),"name":name.strip(),
                                     "designation":desig,"branch":branch,"mobile":mobile})
                    save_officers(officers)
                    st.success(f"'{name}' যোগ হয়েছে!")
                    st.rerun()
                else: st.error("নাম দিন।")

    filtered = [o for o in officers if not search or
                search.lower() in o["name"].lower() or
                search.lower() in o.get("designation","").lower()]
    if not filtered: st.info("কোনো অফিসার নেই।")
    for off in filtered:
        ol = [l for l in loans if l.get("related_co")==off["name"]]
        with st.expander(f"**{off['name']}**  ·  {off.get('designation','—')}"):
            st.write(f"**Branch:** {off.get('branch','—')}  |  **Mobile:** {off.get('mobile','—')}")
            st.write(f"**মোট ভিজিট:** {len(ol)}")
            for lv in ol[-4:]:
                bc=BC.get(lv.get("loan_status",""),"b-pending")
                st.markdown(f"- {lv['member_name']} <span class='badge {bc}'>{lv.get('loan_status','')}</span>",
                            unsafe_allow_html=True)
            if st.button("🗑️ Delete", key=f"do_{off['id']}"):
                save_officers([o for o in officers if o["id"]!=off["id"]])
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# ADD LOAN VISIT
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "add_loan":
    st.markdown("<h2 style='font-family:Exo 2,sans-serif;color:#e91e8c'>➕ Add Loan Visit</h2>",
                unsafe_allow_html=True)
    co_names = [o["name"] for o in officers] or ["—"]
    if "lf" not in st.session_state: st.session_state.lf={}

    tab1,tab2,tab3,tab4 = st.tabs(["👤 Client","💰 Loan","📊 Status","🧠 Analysis"])

    with tab1:
        st.markdown("<div class='sv-hdr'>Client Details</div>", unsafe_allow_html=True)
        st.session_state.lf["visit_date"]   = str(st.date_input("Visited Date", value=date.today()))
        st.session_state.lf["loan_level"]   = st.selectbox("Loan Level",["New","Repeat","Back From Dropout"])
        st.session_state.lf["member_no"]    = st.text_input("Member No")
        st.session_state.lf["member_name"]  = st.text_input("Member Name *")
        st.session_state.lf["gender"]       = st.selectbox("Gender",["Male","Female","Other"])
        st.session_state.lf["father_name"]  = st.text_input("Father's Name")
        st.session_state.lf["mobile_no"]    = st.text_input("Mobile No")
        st.session_state.lf["village"]      = st.text_input("Village / Market Name")
        st.session_state.lf["occupation"]   = st.selectbox("Occupation",
            ["—","Farmer","Business","Service","Day Labour","Housewife","Other"])

    with tab2:
        st.markdown("<div class='sv-hdr'>Loan Details</div>", unsafe_allow_html=True)
        st.session_state.lf["product"]      = st.selectbox("Product Name",
            ["—","Agriculture","Business","Housing","Education","Health","Sanitation"])
        st.session_state.lf["sub_product"]  = st.multiselect("Sub-Product Name",
            ["Beef Fattening","Vegetable Cultivation","Rice Cultivation","Poultry","Fishery",
             "Small Business","Grocery","Transport","Housing Repair","Tube Well","Latrine"])
        st.session_state.lf["others_project"]   = st.text_area("Others Project", height=70)
        st.session_state.lf["last_closed_loan"] = st.number_input("Last Closed Loan Amt.", min_value=0, step=1000)
        st.session_state.lf["applied_loan_amt"] = st.number_input("Applied Loan Amt. *", min_value=0, step=1000)
        st.session_state.lf["proposed_loan_amt"]= st.number_input("Proposed Loan Amt.", min_value=0, step=1000)
        st.session_state.lf["own_land"]     = st.selectbox("Own Cultivate Land",["—","0","1","2","3","4","5+"])
        st.session_state.lf["bonds_land"]   = st.selectbox("Bonds Cultivate Land",["—","0","1","2","3","4","5+"])
        st.session_state.lf["related_co"]   = st.selectbox("Related CO", co_names)

    with tab3:
        st.markdown("<div class='sv-hdr'>Status & Grade</div>", unsafe_allow_html=True)
        st.session_state.lf["loan_status"]      = st.selectbox("Loan Status",
            ["Pending","Proceed","Disbursed","Cancel","Disburse Letter"])
        st.session_state.lf["family_status"]    = st.selectbox("Family Status",["Good","Average","Poor"])
        st.session_state.lf["borrower_grade"]   = st.selectbox("Borrower Grade",
            ["A Grade","B Grade","C Grade","D Grade"])
        st.session_state.lf["repayment_history"]= st.selectbox("Repayment History",
            ["—","Regular","Irregular","New Member"])
        st.session_state.lf["savings_habit"]    = st.selectbox("Savings Habit",["—","Regular","Irregular"])
        st.session_state.lf["remarks"]          = st.text_area("Remarks", height=60)

        st.markdown("<div class='sv-hdr'>Grantor</div>", unsafe_allow_html=True)
        st.session_state.lf["grantor_name"]    = st.text_input("Grantor Name")
        st.session_state.lf["grantor_father"]  = st.text_input("Grantor's Father Name")
        st.session_state.lf["grantor_mobile"]  = st.text_input("Grantor's Mobile")
        st.session_state.lf["grantor_address"] = st.text_input("Grantor Address")

        st.markdown("<div class='sv-hdr'>Family Member</div>", unsafe_allow_html=True)
        st.session_state.lf["fam_member_name"] = st.text_input("Family Member Name")
        st.session_state.lf["fam_relation"]    = st.selectbox("Relation",
            ["—","Spouse","Son","Daughter","Father","Mother","Brother","Sister","Other"])
        st.session_state.lf["fam_mobile"]      = st.text_input("Family Member Mobile")
        st.session_state.lf["fam_occupation"]  = st.selectbox("Family Occupation",
            ["—","Farmer","Business","Service","Day Labour","Student","Housewife","Other"])

    with tab4:
        st.markdown("<div class='sv-hdr'>Loan Analysis</div>", unsafe_allow_html=True)
        st.session_state.lf["member_age"]       = st.number_input("Member Age",18,80,30)
        st.session_state.lf["smartphone_use"]   = st.selectbox("Smartphone Use",["Yes","No"])
        st.session_state.lf["business_income"]  = st.number_input("Business Income",0,step=500)
        st.session_state.lf["agri_income"]      = st.number_input("Agriculture Income",0,step=500)
        st.session_state.lf["remittance"]       = st.number_input("Remittance Income",0,step=500)
        st.session_state.lf["others_income"]    = st.number_input("Others Income",0,step=500)
        st.markdown("**Expenses:**")
        st.session_state.lf["food_expense"]     = st.number_input("Food Expense",0,step=500)
        st.session_state.lf["education_expense"]= st.number_input("Education Expense",0,step=500)
        st.session_state.lf["medical_expense"]  = st.number_input("Medical Expense",0,step=500)
        st.session_state.lf["house_rent"]       = st.number_input("House Rent",0,step=500)
        st.session_state.lf["others_emi"]       = st.number_input("Others Loan EMI",0,step=500)
        st.session_state.lf["others_expense"]   = st.number_input("Others Expense",0,step=500)

    st.markdown("---")
    if st.button("✅  Submit Loan Visit", use_container_width=True):
        lf = st.session_state.lf
        if not lf.get("member_name","").strip():
            st.error("Member Name দিন!")
        else:
            new = dict(lf)
            new["id"] = nid(loans)
            new["created_at"] = str(datetime.now())
            loans.append(new)
            save_loans(loans)
            st.success(f"✅ **{lf['member_name']}** — সংরক্ষিত!")
            st.session_state.lf = {}
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# LOAN LIST
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "loan_list":
    st.markdown("<h2 style='font-family:Exo 2,sans-serif;color:#e91e8c'>📋 Visited Loan List</h2>",
                unsafe_allow_html=True)

    search = st.text_input("🔍 Search", placeholder="নাম / মোবাইল")
    c1,c2  = st.columns(2)
    with c1: fco = st.selectbox("CO Filter",["All"]+[o["name"] for o in officers])
    with c2: fst = st.selectbox("Status",["All","Pending","Proceed","Disbursed","Cancel","Disburse Letter"])

    filtered = loans
    if search:
        filtered=[l for l in filtered if search.lower() in l["member_name"].lower()
                  or search in l.get("mobile_no","")]
    if fco!="All": filtered=[l for l in filtered if l.get("related_co")==fco]
    if fst!="All": filtered=[l for l in filtered if l.get("loan_status")==fst]

    st.caption(f"{len(filtered)} টি রেকর্ড")
    if not filtered: st.info("কোনো রেকর্ড নেই।")

    for lv in reversed(filtered):
        bc = BC.get(lv.get("loan_status",""),"b-pending")
        rs,rl,ai_msg,ai_cls = calc_risk(lv)

        with st.expander(f"**{lv['member_name']}**  ·  {lv.get('village','—')}"):
            st.markdown("<div class='sv-hdr'>👤 Personal Info</div>", unsafe_allow_html=True)
            st.write(f"**নাম:** {lv['member_name']}  |  **Gender:** {lv.get('gender','—')}")
            st.write(f"**Father:** {lv.get('father_name','—')}  |  **Mobile:** {lv.get('mobile_no','—')}")
            st.write(f"**Village:** {lv.get('village','—')}  |  **Occupation:** {lv.get('occupation','—')}")

            st.markdown("<div class='sv-hdr'>💰 Loan Info</div>", unsafe_allow_html=True)
            st.write(f"**Date:** {lv.get('visit_date','—')}  |  **Level:** {lv.get('loan_level','—')}")
            st.write(f"**Product:** {lv.get('product','—')}")
            sp=lv.get('sub_product',[])
            if sp: st.write(f"**Sub-Product:** {', '.join(sp)}")
            if lv.get('others_project'): st.write(f"**Others:** {lv['others_project']}")
            st.write(f"**Applied Amt:** BDT {lv.get('applied_loan_amt',0):,}")
            st.write(f"**Grade:** {lv.get('borrower_grade','—')}  |  **Family:** {lv.get('family_status','—')}")
            st.write(f"**Related CO:** {lv.get('related_co','—')}")

            st.markdown("<div class='sv-hdr-green'>✅ Loan Visit Check List</div>", unsafe_allow_html=True)
            for c in ["Discuss Loan details with Member",
                      "Discuss Loan Details With Family Members",
                      "Visit Loan Project and Member House",
                      "Visit Grantor House and Discuss About Loan"]:
                st.checkbox(c, key=f"c_{lv['id']}_{c[:6]}")

            st.markdown("<div class='sv-hdr-green'>📊 Loan Status</div>", unsafe_allow_html=True)
            st.markdown(f"**Status:** <span class='badge {bc}'>{lv.get('loan_status','')}</span>",
                        unsafe_allow_html=True)

            st.markdown("<div class='sv-hdr'>⚡ Loan Analysis</div>", unsafe_allow_html=True)
            st.write(f"**Risk Score:** {rs}  |  **Decision:** {rl}")
            st.markdown(f"<div class='{ai_cls}'>🤖 AI Recommendation: {ai_msg}</div>",
                        unsafe_allow_html=True)

            if lv.get("grantor_name"):
                st.markdown("<div class='sv-hdr'>🛡️ Grantor</div>", unsafe_allow_html=True)
                st.write(f"{lv['grantor_name']}  |  {lv.get('grantor_mobile','—')}")

            st.markdown("---")
            new_st = st.selectbox("স্ট্যাটাস আপডেট",
                ["Pending","Proceed","Disbursed","Cancel","Disburse Letter"],
                index=["Pending","Proceed","Disbursed","Cancel","Disburse Letter"].index(
                    lv.get("loan_status","Pending")), key=f"us_{lv['id']}")
            new_rm = st.text_input("Remarks", value=lv.get("remarks",""), key=f"ur_{lv['id']}")
            c1,c2  = st.columns(2)
            with c1:
                if st.button("💾 Update", key=f"ub_{lv['id']}"):
                    for l in loans:
                        if l["id"]==lv["id"]:
                            l["loan_status"]=new_st; l["remarks"]=new_rm
                    save_loans(loans)
                    st.success("আপডেট হয়েছে!"); st.rerun()
            with c2:
                if st.button("🗑️ Delete", key=f"db_{lv['id']}"):
                    save_loans([l for l in loans if l["id"]!=lv["id"]]); st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# REPORT
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "report":
    st.markdown("<h2 style='font-family:Exo 2,sans-serif;color:#e91e8c'>📊 CO Wise Report</h2>",
                unsafe_allow_html=True)

    if not officers: st.info("কোনো অফিসার নেই।")
    else:
        for off in officers:
            ol  = [l for l in loans if l.get("related_co")==off["name"]]
            tot = sum(l.get("applied_loan_amt",0) or 0 for l in ol)
            with st.expander(f"**{off['name']}**  ·  {len(ol)} visits  ·  BDT {tot:,}"):
                c1,c2=st.columns(2)
                with c1:
                    st.metric("মোট ভিজিট",len(ol))
                    st.metric("Pending",sum(1 for l in ol if l.get("loan_status")=="Pending"))
                with c2:
                    st.metric("Applied Amt.",f"BDT {tot:,}")
                    st.metric("Disbursed",sum(1 for l in ol if l.get("loan_status")=="Disbursed"))
                if ol:
                    rows=[{"Member":l["member_name"],"Date":l.get("visit_date",""),
                           "Product":l.get("product",""),"Amount":l.get("applied_loan_amt",0),
                           "Status":l.get("loan_status",""),"Grade":l.get("borrower_grade","")} for l in ol]
                    df=pd.DataFrame(rows)
                    st.dataframe(df,use_container_width=True,hide_index=True)
                    st.download_button(f"⬇️ Export CSV",df.to_csv(index=False).encode(),
                        f"{off['name']}_report.csv","text/csv",key=f"exp_{off['id']}")

        st.markdown("---")
        st.markdown("<div class='sv-hdr'>🏢 Branch Total</div>", unsafe_allow_html=True)
        c1,c2=st.columns(2)
        tot_all=sum(l.get("applied_loan_amt",0) or 0 for l in loans)
        with c1:
            st.metric("Total Officers",len(officers))
            st.metric("Total Visits",len(loans))
        with c2:
            st.metric("Total Amount",f"BDT {tot_all:,}")
            st.metric("Disbursed",sum(1 for l in loans if l.get("loan_status")=="Disbursed"))
        if loans:
            st.download_button("⬇️ Export All Loans",
                pd.DataFrame(loans).to_csv(index=False).encode(),"all_loans.csv","text/csv")

