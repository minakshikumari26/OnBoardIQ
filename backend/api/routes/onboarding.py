from fastapi import APIRouter, UploadFile, File, Form

from backend.services.onboarding_service import process_onboarding

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("/apply")
async def onboarding_apply(
    name:            str = Form(...),
    pan:             str = Form(...),
    aadhaar:         str = Form(""),
    dob:             str = Form(...),
    mobile:          str = Form(""),
    email:           str = Form(""),
    monthly_income:  int = Form(0),
    employment_type: str = Form(""),
    document_type:   str = Form("pan"),
    document:        UploadFile = File(...),
):
    file_bytes = await document.read()

    try:
        return process_onboarding(
            name=name,
            pan=pan,
            aadhaar=aadhaar,
            dob=dob,
            mobile=mobile,
            email=email,
            monthly_income=monthly_income,
            employment_type=employment_type,
            document_type=document_type,
            file_bytes=file_bytes,
        )
    except ValueError:
        return {"error": "DOB must be in YYYY-MM-DD format"}
