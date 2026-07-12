# Chapter 7 — Enterprise Knowledge Platforms

Extends the ch06 service to platform grade: engine-enforced multi-tenancy,
IdP-derived entitlements, a connector contract, and the PII gate at
processing time.

| File | Book section | Purpose |
|---|---|---|
| `rls_policies.sql` | 7.11.1 | Row-level security: visibility enforced by Postgres, not app discipline |
| `tenancy.py` | 7.11.1 | Entitlement resolution: IdP groups → knowledge tiers → session binding |
| `connector.py` | 7.11.2 | The connector contract (changes, deletions, ACLs, freshness) + filesystem reference impl |
| `pii_gate.py` | 7.11.3 | Link-3 gate: deterministic patterns + LLM screening; quarantine, never silent drop |
| `sample_docs/` | Lab 1–2 | A second domain's documents, tiered by subfolder |

## Quick start (requires the ch06 stack)

```bash
cd ch07
cp ../ch01/.env .                    # DATABASE_URL from ch06
cp ../ch01/ai_client.py .

psql "$DATABASE_URL" -f rls_policies.sql
python tenancy.py                    # demo: three identities → three tier sets
python connector.py --source ./sample_docs --domain hr
python pii_gate.py                   # runs the gate against seeded test chunks
```

## Connection-pooling caveat (production)

`set_session_tiers` uses session-scoped `set_config`. Under a
transaction-mode pooler (pgbouncer), use the transaction-scoped variant —
`set_config('app.tiers', ..., true)` inside the same transaction as the
query — or tiers will leak across pooled sessions. The book's §7.11.1
and this repo's `tenancy.py` include both variants.

## Design decisions (explained in the book)

- After session tiers are bound, over-retrieval is not a bug the
  application can have — the engine refuses. That is the only multi-tenant
  posture worth defending in an audit.
- `GROUP_TIER_MAP` is deliberately a small reviewed artifact — the
  entitlement policy itself. In production it externalizes to the
  per-domain register YAML (see `register_cli.py` exercise, §7.12).
- Connectors must see deletions: erasure (ch06's drill) is only as good
  as the connector's ability to notice a deletion happened.
- The PII gate runs at processing, before embedding — vectors are not
  encryption, and un-embedding a leak is not a thing.

Models used at time of writing: `gpt-5.5` (PII screening, pinned).
All companies, groups, and documents are fictional.
