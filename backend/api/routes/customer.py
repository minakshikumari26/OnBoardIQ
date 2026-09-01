from fastapi import APIRouter
from pydantic import BaseModel

from backend.db.queries import get_customer_by_pan
from backend.services.onboarding_service import register_new_customer

router = APIRouter(prefix="/customer", tags=["customer"])


class CustomerRegister(BaseModel):
    name:            str
    pan:             str
    aadhaar:         str = ""
    dob:             str        # "YYYY-MM-DD"
    mobile:          str = ""
    email:           str = ""
    monthly_income:  int = 0
    employment_type: str = ""


@router.get("/{pan}")
def get_customer(pan: str):
    customer = get_customer_by_pan(pan)
    if customer:
        return {"data": customer}
    return {"error": "Customer not found"}


@router.post("/register")
def register_customer(data: CustomerRegister):
    existing = get_customer_by_pan(data.pan)
    if existing:
        return {"error": "Customer with this PAN already exists"}

    try:
        customer_id = register_new_customer(
            name=data.name,
            pan=data.pan,
            aadhaar=data.aadhaar,
            dob=data.dob,
            mobile=data.mobile,
            email=data.email,
            monthly_income=data.monthly_income,
            employment_type=data.employment_type,
        )
        return {"success": True, "customer_id": customer_id}
    except ValueError:
        return {"error": "DOB must be in YYYY-MM-DD format"}
    except Exception as e:
        return {"error": str(e)}
