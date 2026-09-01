def assess_risk(data):
    age = data.get("age", 0)
    income = data.get("monthly_income", 0)
    employment = data.get("employment_type", "").lower()
    kyc_status = data.get("kyc_status", "failed")
    document_status = data.get("document_status", "invalid")

    score = 50   # start neutral
    factors = []

    # Age factor
    if 25 <= age <= 55:
        score += 15
        factors.append({"factor": "Age", "impact": 15})
    elif age < 25:
        score -= 10
        factors.append({"factor": "Age", "impact": -10})
    else:
        score -= 5
        factors.append({"factor": "Age", "impact": -5})

    # Income factor
    if income >= 50000:
        score += 20
        factors.append({"factor": "Income", "impact": 20})
    elif income >= 20000:
        score += 10
        factors.append({"factor": "Income", "impact": 10})
    else:
        score -= 15
        factors.append({"factor": "Income", "impact": -15})

    # Employment type
    if employment in ("salaried", "government"):
        score += 15
        factors.append({"factor": "Employment", "impact": 15})
    elif employment == "self-employed":
        score += 5
        factors.append({"factor": "Employment", "impact": 5})
    else:
        score -= 5
        factors.append({"factor": "Employment", "impact": -5})

    # KYC and document quality
    if kyc_status == "verified":
        score += 10
        factors.append({"factor": "KYC", "impact": 10})
    if document_status == "valid":
        score += 10
        factors.append({"factor": "Document", "impact": 10})

    # Keep score in 0-100 range
    if score < 0:
        score = 0
    if score > 100:
        score = 100

    # Convert score to risk level
    if score >= 70:
        risk_level = "Low"
    elif score >= 45:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return {"risk_level": risk_level, "risk_score": score, "factors": factors}
