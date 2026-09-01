from .connection import get_connection


def get_customer_by_pan(pan):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE pan = %s", (pan.strip().upper(),))
    customer = cursor.fetchone()
    cursor.close()
    conn.close()
    return customer


def insert_customer(name, pan, aadhaar_masked, dob, mobile, email, monthly_income, employment_type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO customers
            (name, pan, aadhaar_masked, dob, mobile, email, monthly_income, employment_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (name, pan.upper(), aadhaar_masked, dob, mobile, email, monthly_income, employment_type),
    )
    customer_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return customer_id


def save_application(customer_id, decision, reason, kyc_status, document_status,
                     compliance_status, risk_level, risk_score):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO onboarding_applications
            (customer_id, decision, reason, kyc_status, document_status,
             compliance_status, risk_level, risk_score)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (customer_id, decision, reason, kyc_status, document_status,
         compliance_status, risk_level, risk_score),
    )
    application_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return application_id


def save_document(application_id, document_type, extracted_text, is_valid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO documents (application_id, document_type, extracted_text, is_valid)
        VALUES (%s, %s, %s, %s)
        """,
        (application_id, document_type, extracted_text, is_valid),
    )
    conn.commit()
    cursor.close()
    conn.close()


def list_customers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, name, pan, dob, mobile, email, monthly_income, employment_type, created_at
        FROM customers
        ORDER BY id DESC
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def list_applications():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT a.id, c.name, c.pan, a.decision, a.risk_level, a.risk_score,
               a.kyc_status, a.document_status, a.compliance_status, a.created_at
        FROM onboarding_applications a
        JOIN customers c ON a.customer_id = c.id
        ORDER BY a.id DESC
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
