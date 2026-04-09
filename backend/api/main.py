from fastapi import FastAPI
from pydantic import BaseModel
from backend.agents.orchestrator_agent import run_agents
from backend.db.queries import get_user_by_pan, save_loan 

app = FastAPI()

class LoanRequest(BaseModel):
    income:       float
    loan_amount:  float
    credit_score: int
    emi:          float
    dti:          float = 0.0
    user_id:      int   = None      
    loan_tenure:  str   = "12 months" 

class LoanSaveRequest(BaseModel):
    user_id:        int
    loan_amount:    float
    tenure_months:  int
    status:         str   # "approved" ya "rejected"

@app.get("/")
def home():
    return {"message": "Loan Agentic AI running"}

@app.post("/loan/apply")
def apply_loan(data: LoanRequest):
    tenure_months  = int(data.loan_tenure.split()[0])   # "12 months" -> 12
    new_emi        = data.loan_amount / tenure_months if tenure_months > 0 else 0
    total_emi      = data.emi + new_emi                 # existing + naya
    dti            = total_emi / data.income if data.income > 0 else 0

    payload = data.model_dump()
    payload["dti"]           = round(dti, 4)
    payload["tenure_months"] = tenure_months   
    payload["existing_emi"]  = data.emi        

    return run_agents(payload)

@app.post("/loan/save")
def save_loan_record(data: LoanSaveRequest):
    try:
        save_loan(
            user_id=data.user_id,
            loan_amount=int(data.loan_amount),
            tenure_months=data.tenure_months,
            status=data.status
        )
        return {"message": f"Loan record saved with status: {data.status}"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/user/{pan}")
def get_user(pan: str):
    user = get_user_by_pan(pan)

    if user:
        return {"data": user}
    else:
        return {"error": "User not found"}