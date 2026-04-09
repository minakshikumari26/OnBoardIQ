def make_decision(risk_result, fraud_flag, compliance):

    if fraud_flag:
        return {"decision": "Rejected",
                "reason": "Fraud risk detected"}

    if not compliance:
        return {"decision": "Rejected",
                "reason": "Compliance requirements not met"}

    risk_level = risk_result.get("risk_level", "High Risk")

    if risk_level == "Low Risk":
        return {"decision": "Approved",
                "reason": "Low credit risk — all checks passed"}

    if risk_level == "Medium Risk":
        return {"decision": "Conditional Approval",
                "reason": "Moderate risk — further verification needed"}

    return {"decision": "Rejected",
            "reason": "High credit risk"}