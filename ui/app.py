import os

import streamlit as st
import requests

# When run inside docker-compose, this points at the "backend" service
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="OnBoardIQ", page_icon="🏦", layout="wide")

st.title("🏦 OnBoardIQ — Intelligent Account Onboarding")
st.caption("AI-driven KYC, document verification, and risk profiling")
st.divider()

col_form, col_result = st.columns(2, gap="large")

# ── Form ──────────────────────────────────────────────────────────────────────
with col_form:
    st.subheader("👤 Personal Information")

    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Full Name", placeholder="e.g. Rahul Sharma")
        pan = st.text_input("PAN Number", placeholder="e.g. ABCDE1234F", max_chars=10)
        mobile = st.text_input("Mobile Number", placeholder="10 digits", max_chars=10)
    with c2:
        dob = st.date_input("Date of Birth")
        aadhaar = st.text_input("Aadhaar Number", placeholder="12 digits (optional)", max_chars=12)
        email = st.text_input("Email", placeholder="you@example.com")

    st.subheader("💼 Financial Information")
    c3, c4 = st.columns(2)
    with c3:
        monthly_income = st.number_input("Monthly Income (₹)", min_value=0, step=1000)
    with c4:
        employment_type = st.selectbox(
            "Employment Type",
            ["Salaried", "Self-Employed", "Business Owner", "Government", "Freelancer"]
        )

    st.subheader("📄 Document Upload")
    document_type = st.selectbox("Document Type", ["pan", "aadhaar", "passport"])
    document = st.file_uploader("Upload ID Document (image)", type=["png", "jpg", "jpeg"])

    st.divider()

    can_submit = bool(name and pan and dob and document)
    if not can_submit:
        st.info("Fill name, PAN, DOB and upload a document to enable submit.")

    submit = st.button("🚀 Submit for Onboarding", disabled=not can_submit, use_container_width=True)


# ── Result ────────────────────────────────────────────────────────────────────
with col_result:
    st.subheader("📊 AI Evaluation Result")

    if submit:
        with st.spinner("Running KYC, document, compliance and risk checks…"):
            try:
                files = {"document": (document.name, document.getvalue(), document.type)}
                form_data = {
                    "name": name,
                    "pan": pan.upper(),
                    "aadhaar": aadhaar,
                    "dob": dob.strftime("%Y-%m-%d"),
                    "mobile": mobile,
                    "email": email,
                    "monthly_income": str(monthly_income),
                    "employment_type": employment_type,
                    "document_type": document_type,
                }
                resp = requests.post(f"{API_URL}/onboarding/apply", data=form_data, files=files, timeout=30)
                resp.raise_for_status()
                result = resp.json()
            except Exception as e:
                st.error(f"Error: {e}")
                result = None

        if result:
            decision = result.get("decision", "Unknown")
            reason = result.get("reason", "")

            # Decision banner
            if decision == "Approved":
                st.success(f"✅ APPROVED — {reason}")
            elif decision == "Rejected":
                st.error(f"❌ REJECTED — {reason}")
            elif decision == "Needs Review":
                st.warning(f"⚠️ NEEDS REVIEW — {reason}")
            else:
                st.info(f"Decision: {decision}")

            # Gen AI explanation (from the LangGraph 'explain' node)
            explanation = result.get("explanation", "")
            if explanation:
                st.info(f"💬 **AI Message:** {explanation}")

            # Agent status chips
            st.subheader("🧠 Agent Results")
            kyc = result["kyc"]
            doc = result["document"]
            comp = result["compliance"]
            risk = result["risk"]

            a1, a2, a3, a4 = st.columns(4)
            a1.metric("KYC", kyc["kyc_status"].title())
            a2.metric("Document", doc["document_status"].title())
            a3.metric("Compliance", comp["compliance_status"].title())
            a4.metric("Risk", risk["risk_level"])

            # Reasons for each agent
            with st.expander("📋 Agent Details", expanded=True):
                st.write(f"**KYC:** {kyc.get('reason', '')}")
                st.write(f"**Document:** {doc.get('reason', '')}")
                st.write(f"**Compliance:** {comp.get('reason', '')}")
                if comp.get("matches"):
                    st.write("Sanctions matches:")
                    for m in comp["matches"]:
                        st.write(f"- {m['name']} (score {m['score']})")
                st.write(f"**Risk score:** {risk['risk_score']} / 100")

            # Structured fields extracted from the document via regex
            extracted_fields = doc.get("extracted_fields") or {}
            if any(extracted_fields.values()):
                st.subheader("🔍 Extracted Fields (from OCR)")
                fc1, fc2, fc3 = st.columns(3)
                fc1.metric("PAN",     extracted_fields.get("pan")     or "—")
                fc2.metric("DOB",     extracted_fields.get("dob")     or "—")
                fc3.metric("Aadhaar", extracted_fields.get("aadhaar") or "—")

            # Raw OCR text preview
            extracted_text = doc.get("extracted_text", "")
            if extracted_text:
                with st.expander("📄 Raw OCR Text"):
                    st.text(extracted_text)

            # Risk factors
            if risk.get("factors"):
                st.subheader("📉 Risk Factors")
                for f in risk["factors"]:
                    impact = f["impact"]
                    sign = "+" if impact > 0 else ""
                    bar = min(abs(impact) * 5, 100) / 100
                    st.progress(bar, text=f"{f['factor']} — {sign}{impact}")

            st.caption(f"Processed in {result.get('processing_time_seconds', 0)}s")
    else:
        st.info("Fill the form and click **Submit for Onboarding** to see results.")
