import streamlit as st
import requests

st.set_page_config(page_title="AI Loan Approval", page_icon="🏦", layout="wide")

st.title("🏦 AI Loan Approval System")
st.caption("Powered by NExtGEn-X")
st.divider()

# ── Session State Init ────────────────────────────────────────────────────────
if "pan_verified" not in st.session_state:
    st.session_state.pan_verified = False

if "cibil_score" not in st.session_state:
    st.session_state.cibil_score = 300

if "auto_income" not in st.session_state:
    st.session_state.auto_income = 0

if "existing_emi" not in st.session_state:
    st.session_state.existing_emi = 0

if "verified_name" not in st.session_state:
    st.session_state.verified_name = ""


if "has_active_loan" not in st.session_state:
    st.session_state.has_active_loan = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None


col_form, col_result = st.columns(2, gap="large")

# ── Form ──────────────────────────────────────────────────────────────────────
with col_form:
    st.subheader("📋 Applicant Info")
    applicant_name = st.text_input("Full Name", placeholder="e.g. Rahul Sharma")
    pan_number     = st.text_input("PAN Number", placeholder="e.g. ABCDE1234F")

    if st.button("Verify PAN", use_container_width=True):
        if pan_number.strip():
            with st.spinner("Fetching user details…"):
                try:
                    resp = requests.get(f"http://127.0.0.1:8000/user/{pan_number}", timeout=10)
                    resp.raise_for_status()
                    user_data = resp.json()

                    if "data" in user_data:
                        data_1 = user_data["data"]

                        
                        db_id        = data_1[0]   
                        db_name      = data_1[1]
                        cibil_score  = data_1[3]
                        income       = data_1[4]
                        existing_emi = data_1[5]   

                        
                        if applicant_name.strip().lower() == db_name.strip().lower():

                            st.session_state.pan_verified  = True
                            st.session_state.cibil_score   = int(cibil_score)
                            st.session_state.auto_income   = int(income)
                            st.session_state.existing_emi  = int(existing_emi)
                            st.session_state.verified_name = db_name
                            st.session_state.user_id       = db_id  # CHANGE: save user_id

                            
                            if int(existing_emi) > 0:
                                st.session_state.has_active_loan = True
                                st.warning(
                                    f"⚠️ PAN Verified — {db_name}, "
                                    f"but you already have an active loan "
                                    f"(EMI: ₹{existing_emi}/mo). "
                                    f"New loan application is not allowed."
                                )
                            else:
                                st.session_state.has_active_loan = False
                                st.success(f"✅ PAN Verified! Welcome, {db_name}")

                        else:
                            st.session_state.pan_verified    = False
                            st.session_state.has_active_loan = False
                            st.error("❌ Name does not match PAN records. Please check and retry.")

                    else:
                        st.session_state.pan_verified    = False
                        st.session_state.has_active_loan = False
                        st.error("User not found for this PAN.")

                except requests.exceptions.RequestException as e:
                    st.session_state.pan_verified = False
                    st.error(f"Error fetching user details: {e}")
        else:
            st.warning("Please enter a PAN number to verify.")

    if not st.session_state.pan_verified:
        st.caption("⚠️ PAN verification required before loan evaluation.")

    st.subheader("💰 Financial Details")
    c1, c2 = st.columns(2)

    with c1:
        income = st.number_input(
            "Monthly Income (₹)",
            min_value=0,
            step=1000,
            value=st.session_state.auto_income,
            help="Auto-filled from PAN records. You may edit if needed."
        )
        loan_amount = st.number_input("Loan Amount (₹)", min_value=0, step=10_000)

    with c2:
        credit_score = st.number_input(
            "CIBIL Score",
            min_value=300,
            max_value=900,
            value=st.session_state.cibil_score,
            disabled=True,   
            help="Fetched from credit bureau via PAN. Cannot be edited manually."
        )
        
        existing_emi = st.number_input(
            "Existing EMI (₹/mo)",
            min_value=0,
            step=500,
            value=st.session_state.existing_emi,
            disabled=True,   
            help="Auto-filled from records. Cannot be edited."
        )

    st.subheader("📄 Loan Details")
    c3, c4 = st.columns(2)
    with c3:
        loan_tenure  = st.selectbox("Tenure", ["12 months","24 months","36 months","60 months","84 months"])
        employment   = st.selectbox("Employment", ["Salaried","Self-Employed","Business Owner","Freelancer"])
    with c4:
        loan_purpose     = st.selectbox("Purpose", ["Home Loan","Personal Loan","Auto Loan","Education Loan","Business Loan"])
        employment_years = st.number_input("Years Employed", min_value=0, max_value=40, value=3)

    dti = 0.0
    tenure_months_live = int(loan_tenure.split()[0])   # "12 months" -> 12
    new_emi_estimate   = round(loan_amount / tenure_months_live, 0) if tenure_months_live > 0 else 0
    total_emi_live     = st.session_state.existing_emi + new_emi_estimate

    if income > 0:
        dti   = round((total_emi_live / income) * 100, 1)
        label = "✅ Low Risk" if dti < 30 else "⚠️ Medium Risk" if dti < 50 else "❌ High Risk"
        # CHANGE: Breakdown dikhao — user ko pata chale DTI kaise calculate hua
        st.metric("Live DTI", f"{dti}%", label)
        st.caption(
            f"Existing EMI ₹{int(st.session_state.existing_emi)} "
            f"+ New EMI ~₹{int(new_emi_estimate)} "
            f"= Total ₹{int(total_emi_live)} / Income ₹{int(income)}"
        )

    st.divider()

    can_submit = (
        st.session_state.pan_verified and
        income > 0 and
        loan_amount > 0 and
        applicant_name.strip()
    )

    if not can_submit:
        if not st.session_state.pan_verified:
            st.warning("🔒 Please verify your PAN before submitting.")
        else:
            st.warning("Fill all fields to enable evaluation.")

    submit = st.button(
        "🚀 Evaluate Loan Application",
        disabled=not can_submit,
        use_container_width=True
    )


# ── Results ───────────────────────────────────────────────────────────────────
with col_result:
    st.subheader("📊 AI Evaluation Result")

    if st.session_state.pan_verified and st.session_state.has_active_loan:
        st.warning(
            f"⚠️ Note: You have an existing loan (EMI: ₹{st.session_state.existing_emi}/mo). "
            f"Eligibility will be assessed based on your total EMI burden."
        )

    elif submit and can_submit:
        payload = {
            "income":           income,
            "loan_amount":      loan_amount,
            "credit_score":     st.session_state.cibil_score,
            "emi":              st.session_state.existing_emi,
            "loan_tenure":      loan_tenure,
            "employment_type":  employment,
            "loan_purpose":     loan_purpose,
            "employment_years": employment_years,
            "user_id":          st.session_state.user_id,
            "existing_emi":     st.session_state.existing_emi,
        }

        with st.spinner("AI agents evaluating your application…"):
            try:
                resp = requests.post("http://127.0.0.1:8000/loan/apply", json=payload, timeout=30)
                resp.raise_for_status()
                result = resp.json()
                api_ok = True
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach API. Is FastAPI running on port 8000?")
                api_ok = False
            except requests.exceptions.Timeout:
                st.error("Request timed out. Try again.")
                api_ok = False
            except Exception as e:
                pass    
            compliance_reason = result.get("compliance_reason", "")
            active_loan_flag   = result.get("active_loan", False)
        if api_ok:
            decision   = result.get("decision", {})
            verdict    = decision.get("decision", "UNKNOWN").upper()
            reason     = decision.get("reason", "No reason provided.")
            pd_score   = result.get("pd_score", 0.0)
            risk_level = result.get("risk_level", "UNKNOWN")
            escalated  = result.get("escalated", False)
            factors    = result.get("top_factors", [])
            proc_time  = result.get("processing_time_seconds", 0)

            # Decision banner
            if verdict == "APPROVED":
                st.success("✅ APPROVED — Congratulations! Your loan has been approved.")

                tenure_num = int(loan_tenure.split()[0])
                save_payload = {
                    "user_id":    st.session_state.user_id,
                    "loan_amount": loan_amount,
                    "tenure_months": tenure_num,
                    "status": "approved"
                }
                try:
                    save_resp = requests.post("http://127.0.0.1:8000/loan/save", json=save_payload, timeout=10)
                    if save_resp.status_code == 200:
                        st.caption("📁 Loan record saved to database.")
                    else:
                        st.caption("⚠️ Approved but could not save record. Contact support.")
                except Exception:
                    st.caption("⚠️ Could not save loan record to DB.")

            elif verdict == "REJECTED":
                if active_loan_flag and compliance_reason:
                    st.error(f"❌ REJECTED — {compliance_reason}")
                else:
                    st.error("❌ REJECTED — Application did not meet the required criteria.")

                tenure_num = int(loan_tenure.split()[0])
                save_payload = {
                    "user_id":       st.session_state.user_id,
                    "loan_amount":   loan_amount,
                    "tenure_months": tenure_num,
                    "status":        "rejected"
                }
                try:
                    requests.post("http://127.0.0.1:8000/loan/save", json=save_payload, timeout=10)
                except Exception:
                    pass  

            elif verdict == "CONDITIONAL":
                st.warning("⚠️ CONDITIONAL APPROVAL — Approved with conditions. See reasoning below.")
            elif verdict == "ESCALATED":
                st.info("👤 ESCALATED — Referred to a credit officer for manual review.")
            else:
                st.info(f"Decision: {verdict}")

            m1, m2, m3 = st.columns(3)
            m1.metric("PD Score",     f"{pd_score:.2f}", help="Probability of Default")
            m2.metric("Risk Level",   risk_level)
            m3.metric("Processed In", f"{proc_time}s")

            st.subheader("🧠 AI Reasoning")
            st.info(reason)

            # SHAP factors
            if factors:
                st.subheader("📉 Top Risk Factors (SHAP)")
                for f in factors:
                    fname  = f.get("factor", "").replace("_", " ").title()
                    impact = f.get("impact", 0)
                    sign   = "+" if impact > 0 else ""
                    bar_w  = min(abs(impact) * 400, 100) / 100
                    st.progress(bar_w, text=f"{fname}  —  {sign}{impact:.2f}")

            if escalated:
                st.warning("👤 Case escalated. A credit officer will respond within 24 business hours.")

    else:
        st.info("Fill in the form and click **Evaluate Loan Application** to see results.")