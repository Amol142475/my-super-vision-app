# 👁️ Super Vision — Python Edition

Glide অ্যাপের পূর্ণ Python/Streamlit মাইগ্রেশন।

## ইনস্টলেশন

```bash
pip install -r requirements.txt
streamlit run super_vision_app.py
```

## ফিচার সমূহ

| পেজ | বিবরণ |
|-----|-------|
| 🏠 Dashboard | সারসংক্ষেপ — CO সংখ্যা, মোট ভিজিট, পেন্ডিং, মোট পরিমাণ |
| 👤 CO Profiles | Credit Officer যোগ/দেখা/মুছা, গ্রিড ভিউ |
| ➕ Add Loan Visit | সম্পূর্ণ ফর্ম — Client, Loan, Status, Grantor, Family, Loan Analysis |
| 📋 Visited Loan List | সার্চ, ফিল্টার, স্ট্যাটাস আপডেট, AI Risk Analysis |
| 📊 Loan Visit Report | CO-ওয়াইজ রিপোর্ট, Branch Total, CSV Export |

## ডেটা সংরক্ষণ

`sv_data/` ফোল্ডারে JSON ফাইলে সংরক্ষিত হয়।
- `officers.json` — Credit Officer তালিকা  
- `loans.json` — সব loan visit রেকর্ড

## AI Risk Analysis

| স্কোর | সিদ্ধান্ত |
|-------|-----------|
| ≤ 30 | ✅ Low Risk |
| 31–55 | ⚠️ Medium Risk |
| > 55 | ❌ High Risk |
