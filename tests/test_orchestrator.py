"""Integration tests for the LangGraph orchestrator.

We mock:
- the DB lookup in kyc_agent (via kyc_agent.get_customer_by_pan)
- the Tesseract call in document_agent
- the requests.get call in compliance_agent
- the LLM call in the explain node (implicitly — no key set = no call)

That way the graph exercises every real node except the external services.
"""

from unittest.mock import MagicMock

from backend.agents import kyc_agent, document_agent, compliance_agent
from backend.agents.orchestrator_agent import run_agents


def _mock_all_externals(mocker, ocr_text, sanctions_response):
    """Set up mocks for DB + Tesseract + OpenSanctions."""
    mocker.patch.object(kyc_agent, "get_customer_by_pan", return_value=None)
    mocker.patch.object(document_agent, "Image")
    mocker.patch.object(document_agent.pytesseract, "image_to_string",
                        return_value=ocr_text)
    fake_resp = MagicMock()
    fake_resp.json.return_value = sanctions_response
    mocker.patch.object(compliance_agent.requests, "get", return_value=fake_resp)


def test_full_happy_path(mocker, valid_applicant, mock_pan_card_text,
                        sanctions_clear_response):
    _mock_all_externals(mocker, mock_pan_card_text, sanctions_clear_response)
    valid_applicant["file_bytes"] = b"fake image"

    result = run_agents(valid_applicant)

    assert result["decision"] == "Approved"
    assert result["kyc"]["kyc_status"] == "verified"
    assert result["document"]["document_status"] == "valid"
    assert result["compliance"]["compliance_status"] == "clear"
    assert result["risk"]["risk_level"] == "Low"


def test_short_circuit_on_kyc_failure(mocker, valid_applicant):
    """Bad PAN → KYC fails → Doc/Compliance/Risk are all skipped."""
    mocker.patch.object(kyc_agent, "get_customer_by_pan", return_value=None)
    valid_applicant["pan"] = "BADPAN"

    result = run_agents(valid_applicant)

    assert result["decision"] == "Rejected"
    assert result["kyc"]["kyc_status"] == "failed"
    # Short-circuited nodes should return the "skipped" placeholder
    assert result["document"]["document_status"] == "skipped"
    assert result["compliance"]["compliance_status"] == "skipped"
    assert result["risk"]["risk_level"] == "skipped"


def test_short_circuit_on_document_failure(mocker, valid_applicant):
    """Missing file → Document invalid → Compliance and Risk are skipped."""
    mocker.patch.object(kyc_agent, "get_customer_by_pan", return_value=None)
    valid_applicant["file_bytes"] = None

    result = run_agents(valid_applicant)

    assert result["decision"] == "Rejected"
    assert result["kyc"]["kyc_status"] == "verified"
    assert result["document"]["document_status"] == "invalid"
    assert result["compliance"]["compliance_status"] == "skipped"
    assert result["risk"]["risk_level"] == "skipped"


def test_short_circuit_on_sanctions_hit(mocker, valid_applicant,
                                        mock_pan_card_text,
                                        sanctions_hit_response):
    """Sanctions hit → Compliance flagged → Risk is skipped."""
    _mock_all_externals(mocker, mock_pan_card_text, sanctions_hit_response)
    valid_applicant["file_bytes"] = b"fake image"

    result = run_agents(valid_applicant)

    assert result["decision"] == "Rejected"
    assert result["compliance"]["compliance_status"] == "flagged"
    assert result["risk"]["risk_level"] == "skipped"


def test_processing_time_is_reported(mocker, valid_applicant):
    mocker.patch.object(kyc_agent, "get_customer_by_pan", return_value=None)
    valid_applicant["pan"] = "BADPAN"
    result = run_agents(valid_applicant)
    assert "processing_time_seconds" in result
    assert isinstance(result["processing_time_seconds"], float)
