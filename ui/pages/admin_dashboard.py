import os

import streamlit as st
import requests
import pandas as pd

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Admin Dashboard", page_icon="🏛️", layout="wide")

st.title("🏛️ OnBoardIQ Admin Dashboard")
st.caption("View customers and onboarding applications")
st.divider()


@st.cache_data(ttl=30)
def fetch_customers():
    try:
        resp = requests.get(f"{API_URL}/admin/customers", timeout=10)
        resp.raise_for_status()
        return resp.json().get("data", [])
    except Exception as e:
        st.error(f"Error fetching customers: {e}")
        return []


@st.cache_data(ttl=30)
def fetch_applications():
    try:
        resp = requests.get(f"{API_URL}/admin/applications", timeout=10)
        resp.raise_for_status()
        return resp.json().get("data", [])
    except Exception as e:
        st.error(f"Error fetching applications: {e}")
        return []


customers = fetch_customers()
applications = fetch_applications()

# ── Stats ─────────────────────────────────────────────────────────────────────
if applications:
    df_apps = pd.DataFrame(applications, columns=[
        "ID", "Name", "PAN", "Decision", "Risk Level", "Risk Score",
        "KYC", "Document", "Compliance", "Created At"
    ])

    total = len(df_apps)
    approved = len(df_apps[df_apps["Decision"] == "Approved"])
    rejected = len(df_apps[df_apps["Decision"] == "Rejected"])
    review = len(df_apps[df_apps["Decision"] == "Needs Review"])

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Applications", total)
    s2.metric("Approved", approved)
    s3.metric("Rejected", rejected)
    s4.metric("Needs Review", review)

    st.divider()

# ── Customers ─────────────────────────────────────────────────────────────────
st.subheader("👥 Registered Customers")
if customers:
    df_customers = pd.DataFrame(customers, columns=[
        "ID", "Name", "PAN", "DOB", "Mobile", "Email",
        "Monthly Income", "Employment", "Created At"
    ])
    st.dataframe(df_customers, use_container_width=True, hide_index=True)
else:
    st.info("No customers found.")

st.divider()

# ── Applications ──────────────────────────────────────────────────────────────
st.subheader("📋 Onboarding Applications")
if applications:
    def color_decision(val):
        if val == "Approved":
            return "background-color: #d4edda; color: #155724"
        if val == "Rejected":
            return "background-color: #f8d7da; color: #721c24"
        if val == "Needs Review":
            return "background-color: #fff3cd; color: #856404"
        return ""

    styled = df_apps.style.applymap(color_decision, subset=["Decision"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.subheader("🔍 Filter")
    filter_val = st.selectbox("Filter by Decision", ["All", "Approved", "Rejected", "Needs Review"])
    if filter_val != "All":
        filtered = df_apps[df_apps["Decision"] == filter_val]
        st.dataframe(filtered, use_container_width=True, hide_index=True)
else:
    st.info("No applications found.")

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
