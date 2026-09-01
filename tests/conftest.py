"""Shared fixtures for OnBoardIQ tests."""

import pytest


@pytest.fixture
def valid_applicant():
    """A well-formed applicant payload that should pass basic validation."""
    return {
        "name": "Rahul Sharma",
        "pan": "ABCDE1234F",
        "aadhaar": "123456789012",
        "mobile": "9876543210",
        "age": 30,
        "monthly_income": 60000,
        "employment_type": "Salaried",
        "file_bytes": None,
    }


@pytest.fixture
def mock_pan_card_text():
    """Fake OCR output from a valid PAN card image."""
    return (
        "INCOME TAX DEPARTMENT\n"
        "GOVT. OF INDIA\n"
        "Permanent Account Number Card\n"
        "Name: RAHUL SHARMA\n"
        "Father Name: SURESH SHARMA\n"
        "Date of Birth: 15/03/1990\n"
        "ABCDE1234F\n"
    )


@pytest.fixture
def sanctions_hit_response():
    """Fake OpenSanctions API response indicating a match."""
    return {
        "results": [
            {
                "caption": "Vladimir Putin",
                "score": 0.95,
                "properties": {"topics": ["role.pep", "sanction"]},
            }
        ]
    }


@pytest.fixture
def sanctions_clear_response():
    """Fake OpenSanctions API response with no matches."""
    return {"results": []}
