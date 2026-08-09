import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Admin Dashboard", page_icon="🏛️", layout="wide")

st.title("🏛️ Admin Dashboard")

st.caption("Powered by NExtGEn-X")
st.divider()

# ── Fetch data from API ───────────────────────────────────────────────────────
@st.cache_data(ttl=30)  
def fetch_users():
    try:
        resp = requests.get("http://127.0.0.1:8000/admin/users", timeout=10)
        resp.raise_for_status()
        return resp.json().get("data", [])
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        return []

@st.cache_data(ttl=30)
def fetch_loans():
    try:
        resp = requests.get("http://127.0.0.1:8000/admin/loans", timeout=10)
        resp.raise_for_status()
        return resp.json().get("data", [])
    except Exception as e:
        st.error(f"Error fetching loans: {e}")
        return []

users = fetch_users()
loans = fetch_loans()

# ── Stats Row ─────────────────────────────────────────────────────────────────
if loans:
    df_loans = pd.DataFrame(loans, columns=["ID","User ID","Name","Loan Amount","Tenure","Status","Date"])
    total      = len(df_loans)
    approved   = len(df_loans[df_loans["Status"] == "approved"])
    rejected   = len(df_loans[df_loans["Status"] == "rejected"])
    approval_pct = round((approved / total) * 100, 1) if total > 0 else 0

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Applications", total)
    s2.metric("Approved",  approved,  f"{approval_pct}%")
    s3.metric("Rejected",  rejected)
    s4.metric("Total Users", len(users))

    st.divider()

# ── Users Table ───────────────────────────────────────────────────────────────
st.subheader("👥 Registered Users")
if users:
    df_users = pd.DataFrame(users, columns=["ID","Name","PAN","CIBIL Score","Monthly Income (₹)","Existing EMI (₹)","Created At"])
    st.dataframe(df_users, use_container_width=True, hide_index=True)
else:
    st.info("No users found.")

st.divider()

# ── Loans Table ───────────────────────────────────────────────────────────────
st.subheader("📋 Loan Applications")
if loans:
    # Status color coding
    def color_status(val):
        if val == "approved":
            return "background-color: #d4edda; color: #155724"
        elif val == "rejected":
            return "background-color: #f8d7da; color: #721c24"
        return ""

    styled = df_loans.style.applymap(color_status, subset=["Status"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # Filter by status
    st.subheader("🔍 Filter")
    status_filter = st.selectbox("Filter by Status", ["All", "approved", "rejected"])
    if status_filter != "All":
        filtered = df_loans[df_loans["Status"] == status_filter]
        st.dataframe(filtered, use_container_width=True, hide_index=True)
else:
    st.info("No loan applications found.")

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()