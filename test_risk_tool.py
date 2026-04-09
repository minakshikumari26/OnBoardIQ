#checking the risk tool.............................................

# from backend.tools.risk_tool import predict_risk

# result = predict_risk(50000, 200000, 720, 35)

# print(result)


# checking the credit agent.............................................

# from backend.agents.credit_agent import evaluate_credit

# result = evaluate_credit({
#     "income": 50000,
#     "loan_amount": 200000,
#     "credit_score": 720,
#     "dti": 35
# })

# print(result)

#checking the fraud agent.............................................
# from backend.agents.fraud_agent import check_fraud

# data = {
#  "income": 50000,
#  "loan_amount": 2000000
# }

# result = check_fraud(data)

# print(result)

#checking the compliance agent.............................................
# from backend.agents.compliance_agent import check_compliance

# data = {"credit_score": 520}
# result = check_compliance(data)

# print(result)

#checking the decision agent.............................................
# from backend.agents.decision_agent import make_decision

# risk = "Low Risk - Loan likely safe"
# fraud = False
# compliance = True

# result = make_decision(risk, fraud, compliance)

# print(result)

#checking the orchestrator agent.............................................
# from backend.agents.orchestrator_agent import run_agents

# data = {
#     "income": 50000,
#     "loan_amount": 200000,
#     "credit_score": 720,
#     "dti": 35
# }

# result = run_agents(data)

# print(result)




from backend.db.queries import get_user_by_pan

pan = "ABCDE1234F"

user = get_user_by_pan(pan)

print(user)