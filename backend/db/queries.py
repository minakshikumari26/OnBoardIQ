from .connection import get_connection

def get_user_by_pan(pan):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE pan=%s", (pan,))
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