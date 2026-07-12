# Chapter 10 — Automation Foundations

Workflow reliability, done properly. The Python files teach the patterns
tool-independently; the JSON files are importable n8n workflows showing the
five TIER-R properties in real node structure.

| File | Book section | Purpose |
|---|---|---|
| `idempotency.py` | 10.11.1 | The idempotency-key pattern: stable key, durable atomic claim, before side effects |
| `workflow_review.py` | 10.11.2 | A TIER-R readiness checker for exported n8n workflows (heuristic; sorts a review queue) |
| `workflows/returns_coordinator.json` | 10.9 | The returns workflow — DETERMINISTIC, TIER-R complete, acts through the Ch.9 MCP gateway |
| `workflows/email_triage_ai.json` | 10.4.2 | An AI-INFUSED workflow: one judgment node (classify) → validated → deterministic route |

## Run the Python patterns (no n8n needed)

```bash
cd ch10
python idempotency.py          # shows the retry being safely skipped
python workflow_review.py workflows/returns_coordinator.json
python workflow_review.py workflows/email_triage_ai.json
```

## Import the workflows into n8n

1. Install n8n — self-hosted (`npx n8n` or Docker) or n8n Cloud. See
   https://docs.n8n.io. **Self-host** when workflows touch sensitive data
   you must keep in your boundary (§10.6–10.7).
2. In the n8n UI: **Workflows → Import from File** → choose a JSON.
3. Replace placeholders: credentials, the `mcp-gateway.internal` URLs
   (point them at your Ch.9 gateway or a mock), and the `wf_processed`
   Postgres table (`CREATE TABLE wf_processed (key TEXT PRIMARY KEY, at
   TIMESTAMPTZ DEFAULT now());`).
4. The `_comment` keys are annotations for reading — n8n ignores unknown
   keys. Each maps a node to its TIER-R role.

## The two workflows, and why they differ

- **returns_coordinator** is DETERMINISTIC: the flowchart draws itself
  (§10.4.2), so there is no AI node. It shows all five TIER-R properties:
  event trigger, idempotency claim + "first time only?" gate, retry-on-fail
  and a dead-letter/error workflow, a log+metric node, and safe re-runs.
- **email_triage_ai** is AI-INFUSED: mostly deterministic, with ONE
  judgment node (classify the free-text email). Note the **Validate
  Classification** node — it checks the AI output against an allow-list
  *before* any branch acts (the injection defense, §10.18). The AI informs
  a deterministic rule table; it never triggers an arbitrary action.

## The discipline this chapter enforces

> Reach for the least powerful tool that works: cron+script → workflow →
> AI-infused → agent. Draw the flowchart first — if it draws itself, you
> don't need an agent.

## Caveats

- `workflow_review.py` is a **heuristic** — it string-matches the JSON to
  sort a review queue. A false PASS on a cleverly-named node is expected;
  the human review is the backstop.
- n8n's export schema evolves; if a JSON won't import into your n8n
  version, re-create the nodes from the annotations (the *structure* and
  the TIER-R roles are the lesson, not the exact schema).

All companies, systems, and URLs are fictional.
