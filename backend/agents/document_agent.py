import re
from io import BytesIO

from PIL import Image
import pytesseract


# Regex patterns for structured KYC fields
PAN_PATTERN     = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
DOB_PATTERN     = re.compile(r"\b(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2})\b")
AADHAAR_PATTERN = re.compile(r"\b\d{4} \d{4} \d{4}\b")


def _extract_fields(text):
    """Pull structured KYC fields out of raw OCR text."""
    pan_match     = PAN_PATTERN.search(text)
    dob_match     = DOB_PATTERN.search(text)
    aadhaar_match = AADHAAR_PATTERN.search(text)

    return {
        "pan":     pan_match.group(0) if pan_match else None,
        "dob":     dob_match.group(0) if dob_match else None,
        "aadhaar": aadhaar_match.group(0).replace(" ", "") if aadhaar_match else None,
    }


def verify_document(data):
    file_bytes = data.get("file_bytes")
    name = data.get("name", "").strip()
    applicant_pan = data.get("pan", "").strip().upper()

    if not file_bytes:
        return {
            "document_status":  "invalid",
            "reason":           "No document uploaded",
            "extracted_text":   "",
            "extracted_fields": {},
        }

    # Run OCR on the uploaded image
    try:
        image = Image.open(BytesIO(file_bytes))
        text = pytesseract.image_to_string(image)
    except Exception as e:
        return {
            "document_status":  "unreadable",
            "reason":           f"Could not read document: {e}",
            "extracted_text":   "",
            "extracted_fields": {},
        }

    # Extract structured fields from the OCR text
    extracted = _extract_fields(text)
    text_upper = text.upper()

    # PAN must actually appear in the document
    if not extracted["pan"]:
        return {
            "document_status":  "invalid",
            "reason":           "No PAN number found in document",
            "extracted_text":   text,
            "extracted_fields": extracted,
        }

    # Extracted PAN must match applicant-entered PAN
    if applicant_pan and extracted["pan"] != applicant_pan:
        return {
            "document_status":  "invalid",
            "reason":           f"PAN in document ({extracted['pan']}) does not match applicant PAN ({applicant_pan})",
            "extracted_text":   text,
            "extracted_fields": extracted,
        }

    # Applicant name must appear somewhere in the OCR text
    if name and name.upper() not in text_upper:
        return {
            "document_status":  "invalid",
            "reason":           "Applicant name not found in document",
            "extracted_text":   text,
            "extracted_fields": extracted,
        }

    return {
        "document_status":  "valid",
        "reason":           "Document verified — PAN and name matched",
        "extracted_text":   text,
        "extracted_fields": extracted,
    }
