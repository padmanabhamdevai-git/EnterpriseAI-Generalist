"""knowledge_client.py — stub of the ch06 /ask call (book 9.11.2).

Represents calling the already-governed knowledge platform with a DELEGATED
user token. In production this is an HTTP call to ch06's /ask carrying the
exchanged bearer token; the platform's RLS (Ch. 7) filters by the user's
tiers. Here we simulate RLS by reading the tier out of the mock token.
"""
from __future__ import annotations

import json

# Fixture: answers keyed by the tier required to see them.
_ANSWERS = {
    "all-employees": {
        "answer": "Cross-border remote work is limited to 20 business days per "
                  "year with HR approval [Remote-Policy §2.3].",
        "citations": [{"doc": "Remote-Policy", "section": "2.3"}],
        "status": "answered",
    },
    "hr-only": {
        "answer": "Approved exceptions are logged in the HR case system with the "
                  "approving VP and review date [HR-Internal §1].",
        "citations": [{"doc": "HR-Internal", "section": "1"}],
        "status": "answered",
    },
}


def ask_knowledge(question: str, bearer: str) -> dict:
    """Call the knowledge platform as the delegated user. RLS (simulated)
    returns only what the caller's tiers permit; otherwise a refusal."""
    claims = json.loads(bearer)
    tiers = set(claims.get("cost_centers", [])) | set(claims.get("scope", "").split())
    # Simulate RLS: HR-only content only for hr-team callers.
    if "hr-only" in tiers or "hr-team" in tiers:
        return _ANSWERS["hr-only"] if "exception" in question.lower() \
            else _ANSWERS["all-employees"]
    if "exception" in question.lower():
        return {"answer": "This isn't covered in the documents you can access.",
                "citations": [], "status": "refused"}
    return _ANSWERS["all-employees"]
