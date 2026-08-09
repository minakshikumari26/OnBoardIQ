from fastapi import FastAPI
from pydantic import BaseModel
from backend.agents.orchestrator_agent import run_agents
from backend.db.queries import get_user_by_pan, save_loan, insert_new_user 
from backend.db.connection import get_connection

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
    
class RegisterRequest(BaseModel):
    name:         str
    pan:          str
    cibil:        int  
    salary:       int 
    existing_emi: int

@app.get("/")
def home():
    return {"message": "Loan Agentic AI running"}

@app.post("/loan/apply")
def apply_loan(data: LoanRequest):
    tenure_months  = int(data.loan_tenure.split()[0])   # "12 months" -> 12
    new_emi        = data.loan_amount / tenure_months if tenure_months > 0 else 0
    total_emi      = data.emi + new_emi                 # existing + new
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
    
@app.post("/user/register")
def register_user(data: RegisterRequest):
    existing = get_user_by_pan(data.pan)
    if existing:
        return {"error": "User with this PAN already exists."}
    
    try:
        user_id = insert_new_user(
            name=data.name,
            pan=data.pan,
            cibil=data.cibil,
            monthly_income=data.salary,
            existing_emi=data.existing_emi
        )
        return {"success": True, "user_id": user_id, "message": "User registered successfully!"}
    except Exception as e:
        return {"error": str(e)}
    
      
@app.get("/admin/users")
def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, pan, cibil_score, monthly_income, existing_emi, created_at FROM users ORDER BY id")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"data": [list(u) for u in users]}

@app.get("/admin/loans")
def get_all_loans():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.id, l.user_id, u.name, l.loan_amount, 
               l.tenure_months, l.status, l.created_at
        FROM loans l
        JOIN users u ON l.user_id = u.id
        ORDER BY l.id DESC
    """)
    loans = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"data": [list(l) for l in loans]}