import requests

from backend.config.settings import OPENSANCTIONS_API_URL, OPENSANCTIONS_TIMEOUT


def check_compliance(data):
    name = data.get("name", "").strip()

    if not name:
        return {"compliance_status": "clear", "reason": "No name to screen", "matches": []}

    # Search the OpenSanctions public API
    params = {"q": name, "limit": 5}

    try:
        response = requests.get(OPENSANCTIONS_API_URL, params=params, timeout=OPENSANCTIONS_TIMEOUT)
        results = response.json().get("results", [])
    except Exception:
        # If API is down or offline, don't block onboarding
        return {"compliance_status": "clear",
                "reason": "Sanctions service unavailable",
                "matches": []}

    matches = []
    for item in results:
        score = item.get("score", 0)
        if score > 0.7:
            matches.append({
                "name": item.get("caption", ""),
                "score": round(score, 2),
                "topics": item.get("properties", {}).get("topics", []),
            })

    if matches:
        return {"compliance_status": "flagged",
                "reason": f"Found {len(matches)} sanctions match(es)",
                "matches": matches}

    return {"compliance_status": "clear",
            "reason": "No sanctions match found",
            "matches": []}
