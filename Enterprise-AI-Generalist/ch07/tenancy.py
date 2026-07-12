"""tenancy.py — entitlement resolution: identity → groups → tiers (book 7.11.1).

The mapping table is governance: small, reviewed, versioned. In production
the groups come from the IdP's token claims (Entra/Okta-class); the mapping
logic is identical. The platform stores tiers on documents and nothing
about people.
"""
import os

from dotenv import load_dotenv

load_dotenv()

MAPPING_VERSION = "2026-06-01"  # bump on every reviewed change; log it per query

GROUP_TIER_MAP = {  # reviewed artifact — this IS the entitlement policy
    "all-staff":        ["all-employees"],
    "people-managers":  ["all-employees", "people-managers"],
    "hr-team":          ["all-employees", "people-managers", "hr-only"],
    "support-agents":   ["all-employees", "support"],
}


def resolve_tiers(idp_groups: list[str]) -> list[str]:
    """Union of tiers across the caller's groups. Unknown groups grant
    nothing — deny-by-default posture."""
    tiers: set[str] = set()
    for g in idp_groups:
        tiers.update(GROUP_TIER_MAP.get(g, []))
    return sorted(tiers) or ["public"]


def set_session_tiers(conn, tiers: list[str],
                      transaction_scoped: bool = False) -> None:
    """Bind resolved tiers to the DB session; RLS does the rest.

    After this call, the application code CANNOT retrieve beyond the
    caller's entitlements — even if the application code has bugs.

    transaction_scoped=True is REQUIRED under transaction-mode poolers
    (pgbouncer): call inside the same transaction as the query.
    """
    conn.execute("SELECT set_config('app.tiers', %s, %s)",
                 (",".join(tiers), transaction_scoped))


def audit_line(identity: str, groups: list[str], tiers: list[str]) -> str:
    """The reconstructable audit record: who, via which groups, got which
    tiers, under which mapping version."""
    return (f"entitlement identity={identity} groups={','.join(groups)} "
            f"tiers={','.join(tiers)} mapping={MAPPING_VERSION}")


if __name__ == "__main__":
    DEMO_IDENTITIES = {
        "priya@meridian.example":  ["all-staff", "support-agents"],
        "manager@meridian.example": ["all-staff", "people-managers"],
        "hrlead@meridian.example":  ["all-staff", "hr-team"],
        "contractor@partner.example": ["external-vendors"],   # unmapped → public
    }

    for identity, groups in DEMO_IDENTITIES.items():
        tiers = resolve_tiers(groups)
        print(audit_line(identity, groups, tiers))

    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        import psycopg  # lazy: entitlement logic must not require libpq

        print("\nRLS demo (same query, two identities):")
        with psycopg.connect(db_url) as conn:
            for identity in ("priya@meridian.example", "hrlead@meridian.example"):
                tiers = resolve_tiers(DEMO_IDENTITIES[identity])
                with conn.transaction():
                    set_session_tiers(conn, tiers, transaction_scoped=True)
                    n = conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
                print(f"  {identity:<28} sees {n} chunks (tiers={tiers})")
    else:
        print("\n(set DATABASE_URL to run the live RLS demo)")
