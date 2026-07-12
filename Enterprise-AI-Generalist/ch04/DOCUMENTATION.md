# Chapter 4 — Documentation

Detailed developer documentation for the Chapter 4 code samples ("Advanced
Prompting and Private AI"). Complements the short `README.md` with setup,
per-file walkthroughs, expected output, and reasoning-model notes.

---

## 1. What this chapter teaches

Chapter 4 moves from single prompts to **reliable, multi-stage pipelines** with
governance and privacy posture:

1. **Output Reliability Ladder** — R1 raw → R2 validated (Pydantic) → R3
   repair-and-retry → R4 deterministic rule gate (`structured_output.py`).
2. **Chained stages with typed state** — EXTRACT → ASSESS → DRAFT → CRITIQUE,
   where each stage hands a Pydantic object to the next (`analysis_pipeline.py`).
3. **Private AI plane comparison** — same extraction logic routed to hosted vs.
   local models, scored on the same eval set (`private_pipeline.py`).

---

## 2. Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.10+ | Modern type hints. |
| ch01 wrapper | All API scripts import `ai_client`. |
| ch02 `local_model.py` | `private_pipeline.py` imports it for the local plane. |
| `pydantic>=2.7.0` | Structured outputs and inter-stage contracts. |
| API keys | `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` (reused from ch01). |
| Ollama (optional) | Only for the private plane in `private_pipeline.py`. |

Install dependencies from the repository root:

```bash
pip install -r requirements.txt
```

---

## 3. Setup

Make the ch01 wrapper (and ch02 local model) importable:

```bash
# Windows PowerShell
$env:PYTHONPATH="..\ch01;..\ch02"
$env:PYTHONUTF8="1"
# macOS/Linux
export PYTHONPATH=../ch01:../ch02
```

The wrapper's `load_dotenv()` finds `ch01/.env` automatically.

---

## 4. Files in this chapter

| File | Book section | Purpose |
|---|---|---|
| `structured_output.py` | 4.11.1 | Output Reliability Ladder: R1 raw → R2 validated → R3 repair-and-retry. |
| `analysis_pipeline.py` | 4.11.2 | Four-stage chain with typed state, R4 rule gate, rubric critique loop. |
| `private_pipeline.py` | 4.11.3 | Same pipeline routed to local Ollama + hosted vs. private plane comparison. |
| `eval_notes.py` | 4.11.3 | 12-note evaluation set (3 intentional traps) for the plane comparison. |

### 4.1 `structured_output.py`
Extracts `InspectionFacts` from a free-text inspection note. `extract()` is R1
(raw JSON). `extract_validated()` is R2+R3: Pydantic validation with bounded
retries, where the validator's error message becomes the repair prompt.

### 4.2 `analysis_pipeline.py`
Full pipeline: EXTRACT → ASSESS → DRAFT → CRITIQUE. Key design points:
- `rule_gate()` is deterministic code that outranks the model (R4).
- The critique loop is bounded (max 2 revisions); exhaustion routes to human queue.
- The accumulated stage objects ARE the audit trail.

### 4.3 `private_pipeline.py`
Runs the extraction stage across `eval_notes.py` on hosted and (optionally) local
planes. Routing tables (`ROUTES_HOSTED`, `ROUTES_PRIVATE`) express privacy
posture as data. If Ollama is not running, the private plane is skipped with a
clear message.

### 4.4 `eval_notes.py`
12 inspection notes with expected `defect_category` and `defect_confirmed`. Traps:
- **#7** — liquid damage alongside confirmed defect (rule 3 must win).
- **#9** — customer-reported only, not bench-confirmed.
- **#11** — purchase outside coverage window.

---

## 5. Reasoning-model changes

Consistent with ch01–ch03, the current flagship models are reasoning models.
Adjustments made here:

1. **`temperature` removed** from all `ask()` / `ask_fn()` calls.
2. **Token caps raised** — reasoning models spend part of the budget "thinking"
   before emitting JSON or prose:
   - `structured_output.py`: `max_tokens` 400 → 700
   - `analysis_pipeline.py` `_call_json`: 600 → 1200
   - `draft()` and revision loop: 400 → 800

Without these raises, validation sees truncated JSON or empty strings and the
repair loop fires unnecessarily.

---

## 6. How to run

```bash
python structured_output.py      # R1 + R2+R3 extraction demo
python analysis_pipeline.py      # full four-stage pipeline (~2 min)
python private_pipeline.py       # hosted plane + local if Ollama available
```

For the private plane:

```bash
ollama pull llama3.2
python private_pipeline.py
```

### Observed output (shape; exact values vary)

`structured_output.py`:

```
R2+R3 (validated, repaired):
  attempt 1: VALID
{ "unit_id": "MS-88213", "defect_category": "sensor_drift", ... }
```

`analysis_pipeline.py`:

```
Stage 1 · EXTRACT
  attempt 1: VALID
Stage 2 · ASSESS
Stage 3 · DRAFT
Stage 4 · CRITIQUE
Outcome: complete | escalated: critique loop exhausted | escalated: human queue
```

All three outcomes are valid — the pipeline documents itself in the audit trail.

`private_pipeline.py` (hosted plane):

```
hosted     accuracy 10/12 (83%)   avg latency   3.5s per note
Skipping private plane: Ollama not running on localhost:11434.
```

---

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: ai_client` | ch01 not importable | Set `PYTHONPATH=../ch01` or copy `ai_client.py` here. |
| `ModuleNotFoundError: local_model` | ch02 not importable | Add `../ch02` to `PYTHONPATH` or copy `local_model.py` here. |
| `ModuleNotFoundError: pydantic` | Dependency missing | `pip install -r requirements.txt`. |
| Validation fails all 3 attempts | Truncated JSON from low token cap | Raise `max_tokens` (already applied). |
| `critique loop exhausted` | Draft keeps failing rubric after max revisions | Valid outcome — routes to human queue. Check `critique_r*` keys in trail. |
| Private plane skipped | Ollama not installed/running | Install from https://ollama.com, `ollama pull llama3.2`. |
| Hosted plane misses traps #7/#9 | Model misclassifies boundary cases | Expected on a 12-note demo; expand eval set for selection decisions. |

---

## 8. Key design decisions (from the book)

- The validator's error message becomes the repair prompt (R3's core move).
- `rule_gate` is deterministic code, not a model call: AI proposes, code disposes.
- Bounded retries; exhaustion routes to a human queue, never a fourth attempt.
- The pipeline's validated stage objects ARE the audit trail.
- Routing tables express privacy posture as data.

Models used at time of writing: `gpt-5.5`, `claude-sonnet-5`, `llama3.2`. All
companies, people, and part numbers are fictional.
