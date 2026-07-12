# LOGIC.md — What Is Identical, What Is Costume

One automation, three family-native expressions. Read all three in an hour and the
chapter's economics become tactile.

## The identical core (the part the Portability Ledger protects)

| Element | Value — same in all three |
|---|---|
| Trigger contract | new email on the support mailbox; at-least-once delivery assumed |
| Judgment | one classification prompt (`support/triage-classify@v3` in the registry) |
| Allow-list | `returns / order-status / billing / other` — anything else fail-safes |
| Action | route via governed door `POST /doors/support/route`, never a raw credential |
| Idempotency | key `triage:{email_id}` — redelivery is harmless |
| Injection defense | validation **after** the judgment step; email content is data, not instructions |
| TIER-R | T (defined trigger), I (key), E (fail-safe allow-list), R (retryable), R (logged) |

## The costume (the part each platform holds)

| | n8n JSON (Family 1) | Agent spec (Family 3) | Python (Family 5) |
|---|---|---|---|
| Build time | longest to wire | fastest to draft | in between |
| Operations | the engine runs it | the studio runs it | you run it forever |
| Guardrail enforcement | structural (Switch node) | configuration you must test | structural (code) |
| Export path | JSON (this file) | this spec in git | git, natively |
| What's hostage on exit | node graph, credentials config | deployment, connector config | nothing but hosting |

Same logic, three cost structures — that is the landscape in miniature (§13.11.3).

## The lesson

The n8n version took the longest to wire but operates itself. The studio spec was
fastest to draft but its guardrails are configuration you must test — which is why
its acceptance tests are the longest section of the spec. The code version is fifty
lines you own forever.

None of the three is "best." The choice is a task-profile question (§13.9): who
builds it, who operates it, what it may touch, and what it costs at your volume.
What must never vary is the core — and because the core lives in *your* registry,
*your* doors, and *your* repo, you can re-costume it in an afternoon. That is the
Portability Ledger reading green.
