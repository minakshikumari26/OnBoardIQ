"""Tests for backend/agents/kyc_agent.py"""

from backend.agents import kyc_agent


def test_valid_applicant_passes(valid_applicant, mocker):
    mocker.patch.object(kyc_agent, "get_customer_by_pan", return_value=None)
    result = kyc_agent.evaluate_kyc(valid_applicant)
    assert result["kyc_status"] == "verified"


def test_short_pan_fails(valid_applicant, mocker):
    mocker.patch.object(kyc_agent, "get_customer_by_pan", return_value=None)
    valid_applicant["pan"] = "SHORT"
    result = kyc_agent.evaluate_kyc(valid_applicant)
    assert result["kyc_status"] == "failed"
    assert "PAN" in result["reason"]


def test_bad_aadhaar_fails(valid_applicant, mocker):
    mocker.patch.object(kyc_agent, "get_customer_by_pan", return_value=None)
    valid_applicant["aadhaar"] = "12345"   # too short
    result = kyc_agent.evaluate_kyc(valid_applicant)
    assert result["kyc_status"] == "failed"
    assert "Aadhaar" in result["reason"]


def test_non_digit_mobile_fails(valid_applicant, mocker):
    mocker.patch.object(kyc_agent, "get_customer_by_pan", return_value=None)
    valid_applicant["mobile"] = "98abc43210"
    result = kyc_agent.evaluate_kyc(valid_applicant)
    assert result["kyc_status"] == "failed"


def test_underage_fails(valid_applicant, mocker):
    mocker.patch.object(kyc_agent, "get_customer_by_pan", return_value=None)
    valid_applicant["age"] = 16
    result = kyc_agent.evaluate_kyc(valid_applicant)
    assert result["kyc_status"] == "failed"
    assert "18" in result["reason"]


def test_name_mismatch_against_bureau_fails(valid_applicant, mocker):
    # Simulate a DB record where the name doesn't match
    fake_row = (1, "Different Name", "ABCDE1234F", None, None, None, None, None, None)
    mocker.patch.object(kyc_agent, "get_customer_by_pan", return_value=fake_row)
    result = kyc_agent.evaluate_kyc(valid_applicant)
    assert result["kyc_status"] == "failed"
    assert "match" in result["reason"].lower()


def test_db_down_doesnt_crash(valid_applicant, mocker):
    # If the DB lookup raises, KYC should still complete gracefully
    mocker.patch.object(kyc_agent, "get_customer_by_pan", side_effect=Exception("boom"))
    result = kyc_agent.evaluate_kyc(valid_applicant)
    assert result["kyc_status"] == "verified"


def test_empty_aadhaar_is_optional(valid_applicant, mocker):
    mocker.patch.object(kyc_agent, "get_customer_by_pan", return_value=None)
    valid_applicant["aadhaar"] = ""
    result = kyc_agent.evaluate_kyc(valid_applicant)
    assert result["kyc_status"] == "verified"
