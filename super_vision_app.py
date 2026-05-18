import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Super Vision",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@400;600;700;900&family=Nunito:wght@400;600;700&display=swap');

:root {
    --magenta: #e91e8c;
    --magenta-dark: #c01070;
    --teal: #00bcd4;
    --bg: #0d0d0d;
    --card: #1a1a1a;
    --card2: #242424;
    --text: #f0f0f0;
    --muted: #888;
    --success: #2e7d32;
    --warning: #f57c00;
    --danger: #c62828;
}

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
    background: var(--bg);
    color: var(--text);
}

h1, h2, h3 { font-family: 'Exo 2', sans-serif; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a0a14 0%, #0d0d0d 100%);
    border-right: 1px solid #2a2a2a;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--magenta), var(--magenta-dark));
    color: white;
    border: none;
    border-radius: 12px;
    font-family: 'Exo 2', sans-serif;
    font-weight: 700;
    padding: 0.5rem 1.5rem;
    transition: all 0.2s;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(233,30,140,0.4);
}

/* Cards */
.sv-card {
    background: var(--card);
    border: 1px solid #2a2a2a;
    border-radius: 16px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    transition: border-color 0.2s;
}
.sv-card:hover { border-color: var(--magenta); }

.sv-header {
    background: linear-gradient(135deg, var(--magenta), #9c27b0);
    border-radius: 12px;
    padding: 0.6rem 1rem;
    margin-bottom: 1rem;
    font-family: 'Exo 2', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    letter-spacing: 0.5px;
}

/* Metric cards */
.metric-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.metric-card {
    flex: 1;
    background: var(--card);
    border: 1px solid #2a2a2a;
    border-radius: 14px;
    padding: 1rem;
    text-align: center;
}
.metric-card .val {
    font-family: 'Exo 2', sans-serif;
    font-size: 2rem;
    font-weight: 900;
    color: var(--magenta);
}
.metric-card .lbl { font-size: 0.8rem; color: var(--muted); }

/* Status badges */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
}
.badge-pending  { background:#3e2300; color:#ff9800; }
.badge-proceed  { background:#1a3a1a; color:#4caf50; }
.badge-disbursed{ background:#0d2a40; color:#29b6f6; }
.badge-cancel   { background:#3a1a1a; color:#ef5350; }
.badge-letter   { background:#2a1a3a; color:#ab47bc; }

/* Risk */
.risk-high   { color:#ef5350; font-weight:700; }
.risk-medium { color:#ff9800; font-weight:700; }
.risk-low    { color:#4caf50; font-weight:700; }

/* AI box */
.ai-box {
    background: #1a0a0a;
    border: 1px solid #ef5350;
    border-radius: 12px;
    padding: 0.8rem 1rem;
    color: #ef5350;
    font-weight: 600;
    margin-top: 0.5rem;
}
.ai-box-ok {
    background: #0a1a0a;
    border: 1px solid #4caf50;
    border-radius: 12px;
    padding: 0.8rem 1rem;
    color: #4caf50;
    font-weight: 600;
    margin-top: 0.5rem;
}

/* Input tweaks */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] div,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: #242424 !important;
    border: 1px solid #333 !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}

div[data-testid="stForm"] {
    background: var(--card2);
    border: 1px solid #2a2a2a;
    border-radius: 16px;
    padding: 1.5rem;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Exo 2', sans-serif;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    color: var(--magenta) !important;
    border-bottom-color: var(--magenta) !important;
}

hr { border-color: #2a2a2a; }
</style>
""", unsafe_allow_html=True)

# ── Data persistence (JSON files) ─────────────────────────────────────────────
DATA_DIR = "sv_data"
os.makedirs(DATA_DIR, exist_ok=True)

def load_json(fname, default):
    path = os.path.join(DATA_DIR, fname)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def save_json(fname, data):
    with open(os.path.join(DATA_DIR, fname), "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_officers():  return load_json("officers.json", [])
def save_officers(d): save_json("officers.json", d)
def load_loans():     return load_json("loans.json", [])
def save_loans(d):    save_json("loans.json", d)

# ── Helper: next ID ───────────────────────────────────────────────────────────
def next_id(lst, field="id"):
    return max((x.get(field,0) for x in lst), default=0) + 1

# ── Risk calculator ───────────────────────────────────────────────────────────
def calculate_risk(loan: dict) -> tuple[int, str, str]:
    score = 0
    grade = loan.get("borrower_grade","")
    family = loan.get("family_status","")
    rep = loan.get("repayment_history","")
    savings = loan.get("savings_habit","")
    amt = loan.get("applied_loan_amt", 0) or 0

    if grade == "A Grade": score += 10
    elif grade == "B Grade": score += 20
    elif grade == "C Grade": score += 30
    else: score += 40

    if family == "Good": score += 5
    elif family == "Average": score += 15
    else: score += 25

    if rep == "Regular": score += 5
    elif rep == "Irregular": score += 20
    else: score += 10

    if savings == "Regular": score += 5
    else: score += 15

    if amt > 200000: score += 20
    elif amt > 100000: score += 10

    if score <= 30:
        return score, "Low Risk", "✅ Loan looks safe to approve."
    elif score <= 55:
        return score, "Medium Risk", "⚠️ Review carefully before approving."
    else:
        return score, "High Risk", "❌ The Loan is very Risky. Do not Approve the Loan."

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1rem 0'>
      <div style='font-family:Exo 2,sans-serif;font-size:1.8rem;font-weight:900;
                  background:linear-gradient(135deg,#e91e8c,#00bcd4);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent'>
        👁️ Super Vision
      </div>
      <div style='color:#888;font-size:0.8rem'>Loan Visit Management</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    page = st.radio("Navigation", [
        "🏠 Dashboard",
        "👤 CO Profiles",
        "📋 Visited Loan List",
        "➕ Add Loan Visit",
        "📊 Loan Visit Report",
    ], label_visibility="collapsed")

    st.divider()
    st.caption("Super Vision v1.0 · Python Edition")

# ── Load data ─────────────────────────────────────────────────────────────────
officers = load_officers()
loans    = load_loans()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.markdown("<h1 style='font-family:Exo 2,sans-serif;color:#e91e8c'>Super Vision</h1>", unsafe_allow_html=True)

    total_loans     = len(loans)
    pending_loans   = sum(1 for l in loans if l.get("loan_status") == "Pending")
    disbursed_loans = sum(1 for l in loans if l.get("loan_status") == "Disbursed")
    total_amount    = sum(l.get("applied_loan_amt", 0) or 0 for l in loans)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class='metric-card'>
            <div class='val'>{len(officers)}</div>
            <div class='lbl'>Credit Officers</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='metric-card'>
            <div class='val'>{total_loans}</div>
            <div class='lbl'>Total Loan Visits</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class='metric-card'>
            <div class='val'>{pending_loans}</div>
            <div class='lbl'>Pending</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class='metric-card'>
            <div class='val'>৳{total_amount:,.0f}</div>
            <div class='lbl'>Total Applied Amount</div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='sv-header'>📌 Quick Links</div>", unsafe_allow_html=True)
        if st.button("👤 Profile (CO List)"):
            st.session_state["_nav"] = "👤 CO Profiles"
            st.rerun()
        if st.button("📋 Visited Loan List"):
            st.session_state["_nav"] = "📋 Visited Loan List"
            st.rerun()
        if st.button("➕ Add New Loan Visit"):
            st.session_state["_nav"] = "➕ Add Loan Visit"
            st.rerun()
        if st.button("📊 Loan Visit Report"):
            st.session_state["_nav"] = "📊 Loan Visit Report"
            st.rerun()

    with col2:
        st.markdown("<div class='sv-header'>📈 Loan Status Summary</div>", unsafe_allow_html=True)
        status_counts = {}
        for l in loans:
            s = l.get("loan_status", "Unknown")
            status_counts[s] = status_counts.get(s, 0) + 1
        if status_counts:
            df_status = pd.DataFrame(list(status_counts.items()), columns=["Status","Count"])
            st.dataframe(df_status, use_container_width=True, hide_index=True)
        else:
            st.info("No loan visits recorded yet.")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: CO PROFILES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "👤 CO Profiles":
    st.markdown("<h2 style='font-family:Exo 2,sans-serif;color:#e91e8c'>👤 Profile</h2>", unsafe_allow_html=True)

    search = st.text_input("🔍 Search officer...", placeholder="Name or designation")

    # Add new officer
    with st.expander("➕ Add New Officer"):
        with st.form("add_officer"):
            st.markdown("<div class='sv-header'>New Credit Officer</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                o_name  = st.text_input("Full Name *")
                o_desig = st.selectbox("Designation", [
                    "Senior Credit Officer (Progoti)",
                    "Credit Officer (Progoti)",
                    "Trainee Credit Officer (Progoti)",
                    "Assistant Area Manager (Progoti)",
                    "Area Manager (Progoti)",
                ])
            with c2:
                o_branch = st.text_input("Branch")
                o_mobile = st.text_input("Mobile No")

            o_email = st.text_input("Email")
            if st.form_submit_button("✅ Add Officer"):
                if o_name.strip():
                    officers.append({
                        "id": next_id(officers),
                        "name": o_name.strip(),
                        "designation": o_desig,
                        "branch": o_branch,
                        "mobile": o_mobile,
                        "email": o_email,
                    })
                    save_officers(officers)
                    st.success(f"Officer '{o_name}' added!")
                    st.rerun()
                else:
                    st.error("Name is required.")

    st.markdown("---")

    filtered = [o for o in officers if
                not search or search.lower() in o["name"].lower() or
                search.lower() in o.get("designation","").lower()]

    if not filtered:
        st.info("No officers found. Add one above.")
    else:
        cols = st.columns(3)
        for i, off in enumerate(filtered):
            with cols[i % 3]:
                officer_loans = [l for l in loans if l.get("related_co") == off["name"]]
                st.markdown(f"""
                <div class='sv-card'>
                  <div style='font-family:Exo 2,sans-serif;font-size:1.05rem;
                              font-weight:700;color:#e91e8c'>{off['name']}</div>
                  <div style='font-size:0.8rem;color:#888;margin-bottom:0.5rem'>
                    {off.get('designation','')}
                  </div>
                  <div style='font-size:0.82rem'>📍 {off.get('branch','—')}</div>
                  <div style='font-size:0.82rem'>📱 {off.get('mobile','—')}</div>
                  <div style='font-size:0.82rem;margin-top:0.4rem'>
                    Loans visited: <b style='color:#e91e8c'>{len(officer_loans)}</b>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander(f"View details — {off['name']}"):
                    st.write(f"**Name:** {off['name']}")
                    st.write(f"**Designation:** {off.get('designation','—')}")
                    st.write(f"**Branch:** {off.get('branch','—')}")
                    st.write(f"**Mobile:** {off.get('mobile','—')}")
                    st.write(f"**Email:** {off.get('email','—')}")

                    if officer_loans:
                        st.markdown("**Visited Loan List:**")
                        for lv in officer_loans[-5:]:
                            badge_map = {
                                "Pending":"badge-pending","Proceed":"badge-proceed",
                                "Disbursed":"badge-disbursed","Cancel":"badge-cancel",
                                "Disburse Letter":"badge-letter"
                            }
                            bclass = badge_map.get(lv.get("loan_status",""),"badge-pending")
                            st.markdown(
                                f"- **{lv['member_name']}** "
                                f"<span class='badge {bclass}'>{lv.get('loan_status','')}</span>",
                                unsafe_allow_html=True)

                    if st.button(f"🗑️ Delete", key=f"del_off_{off['id']}"):
                        officers = [o for o in officers if o["id"] != off["id"]]
                        save_officers(officers)
                        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ADD LOAN VISIT
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add Loan Visit":
    st.markdown("<h2 style='font-family:Exo 2,sans-serif;color:#e91e8c'>➕ Add Loan Visit</h2>", unsafe_allow_html=True)

    officer_names = [o["name"] for o in officers] or ["—"]

    with st.form("add_loan"):
        # ── Tab-style section picker ──
        st.markdown("<div class='sv-header'>📋 Client Details</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            visit_date  = st.date_input("Loan Visited Date *", value=date.today())
            loan_level  = st.selectbox("Loan Level", ["New", "Repeat", "Back From Dropout"])
            member_no   = st.text_input("Member No")
            member_name = st.text_input("Member Name *")
            gender      = st.selectbox("Gender", ["Male", "Female", "Other"])
            father_name = st.text_input("Father's Name")
            mobile_no   = st.text_input("Mobile No")
        with c2:
            village     = st.text_input("Village / Market Name")
            occupation  = st.selectbox("Occupation", ["—","Farmer","Business","Service","Day Labour","Housewife","Other"])
            product     = st.selectbox("Product Name", ["—","Agriculture","Business","Housing","Education","Health","Sanitation"])
            sub_product = st.multiselect("Sub-Product Name", [
                "Beef Fattening","Vegetable Cultivation","Rice Cultivation",
                "Poultry","Fishery","Small Business","Grocery","Transport",
                "Housing Repair","Tube Well","Latrine",
            ])
            others_proj = st.text_area("Others Project", height=80)

        st.markdown("<div class='sv-header'>💰 Loan Details</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            last_closed = st.number_input("Last Closed Loan Amt.", min_value=0, step=1000)
            applied_amt = st.number_input("Applied Loan Amt. *", min_value=0, step=1000)
        with c2:
            proposed_amt = st.number_input("Proposed Loan Amt.", min_value=0, step=1000)
            own_land     = st.selectbox("Own Cultivate Land", ["—","0","1","2","3","4","5+"])
        with c3:
            bonds_land   = st.selectbox("Bonds Cultivate Land", ["—","0","1","2","3","4","5+"])
            related_co   = st.selectbox("Related CO", officer_names)

        st.markdown("<div class='sv-header'>📊 Status & Grade</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            loan_status  = st.selectbox("Loan Status", ["Pending","Proceed","Disbursed","Cancel","Disburse Letter"])
            family_status= st.selectbox("Family Status", ["Good","Average","Poor"])
        with c2:
            borrower_grade = st.selectbox("Borrower Grade", ["A Grade","B Grade","C Grade","D Grade"])
            repayment_hist = st.selectbox("Repayment History", ["—","Regular","Irregular","New Member"])
        with c3:
            savings_habit  = st.selectbox("Savings Habit", ["—","Regular","Irregular"])
            remarks        = st.text_area("Remarks", height=60)

        st.markdown("<div class='sv-header'>👨‍👩‍👧 Grantor & Family</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            grantor_name   = st.text_input("Grantor Name")
            grantor_father = st.text_input("Grantor's Father Name")
            grantor_mobile = st.text_input("Grantor's Mobile No")
            grantor_addr   = st.text_input("Grantor Address")
        with c2:
            fam_member_name = st.text_input("Family Member Name")
            fam_relation    = st.selectbox("Relation", ["—","Spouse","Son","Daughter","Father","Mother","Brother","Sister","Other"])
            fam_mobile      = st.text_input("Family Member Mobile")
            fam_occupation  = st.selectbox("Family Member Occupation", ["—","Farmer","Business","Service","Day Labour","Student","Housewife","Other"])

        st.markdown("<div class='sv-header'>🧠 Loan Analysis</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            member_age       = st.number_input("Member Age", min_value=18, max_value=80, value=30)
            smartphone_use   = st.selectbox("Smartphone Use", ["Yes","No"])
            business_income  = st.number_input("Business Income", min_value=0, step=500)
            agri_income      = st.number_input("Agriculture Income", min_value=0, step=500)
        with c2:
            remittance       = st.number_input("Remittance Income", min_value=0, step=500)
            others_income    = st.number_input("Others Income", min_value=0, step=500)
            food_exp         = st.number_input("Food Expense", min_value=0, step=500)
            education_exp    = st.number_input("Education Expense", min_value=0, step=500)
        c1, c2, c3 = st.columns(3)
        with c1:
            medical_exp = st.number_input("Medical Expense", min_value=0, step=500)
            house_rent  = st.number_input("House Rent", min_value=0, step=500)
        with c2:
            others_emi  = st.number_input("Others Loan EMI", min_value=0, step=500)
            others_exp  = st.number_input("Others Expense", min_value=0, step=500)
        with c3:
            pass  # spacer

        submitted = st.form_submit_button("✅ Submit Loan Visit", use_container_width=True)
        if submitted:
            if not member_name.strip():
                st.error("Member Name is required.")
            else:
                new_loan = {
                    "id": next_id(loans),
                    "visit_date": str(visit_date),
                    "loan_level": loan_level,
                    "member_no": member_no,
                    "member_name": member_name.strip(),
                    "gender": gender,
                    "father_name": father_name,
                    "mobile_no": mobile_no,
                    "village": village,
                    "occupation": occupation,
                    "product": product,
                    "sub_product": sub_product,
                    "others_project": others_proj,
                    "last_closed_loan": last_closed,
                    "applied_loan_amt": applied_amt,
                    "proposed_loan_amt": proposed_amt,
                    "own_land": own_land,
                    "bonds_land": bonds_land,
                    "related_co": related_co,
                    "loan_status": loan_status,
                    "family_status": family_status,
                    "borrower_grade": borrower_grade,
                    "repayment_history": repayment_hist,
                    "savings_habit": savings_habit,
                    "remarks": remarks,
                    "grantor_name": grantor_name,
                    "grantor_father": grantor_father,
                    "grantor_mobile": grantor_mobile,
                    "grantor_address": grantor_addr,
                    "fam_member_name": fam_member_name,
                    "fam_relation": fam_relation,
                    "fam_mobile": fam_mobile,
                    "fam_occupation": fam_occupation,
                    "member_age": member_age,
                    "smartphone_use": smartphone_use,
                    "business_income": business_income,
                    "agri_income": agri_income,
                    "remittance": remittance,
                    "others_income": others_income,
                    "food_expense": food_exp,
                    "education_expense": education_exp,
                    "medical_expense": medical_exp,
                    "house_rent": house_rent,
                    "others_emi": others_emi,
                    "others_expense": others_exp,
                    "created_at": str(datetime.now()),
                }
                loans.append(new_loan)
                save_loans(loans)
                st.success(f"✅ Loan visit for **{member_name}** saved successfully!")
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: VISITED LOAN LIST
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Visited Loan List":
    st.markdown("<h2 style='font-family:Exo 2,sans-serif;color:#e91e8c'>📋 Visited Loan List</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("🔍 Search member", placeholder="Name / mobile")
    with col2:
        filter_co = st.selectbox("Filter by CO", ["All"] + [o["name"] for o in officers])
    with col3:
        filter_status = st.selectbox("Filter by Status", ["All","Pending","Proceed","Disbursed","Cancel","Disburse Letter"])

    filtered = loans
    if search:
        filtered = [l for l in filtered if
                    search.lower() in l["member_name"].lower() or
                    search in l.get("mobile_no","")]
    if filter_co != "All":
        filtered = [l for l in filtered if l.get("related_co") == filter_co]
    if filter_status != "All":
        filtered = [l for l in filtered if l.get("loan_status") == filter_status]

    st.caption(f"Showing {len(filtered)} records")

    if not filtered:
        st.info("No loan visits found.")
    else:
        badge_map = {
            "Pending":"badge-pending","Proceed":"badge-proceed",
            "Disbursed":"badge-disbursed","Cancel":"badge-cancel",
            "Disburse Letter":"badge-letter"
        }

        for lv in reversed(filtered):
            bclass = badge_map.get(lv.get("loan_status",""),"badge-pending")
            risk_score, risk_label, ai_rec = calculate_risk(lv)
            risk_class = "risk-high" if "High" in risk_label else ("risk-medium" if "Medium" in risk_label else "risk-low")

            with st.expander(
                f"**{lv['member_name']}** · {lv.get('village','—')} · "
                f"{lv.get('visit_date','')}"):

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class='sv-header'>👤 Personal Information</div>
                    """, unsafe_allow_html=True)
                    st.write(f"**Member Name:** {lv['member_name']}")
                    st.write(f"**Gender:** {lv.get('gender','—')}")
                    st.write(f"**Father's Name:** {lv.get('father_name','—')}")
                    st.write(f"**Mobile:** {lv.get('mobile_no','—')}")
                    st.write(f"**Village/Market:** {lv.get('village','—')}")
                    st.write(f"**Occupation:** {lv.get('occupation','—')}")

                    st.markdown("<div class='sv-header' style='margin-top:0.8rem'>💰 Loan Information</div>", unsafe_allow_html=True)
                    st.write(f"**Visit Date:** {lv.get('visit_date','—')}")
                    st.write(f"**Loan Level:** {lv.get('loan_level','—')}")
                    st.write(f"**Product:** {lv.get('product','—')}")
                    st.write(f"**Sub-Product:** {', '.join(lv.get('sub_product',[]))}")
                    st.write(f"**Others Project:** {lv.get('others_project','—')}")
                    st.write(f"**Applied Loan Amt.:** ৳{lv.get('applied_loan_amt',0):,}")
                    st.write(f"**Borrower Grade:** {lv.get('borrower_grade','—')}")
                    st.write(f"**Family Status:** {lv.get('family_status','—')}")
                    st.write(f"**Own Cultivate Land:** {lv.get('own_land','—')}")
                    st.write(f"**Related CO:** {lv.get('related_co','—')}")

                with col2:
                    st.markdown("<div class='sv-header'>📊 Loan Visit Checklist</div>", unsafe_allow_html=True)
                    checks = [
                        "Discuss Loan details with Member",
                        "Discuss Loan Details With Family Members",
                        "Visit Loan Project and Member House",
                        "Visit Grantor House and Discuss About Loan",
                    ]
                    for ch in checks:
                        st.checkbox(ch, key=f"chk_{lv['id']}_{ch[:10]}")

                    st.markdown("<div class='sv-header' style='background:linear-gradient(135deg,#1a5c2e,#2e7d32);margin-top:0.8rem'>✅ Loan Status</div>", unsafe_allow_html=True)
                    st.markdown(
                        f"**Loan Status:** <span class='badge {bclass}'>{lv.get('loan_status','')}</span>",
                        unsafe_allow_html=True)

                    st.markdown("<div class='sv-header' style='background:linear-gradient(135deg,#4a148c,#7b1fa2);margin-top:0.8rem'>⚡ Loan Analysis</div>", unsafe_allow_html=True)
                    st.write(f"**Risk Score:** {risk_score}")
                    st.markdown(f"**Final Decision:** <span class='{risk_class}'>{risk_label}</span>", unsafe_allow_html=True)

                    if "High" in risk_label:
                        st.markdown(f"<div class='ai-box'>🤖 AI Recommendation:- {ai_rec}</div>", unsafe_allow_html=True)
                    elif "Medium" in risk_label:
                        st.markdown(f"<div class='ai-box' style='border-color:#ff9800;color:#ff9800'>🤖 AI Recommendation:- {ai_rec}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='ai-box-ok'>🤖 AI Recommendation:- {ai_rec}</div>", unsafe_allow_html=True)

                    if lv.get("grantor_name"):
                        st.markdown("<div class='sv-header' style='margin-top:0.8rem'>🛡️ Grantor</div>", unsafe_allow_html=True)
                        st.write(f"**Name:** {lv.get('grantor_name','—')}")
                        st.write(f"**Mobile:** {lv.get('grantor_mobile','—')}")
                        st.write(f"**Address:** {lv.get('grantor_address','—')}")

                # Update status
                st.markdown("---")
                ucol1, ucol2, ucol3 = st.columns([2,2,1])
                with ucol1:
                    new_status = st.selectbox(
                        "Update Status",
                        ["Pending","Proceed","Disbursed","Cancel","Disburse Letter"],
                        index=["Pending","Proceed","Disbursed","Cancel","Disburse Letter"].index(lv.get("loan_status","Pending")),
                        key=f"upd_status_{lv['id']}"
                    )
                with ucol2:
                    new_remarks = st.text_input("Remarks", value=lv.get("remarks",""), key=f"upd_rem_{lv['id']}")
                with ucol3:
                    st.write("")
                    if st.button("💾 Update", key=f"upd_btn_{lv['id']}"):
                        for l in loans:
                            if l["id"] == lv["id"]:
                                l["loan_status"] = new_status
                                l["remarks"] = new_remarks
                        save_loans(loans)
                        st.success("Updated!")
                        st.rerun()

                if st.button(f"🗑️ Delete Visit", key=f"del_loan_{lv['id']}"):
                    loans_new = [l for l in loans if l["id"] != lv["id"]]
                    save_loans(loans_new)
                    st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: LOAN VISIT REPORT
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Loan Visit Report":
    st.markdown("<h2 style='font-family:Exo 2,sans-serif;color:#e91e8c'>📊 Credit Officer Wise Report</h2>", unsafe_allow_html=True)

    if not officers:
        st.info("No officers added yet.")
    else:
        for off in officers:
            off_loans = [l for l in loans if l.get("related_co") == off["name"]]
            total_amt = sum(l.get("applied_loan_amt",0) or 0 for l in off_loans)

            badge_map = {
                "Pending":"badge-pending","Proceed":"badge-proceed",
                "Disbursed":"badge-disbursed","Cancel":"badge-cancel",
                "Disburse Letter":"badge-letter"
            }

            with st.expander(f"**{off['name']}** · {off.get('designation','—')} · {len(off_loans)} visits"):
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("Total Visits", len(off_loans))
                with c2:
                    st.metric("Total Applied Amt.", f"৳{total_amt:,.0f}")
                with c3:
                    pending = sum(1 for l in off_loans if l.get("loan_status") == "Pending")
                    st.metric("Pending", pending)
                with c4:
                    disbursed = sum(1 for l in off_loans if l.get("loan_status") == "Disbursed")
                    st.metric("Disbursed", disbursed)

                if off_loans:
                    st.markdown("---")
                    rows = []
                    for lv in off_loans:
                        rows.append({
                            "Member": lv["member_name"],
                            "Visit Date": lv.get("visit_date",""),
                            "Product": lv.get("product",""),
                            "Applied Amt": f"৳{lv.get('applied_loan_amt',0):,}",
                            "Status": lv.get("loan_status",""),
                            "Grade": lv.get("borrower_grade",""),
                            "Village": lv.get("village",""),
                        })
                    df = pd.DataFrame(rows)
                    st.dataframe(df, use_container_width=True, hide_index=True)

                    # CSV export
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        f"⬇️ Export {off['name']}'s Report (CSV)",
                        csv,
                        f"{off['name']}_report.csv",
                        "text/csv",
                        key=f"exp_{off['id']}"
                    )

        # Branch total
        st.markdown("---")
        st.markdown("<h3 style='font-family:Exo 2,sans-serif;color:#00bcd4'>🏢 Branch Total</h3>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Total Officers", len(officers))
        with c2: st.metric("Total Loan Visits", len(loans))
        with c3:
            tot = sum(l.get("applied_loan_amt",0) or 0 for l in loans)
            st.metric("Total Applied Amt.", f"৳{tot:,.0f}")
        with c4:
            dis = sum(1 for l in loans if l.get("loan_status")=="Disbursed")
            st.metric("Total Disbursed", dis)

        # All-export
        if loans:
            df_all = pd.DataFrame(loans)
            csv_all = df_all.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Export All Loans (CSV)",
                csv_all,
                "all_loans_report.csv",
                "text/csv"
            )
