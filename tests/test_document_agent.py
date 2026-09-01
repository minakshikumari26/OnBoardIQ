"""Tests for backend/agents/document_agent.py"""

from backend.agents import document_agent
from backend.agents.document_agent import _extract_fields, verify_document


class TestExtractFields:
    def test_pan_pattern(self, mock_pan_card_text):
        fields = _extract_fields(mock_pan_card_text)
        assert fields["pan"] == "ABCDE1234F"

    def test_dob_slash_format(self, mock_pan_card_text):
        fields = _extract_fields(mock_pan_card_text)
        assert fields["dob"] == "15/03/1990"

    def test_aadhaar_extraction(self):
        text = "Rahul Sharma\nDOB: 15-03-1990\n1234 5678 9012"
        # The agent strips spaces so downstream code sees a plain 12-digit string
        assert _extract_fields(text)["aadhaar"] == "123456789012"

    def test_no_fields_present(self):
        fields = _extract_fields("just some plain text")
        assert fields == {"pan": None, "dob": None, "aadhaar": None}

    def test_pan_must_have_word_boundary(self):
        # Long alphanumeric shouldn't produce false PAN matches
        text = "SOMEXTRAABCDE1234FSTRING"
        assert _extract_fields(text)["pan"] is None


class TestVerifyDocument:
    def _run(self, mocker, ocr_text, applicant):
        mocker.patch.object(document_agent, "Image")
        mocker.patch.object(document_agent.pytesseract, "image_to_string",
                            return_value=ocr_text)
        applicant["file_bytes"] = b"fake image bytes"
        return verify_document(applicant)

    def test_valid_document(self, mocker, valid_applicant, mock_pan_card_text):
        result = self._run(mocker, mock_pan_card_text, valid_applicant)
        assert result["document_status"] == "valid"
        assert result["extracted_fields"]["pan"] == "ABCDE1234F"

    def test_missing_file_bytes(self, valid_applicant):
        valid_applicant["file_bytes"] = None
        result = verify_document(valid_applicant)
        assert result["document_status"] == "invalid"

    def test_ocr_failure_returns_unreadable(self, mocker, valid_applicant):
        mocker.patch.object(document_agent, "Image")
        mocker.patch.object(document_agent.pytesseract, "image_to_string",
                            side_effect=Exception("tesseract crashed"))
        valid_applicant["file_bytes"] = b"garbage"
        result = verify_document(valid_applicant)
        assert result["document_status"] == "unreadable"

    def test_pan_mismatch(self, mocker, valid_applicant, mock_pan_card_text):
        valid_applicant["pan"] = "XYZAB9999Z"
        result = self._run(mocker, mock_pan_card_text, valid_applicant)
        assert result["document_status"] == "invalid"
        assert "does not match" in result["reason"]

    def test_name_not_in_document(self, mocker, valid_applicant, mock_pan_card_text):
        valid_applicant["name"] = "Somebody Else"
        result = self._run(mocker, mock_pan_card_text, valid_applicant)
        assert result["document_status"] == "invalid"
        assert "name" in result["reason"].lower()

    def test_no_pan_in_document(self, mocker, valid_applicant):
        result = self._run(mocker, "text without any PAN", valid_applicant)
        assert result["document_status"] == "invalid"
        assert "PAN" in result["reason"]
