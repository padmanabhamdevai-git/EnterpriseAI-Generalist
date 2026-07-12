# Chapter 4 — Advanced Prompting and Private AI

Code for sections 4.10–4.11 of the book.

| File | Book section | Purpose |
|---|---|---|
| `structured_output.py` | 4.11.1 | The Output Reliability Ladder in code: R1 raw → R2 validated (Pydantic) → R3 repair-and-retry |
| `analysis_pipeline.py` | 4.11.2 | Four-stage chain (extract → assess → draft → critique) with typed state, R4 rule gate, rubric critique loop |
| `private_pipeline.py` | 4.11.3 | Same pipeline routed to a local Ollama model, plus the hosted-vs-local plane comparison harness |
| `eval_notes.py` | 4.11.3 | The 12-note evaluation set (3 intentional traps) used by the plane comparison |

## Setup

```bash
cd ch04
cp ../ch01/.env .
cp ../ch01/ai_client.py .            # or export PYTHONPATH=../ch01
cp ../ch02/local_model.py .          # private_pipeline.py needs the local provider

python structured_output.py          # hosted; shows the repair loop in action
python analysis_pipeline.py          # hosted; full four-stage run with audit trail
ollama pull llama3.2                 # once
python private_pipeline.py           # local + comparison table
```

## Key design decisions (explained in the book)

- The validator's error message becomes the repair prompt (R3's core move).
- `rule_gate` is deterministic code, not a model call: AI proposes, code disposes.
- Bounded retries; exhaustion routes to a human queue, never a fourth attempt.
- The pipeline's validated stage objects ARE the audit trail.
- Routing tables (`ROUTES_PRIVATE`, `ROUTES_HYBRID`) express privacy posture as data.

Models used at time of writing: `gpt-5.5`, `claude-sonnet-5`, `llama3.2`. All companies, people, and part numbers are fictional.
