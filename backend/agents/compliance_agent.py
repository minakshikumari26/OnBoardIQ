def check_compliance(data):

    credit_score  = data["credit_score"]
    dti           = data.get("dti", 0)
    income        = data.get("income", 0)
    loan_amount   = data.get("loan_amount", 0)
    tenure_months = data.get("tenure_months", 12)   
    existing_emi  = data.get("existing_emi", 0)     
    active_loan   = data.get("active_loan", False)  

    if dti > 1:
        dti = dti / 100

    if credit_score == 0:
        pass
    elif credit_score < 600:
        return {
            "compliance": False,
            "reason": "Credit score below 600 — RBI minimum requirement"
        }

    if dti > 0.6:
        return {
            "compliance": False,
            "reason": "Debt-to-income ratio exceeds 60%"
        }

    if active_loan and income > 0:

        estimated_new_emi = loan_amount / tenure_months if tenure_months > 0 else loan_amount

        total_emi = existing_emi + estimated_new_emi
        emi_ratio = total_emi / income   

        if emi_ratio > 0.5:
            return {
                "compliance": False,
                "reason": (
                    f"Existing loan detected. Total EMI burden would be "
                    f"₹{int(total_emi)}/mo ({round(emi_ratio*100)}% of income). "
                    f"Exceeds 50% affordability limit."
                )
            }

        elif emi_ratio > 0.35:
            return {
                "compliance": True,
                "reason": (
                    f"Existing loan detected. EMI ratio {round(emi_ratio*100)}% — "
                    f"borderline affordability. Conditional approval possible."
                ),
                "emi_ratio": round(emi_ratio, 3),
                "existing_borrower": True
            }

        else:
            return {
                "compliance": True,
                "reason": (
                    f"Existing loan detected but EMI ratio {round(emi_ratio*100)}% "
                    f"is within acceptable limits."
                ),
                "emi_ratio": round(emi_ratio, 3),
                "existing_borrower": True
            }
    return {
        "compliance": True,
        "reason": "Compliance check passed"
    }