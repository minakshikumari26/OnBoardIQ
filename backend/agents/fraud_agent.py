def check_fraud(data):

    income      = data["income"]
    loan_amount = data["loan_amount"]
    credit_score= data["credit_score"]

    
    if loan_amount > income * 20:
        return {"fraud_flag": True,
                "reason": "Loan amount unusually high vs income"}

   
    if credit_score < 500 and loan_amount > 500000:
        return {"fraud_flag": True,
                "reason": "High loan with very low credit score"}

    return {"fraud_flag": False, "reason": "No fraud detected"}