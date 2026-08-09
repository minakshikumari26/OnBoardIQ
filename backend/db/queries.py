from .connection import get_connection

def get_user_by_pan(pan):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE pan=%s",(pan.strip().upper(),))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def check_active_loan(user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM loans WHERE user_id = %s AND status IN ('approved', 'active')",
        (user_id,)
    )
    loan = cursor.fetchone()
    cursor.close()
    conn.close()
    return loan is not None  

def save_loan(user_id: int, loan_amount: int, tenure_months: int, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO loans (user_id, loan_amount, tenure_months, interest_rate, status)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user_id, loan_amount, tenure_months, 0.0, status)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
def insert_new_user(name: str, pan: str, cibil: int, monthly_income: int, existing_emi: int) -> int:
    """Insert new user, return unka generated user_id"""
    conn = get_connection()  
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (name, pan, cibil_score ,monthly_income , existing_emi)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        (name.strip(), pan.strip().upper(), cibil, monthly_income, existing_emi)
    )
    user_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return user_id