from backend.agents.credit_agent     import evaluate_credit
from backend.agents.fraud_agent      import check_fraud
from backend.agents.compliance_agent import check_compliance
from backend.agents.decision_agent   import make_decision
from backend.db.queries              import check_active_loan  
import time

def run_agents(data):

    start = time.time()
    print("PAYLOAD:", data)

    user_id     = data.get("user_id")
    active_loan = check_active_loan(user_id) if user_id else False

    data["active_loan"]   = active_loan
    data["tenure_months"] = int(data.get("loan_tenure", "12 months").split()[0])

    credit_result     = evaluate_credit(data)
    fraud_result      = check_fraud(data)
    compliance_result = check_compliance(data)

    decision_result   = make_decision(
        credit_result["risk_result"],
        fraud_result["fraud_flag"],
        compliance_result["compliance"]
    )

    real_shap_factors = credit_result["risk_result"].get("top_factors", [])

    return {
        "credit":            credit_result,
        "fraud":             fraud_result,
        "compliance":        compliance_result,
        "decision":          decision_result,
        "active_loan":       active_loan,
        "compliance_reason": compliance_result.get("reason", ""),

        "pd_score":                credit_result["risk_result"].get("pd_score", 0.0),
        "risk_level":              credit_result["risk_result"].get("risk_level", "Unknown"),
        "processing_time_seconds": round(time.time() - start, 2),
        "escalated":               decision_result["decision"] == "Conditional Approval",
        "top_factors":             real_shap_factors
    }