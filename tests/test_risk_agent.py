"""Tests for backend/agents/risk_agent.py"""

from backend.agents.risk_agent import assess_risk


def test_low_risk_profile():
    """Prime-age, high-income, salaried, KYC + doc verified → Low."""
    result = assess_risk({
        "age": 35, "monthly_income": 100000,
        "employment_type": "Salaried",
        "kyc_status": "verified", "document_status": "valid",
    })
    assert result["risk_level"] == "Low"
    assert result["risk_score"] >= 70


def test_high_risk_profile():
    """Young, low income, freelancer, KYC failed, doc invalid → High."""
    result = assess_risk({
        "age": 20, "monthly_income": 5000,
        "employment_type": "Freelancer",
        "kyc_status": "failed", "document_status": "invalid",
    })
    assert result["risk_level"] == "High"
    assert result["risk_score"] < 45


def test_score_stays_in_range():
    """No matter how extreme the inputs, score must be 0-100."""
    hi = assess_risk({"age": 35, "monthly_income": 10_000_000,
                      "employment_type": "Government",
                      "kyc_status": "verified", "document_status": "valid"})
    lo = assess_risk({"age": 18, "monthly_income": 0,
                      "employment_type": "Unknown",
                      "kyc_status": "failed", "document_status": "invalid"})
    assert 0 <= hi["risk_score"] <= 100
    assert 0 <= lo["risk_score"] <= 100


def test_factors_are_reported():
    result = assess_risk({
        "age": 30, "monthly_income": 60000,
        "employment_type": "Salaried",
        "kyc_status": "verified", "document_status": "valid",
    })
    factor_names = {f["factor"] for f in result["factors"]}
    assert "Age" in factor_names
    assert "Income" in factor_names
    assert "Employment" in factor_names


def test_government_employment_boosts_score():
    salaried = assess_risk({"age": 30, "monthly_income": 50000,
                            "employment_type": "Salaried",
                            "kyc_status": "verified", "document_status": "valid"})
    govt = assess_risk({"age": 30, "monthly_income": 50000,
                        "employment_type": "Government",
                        "kyc_status": "verified", "document_status": "valid"})
    assert govt["risk_score"] >= salaried["risk_score"]
