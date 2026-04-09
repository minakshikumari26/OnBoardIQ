from backend.tools.risk_tool import predict_risk

def evaluate_credit(data):

    risk = predict_risk(
        data["income"],
        data["loan_amount"],
        data["credit_score"],
        data.get("dti", 0)    
    )
 
    return {
        "risk_result": risk,
        "risk_level": risk.get("risk_level", "High Risk")
    }