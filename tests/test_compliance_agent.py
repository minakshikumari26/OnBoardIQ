"""Tests for backend/agents/compliance_agent.py"""

from unittest.mock import MagicMock

from backend.agents import compliance_agent
from backend.agents.compliance_agent import check_compliance


def _mock_response(mocker, json_body):
    fake_response = MagicMock()
    fake_response.json.return_value = json_body
    mocker.patch.object(compliance_agent.requests, "get", return_value=fake_response)


def test_clear_when_no_matches(mocker, sanctions_clear_response):
    _mock_response(mocker, sanctions_clear_response)
    result = check_compliance({"name": "Random Person"})
    assert result["compliance_status"] == "clear"
    assert result["matches"] == []


def test_flagged_on_high_score_match(mocker, sanctions_hit_response):
    _mock_response(mocker, sanctions_hit_response)
    result = check_compliance({"name": "Vladimir Putin"})
    assert result["compliance_status"] == "flagged"
    assert len(result["matches"]) == 1
    assert result["matches"][0]["score"] > 0.7


def test_low_score_match_is_ignored(mocker):
    _mock_response(mocker, {"results": [{
        "caption": "Someone", "score": 0.3,
        "properties": {"topics": []}
    }]})
    result = check_compliance({"name": "Someone"})
    assert result["compliance_status"] == "clear"


def test_network_error_falls_back_to_clear(mocker):
    mocker.patch.object(compliance_agent.requests, "get",
                        side_effect=Exception("network down"))
    result = check_compliance({"name": "Anyone"})
    assert result["compliance_status"] == "clear"
    assert "unavailable" in result["reason"].lower()


def test_empty_name_returns_clear_without_api_call(mocker):
    spy = mocker.patch.object(compliance_agent.requests, "get")
    result = check_compliance({"name": ""})
    assert result["compliance_status"] == "clear"
    spy.assert_not_called()
