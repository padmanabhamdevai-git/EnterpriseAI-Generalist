"""auth.py — identity: validation, scopes, delegation (book 9.11.3).

The four verbs a server builder needs: VALIDATE, INSPECT SCOPES, EXCHANGE,
and never mint/store-long-lived.

PRODUCTION: validate_token wraps a maintained JWT library (PyJWT) and checks
ALL FOUR claims — signature, issuer, audience, expiry. This teaching version
carries a clearly-marked mock verifier so the chapter runs without an IdP;
the Caller shape and the authorization logic are identical to production.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field


@dataclass
class Caller:
    """The validated identity every tool receives."""

    subject: str                       # who (the user) — for authz + audit
    host: str                          # which app is calling
    scopes: list[str] = field(default_factory=list)
    cost_centers: list[str] = field(default_factory=list)  # fine-grained authz attr
    token: str = ""                    # raw, for delegation exchange


class TokenError(Exception):
    """Raised when a token fails any of the four validations."""


# --- Mock token format for the standalone demo -------------------------------
# A real deployment uses signed JWTs. Here a "token" is a base64-ish JSON blob
# with an expiry, so client_test.py can mint test identities without an IdP.
def make_mock_token(subject: str, host: str, scopes: list[str],
                    cost_centers: list[str], ttl_s: int = 300,
                    issuer: str = "mock-idp", audience: str = "mcp-gateway") -> str:
    payload = {"sub": subject, "azp": host, "scope": " ".join(scopes),
               "cost_centers": cost_centers, "iss": issuer, "aud": audience,
               "exp": int(time.time()) + ttl_s}
    return json.dumps(payload)


EXPECTED_ISSUER = "mock-idp"
EXPECTED_AUDIENCE = "mcp-gateway"


def validate_token(raw: str) -> Caller:
    """VALIDATE — all four checks. (Production: verify RS256 signature via
    JWKS; here we validate structure, issuer, audience, and expiry.)"""
    try:
        claims = json.loads(raw)
    except Exception as e:
        raise TokenError(f"malformed token: {e}") from e

    # issuer + audience (the checks hand-rolled servers skip)
    if claims.get("iss") != EXPECTED_ISSUER:
        raise TokenError("bad issuer")
    if claims.get("aud") != EXPECTED_AUDIENCE:
        raise TokenError("bad audience")
    # expiry
    if claims.get("exp", 0) < time.time():
        raise TokenError("token expired")

    return Caller(subject=claims["sub"], host=claims.get("azp", "unknown"),
                  scopes=claims.get("scope", "").split(),
                  cost_centers=claims.get("cost_centers", []), token=raw)


def require_scope(caller: Caller, scope: str) -> None:
    """INSPECT SCOPES — the runtime expression of the first law."""
    if scope not in caller.scopes:
        raise PermissionError(f"missing required scope: {scope}")


def exchange_token(user_token: str, audience: str) -> str:
    """EXCHANGE — trade a user token for a downstream-scoped token (delegation).

    Production: OAuth 2.0 token exchange (RFC 8693) against the IdP, with the
    exchanged token's audience RESTRICTED to the specific downstream. Here we
    re-issue a mock token re-audienced for the downstream, preserving subject
    and cost centers so downstream (RLS) sees the real user.
    """
    claims = json.loads(user_token)
    return make_mock_token(subject=claims["sub"], host=claims["azp"],
                           scopes=claims.get("scope", "").split(),
                           cost_centers=claims.get("cost_centers", []),
                           issuer=EXPECTED_ISSUER, audience=audience)
