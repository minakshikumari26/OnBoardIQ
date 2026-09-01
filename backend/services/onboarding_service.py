"""
Business logic for onboarding.

Routes call these functions. Everything DB-facing and agent-facing happens
here, so route handlers stay thin (parse input, call service, return response).
"""

from datetime import date, datetime

from backend.agents.orchestrator_agent import run_agents
from backend.db.queries import (
    get_customer_by_pan,
    insert_customer,
    save_application,
    save_document,
)


def _parse_dob(dob_str):
    """Parse YYYY-MM-DD and compute current age. Raises ValueError on bad input."""
    dob_date = datetime.strptime(dob_str, "%Y-%m-%d").date()
    today = date.today()
    age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
    return dob_date, age


def _mask_aadhaar(aadhaar):
    """Return XXXX-XXXX-1234 style mask, or empty string if not a full number."""
    if aadhaar and len(aadhaar) == 12:
        return "XXXX-XXXX-" + aadhaar[-4:]
    return ""


def register_new_customer(name, pan, aadhaar, dob, mobile, email,
                          monthly_income, employment_type):
    """Insert a new customer row and return the new customer_id."""
    dob_date, _ = _parse_dob(dob)
    return insert_customer(
        name=name.strip(),
        pan=pan.strip().upper(),
        aadhaar_masked=_mask_aadhaar(aadhaar),
        dob=dob_date,
        mobile=mobile,
        email=email,
        monthly_income=monthly_income,
        employment_type=employment_type,
    )


def process_onboarding(name, pan, aadhaar, dob, mobile, email,
                       monthly_income, employment_type,
                       document_type, file_bytes):
    """Run the full onboarding pipeline and persist the application.

    Returns the orchestrator result with customer_id + application_id added.
    """
    dob_date, age = _parse_dob(dob)

    payload = {
        "name": name,
        "pan": pan.upper(),
        "aadhaar": aadhaar,
        "mobile": mobile,
        "email": email,
        "age": age,
        "monthly_income": monthly_income,
        "employment_type": employment_type,
        "file_bytes": file_bytes,
    }
    result = run_agents(payload)

    # Save customer if new
    existing = get_customer_by_pan(pan)
    if existing:
        customer_id = existing[0]
    else:
        customer_id = insert_customer(
            name=name.strip(),
            pan=pan.strip().upper(),
            aadhaar_masked=_mask_aadhaar(aadhaar),
            dob=dob_date,
            mobile=mobile,
            email=email,
            monthly_income=monthly_income,
            employment_type=employment_type,
        )

    application_id = save_application(
        customer_id=customer_id,
        decision=result["decision"],
        reason=result["reason"],
        kyc_status=result["kyc"]["kyc_status"],
        document_status=result["document"]["document_status"],
        compliance_status=result["compliance"]["compliance_status"],
        risk_level=result["risk"]["risk_level"],
        risk_score=result["risk"]["risk_score"],
    )

    save_document(
        application_id=application_id,
        document_type=document_type,
        extracted_text=result["document"].get("extracted_text", ""),
        is_valid=(result["document"]["document_status"] == "valid"),
    )

    result["customer_id"] = customer_id
    result["application_id"] = application_id
    return result
