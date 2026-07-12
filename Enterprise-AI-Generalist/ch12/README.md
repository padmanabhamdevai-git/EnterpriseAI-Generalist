# Chapter 12 — Multi-Agent Systems and Orchestration

A supervised multi-agent system, kept deliberately to the simplest form that
demonstrates real orchestration. The supervisor pattern is built by hand so
the coordination holds no mystery (as with Ch.11's single-agent loop).

| File | Book section | Purpose |
|---|---|---|
| `orchestrator.py` | 12.11.1 | The supervisor pattern from scratch: delegate → collect → decide, with SYSTEM-level guards |
| `specialists.py` | 12.11.3 | The specialist agents (product, pricing, ops) — each narrow + PACT-bounded; none can book |
| `quote_to_order.py` | 12.11.3 | The assembled system: supervisor + specialists + collective PACT + trust plane + gated booking |
| `memory.py` | 12.11.2 | Persistent memory as governed retrieval: scoping, write-side validation, retention |

## Run

```bash
cd ch12
cp ../ch01/.env . && cp ../ch01/ai_client.py .
python quote_to_order.py    # supervised team produces a quote; booking is gated
python memory.py            # governed persistent memory (no API key needed)
```

`quote_to_order.py` uses stub tools so it runs standalone. The SHAPE is
production: swap the stubs in `specialists.py` for the real Ch.9 governed
servers and the orchestration, guards, and collective bounding are unchanged.

## The multi-agent discipline this code enforces

- **System-level guards** (`SystemGuards`): a TOTAL budget across all agents
  (the #1 multi-agent guard), a total delegation limit, and coordination-loop
  detection. The failure modes live at the system level (§12.7), so the guards
  do too.
- **Concentrated authority**: NO specialist can book the order. Booking is
  concentrated in the supervisor behind a human gate — so the system's
  autonomy is "produce the quote alone, book only with approval". This defeats
  conflicting actions and makes a propagating injection harmless (a manipulated
  specialist can only recommend, never act).
- **Unified trace**: one observable record of the whole team's decisions —
  the only tractable way to debug emergent multi-agent behavior.
- **Governed memory** (`memory.py`): scoping = access control; write-side
  validation (a poisoned memory is permanent); retention. Memory is the Part II
  RAG discipline with a validated write path.

## When to build one of these (the honest gate)

> Multi-agent only for genuinely TEAM-SHAPED work: multiple DEEP, DISTINCT
> expertises that must be COORDINATED. Most work isn't — it's a single agent
> (Ch.11) or a workflow (Ch.10). Build multi-agent reluctantly, minimally,
> and rigorously.

Quote-to-order passes: four deep distinct expertises (product, pricing, ops,
contracts) coordinated into one quote. The returns exception agent (Ch.11)
does NOT — one expertise, one agent.

## Pedagogical notes

- `orchestrator.py` uses the same JSON-in-text protocol as Ch.11 (model-
  independent, legible). Production uses native tool/structured calling.
- The supervisor is built by hand for understanding; the production path is
  LangGraph-class orchestration (durable state, checkpointing, parallel
  delegation). What a framework contains vs. what stays YOUR design (the
  collective PACT, action concentration, system budget) is the Cursor
  exercise §12.12.
- `memory.py`'s write-time injection check is a simple keyword screen for
  teaching; production uses Ch.7's fuller PII/injection gate.

All companies, configs, and contracts are fictional.
