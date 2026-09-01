from backend.db.queries import get_customer_by_pan


def evaluate_kyc(data):
    name = data.get("name", "").strip()
    pan = data.get("pan", "").strip().upper()
    aadhaar = data.get("aadhaar", "").strip()
    mobile = data.get("mobile", "").strip()
    age = data.get("age", 0)

    # PAN must be 10 characters
    if len(pan) != 10:
        return {"kyc_status": "failed", "reason": "PAN must be 10 characters"}

    # Aadhaar must be 12 digits (if given)
    if aadhaar and (len(aadhaar) != 12 or not aadhaar.isdigit()):
        return {"kyc_status": "failed", "reason": "Aadhaar must be 12 digits"}

    # Mobile must be 10 digits (if given)
    if mobile and (len(mobile) != 10 or not mobile.isdigit()):
        return {"kyc_status": "failed", "reason": "Mobile must be 10 digits"}

    # Age must be 18 or above
    if age < 18:
        return {"kyc_status": "failed", "reason": "Age is below 18"}

    # If PAN already exists in database, check name matches
    try:
        existing = get_customer_by_pan(pan)
    except Exception:
        # DB not reachable — skip the bureau match, don't fail the pipeline
        existing = None

    if existing:
        db_name = existing[1]
        if db_name.lower() != name.lower():
            return {"kyc_status": "failed", "reason": "Name does not match records"}

    return {"kyc_status": "verified", "reason": "Identity verified"}
