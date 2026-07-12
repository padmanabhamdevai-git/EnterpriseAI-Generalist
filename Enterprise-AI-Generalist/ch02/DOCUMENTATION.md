# Chapter 2 — Documentation

Detailed developer documentation for the Chapter 2 code samples ("How Large
Language Models Actually Work"). Complements the short `README.md` with setup,
per-file walkthroughs, expected output, and — importantly — the changes required to
run these examples against today's *reasoning* models.

---

## 1. What this chapter teaches

Chapter 2 makes the mechanics of LLMs concrete and measurable:

1. **Tokens** are the unit of cost, capacity, and latency (`token_explorer.py`).
2. **Sampling variance** shows up where the model is uncertain (`temperature_lab.py`).
3. **Capability must be measured**, not assumed — the seed of an eval harness
   (`model_compare.py`).
4. **The provider interface generalizes** to local models too (`local_model.py`).

---

## 2. Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.10+ | Modern type hints. |
| ch01 wrapper | These scripts import `ai_client` from Chapter 1. |
| API keys | `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` (reused from ch01). |
| `tiktoken>=0.7.0` | For `token_explorer.py`. In `requirements.txt`. |
| Ollama (optional) | Only for `local_model.py`. See https://ollama.com |

Install dependencies from the repository root:

```bash
pip install -r requirements.txt
```

---

## 3. Setup — making the ch01 wrapper importable

These scripts do `from ai_client import ask`, which lives in `../ch01`. Pick one:

**Option A — add ch01 to `PYTHONPATH` (no file duplication):**

```bash
# Windows PowerShell
$env:PYTHONPATH="..\ch01"
# macOS/Linux
export PYTHONPATH=../ch01
```

`ai_client.py` calls `load_dotenv()`, which locates `ch01/.env` automatically
(it searches upward from the wrapper's own directory), so your keys are picked up.

**Option B — copy the wrapper and env next to these scripts:**

```bash
cp ../ch01/ai_client.py .
cp ../ch01/.env .
```

> On Windows, if you see `UnicodeEncodeError` for characters like `→`, enable UTF-8
> output: `$env:PYTHONUTF8="1"` (PowerShell). This is a console encoding issue, not
> a bug in the scripts.

---

## 4. Files in this chapter

| File | Book section | Purpose |
|---|---|---|
| `token_explorer.py` | 2.11.1 | Visualize tokenization; price a system prompt at production volume. |
| `temperature_lab.py` | 2.11.2 | Observe sampling variance: factual (peaked) vs. creative (fans out). |
| `model_compare.py` | 2.11.3 | Minimal evaluation harness — accuracy, latency, tokens per provider. |
| `local_model.py` | 2.11.4 | Extend the ch01 wrapper to a local Ollama model. |

### 4.1 `token_explorer.py`
Encodes sample strings with `tiktoken` (`o200k_base`) and prints the token
boundaries, then prices a 1,200-token system prompt at 50,000 calls/day. No API key
needed. Prices in the script are **illustrative** — always check current vendor
pricing.

### 4.2 `temperature_lab.py`
Samples a factual and a creative prompt several times and prints the spread. The
factual answer stays constant; the creative one varies. See
[§5 Reasoning-model changes](#5-reasoning-model-changes) for why this no longer
sweeps a `temperature` value.

### 4.3 `model_compare.py`
Runs a small eval set (classify / extract / reason) against each provider and
reports accuracy, average latency, and output tokens. Misses are printed in full —
"the misses teach more than the score."

### 4.4 `local_model.py`
Shows that because the ch01 wrapper normalized the interface, adding a model running
on your own hardware (via Ollama's OpenAI-compatible endpoint) is ~15 lines. Local
models still accept `temperature` and `max_tokens`, so no reasoning-model
adaptation is needed here.

Requires Ollama:

```bash
ollama pull llama3.2
python local_model.py
```

---

## 5. Reasoning-model changes

The book was written when the flagship models accepted a `temperature` parameter
and returned answers directly. The current models (`gpt-5.5`, `claude-sonnet-5`)
are **reasoning models**, which changes two things that affect this chapter:

1. **`temperature` is no longer accepted.** `temperature_lab.py` originally swept
   `temperature` from 0.0 → 1.0. That is now impossible, so the script instead
   samples each prompt multiple times at the model's default settings and observes
   the inherent spread. The lesson (variance appears where the model is uncertain)
   is unchanged.
2. **Reasoning consumes the output budget.** The models spend part of `max_tokens`
   "thinking" before emitting the answer. The book's tight caps (20–30 tokens)
   returned empty strings or a `400 max_tokens ... limit was reached` error, so the
   caps were raised (`temperature_lab.py` → 300, `model_compare.py` → 512).

A related wrapper fix lives in `../ch01/ai_client.py`: Anthropic responses may now
begin with a `ThinkingBlock`, so the wrapper concatenates only the `text` blocks
instead of assuming `content[0].text`.

---

## 6. How to run

From the `ch02` directory, after [§3 Setup](#3-setup):

```bash
python token_explorer.py
python temperature_lab.py
python model_compare.py
python local_model.py     # requires Ollama
```

### Observed output (shape; exact values vary)

`token_explorer.py`:

```
English prose: 71 chars → 12 tokens
  The| invoice| was| rejected| ...
...
That system prompt alone: $180.00/day → $65,700/year
```

`temperature_lab.py`:

```
=== FACTUAL (8 samples at default settings) ===
  '404'×8

=== CREATIVE (8 samples at default settings) ===
  'Nimbus Ledger'×6, 'Cloud Ledger'×2
```

`model_compare.py`:

```
openai       accuracy 100%   avg latency 14,245 ms   output tokens 92
anthropic    accuracy 100%   avg latency 6,898 ms    output tokens 118
```

> Note: reasoning models are slower and more expensive per call. `temperature_lab.py`
> makes 16 calls and can take several minutes; `model_compare.py` makes 6.

---

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: ai_client` | ch01 not importable | Set `PYTHONPATH=../ch01` or copy `ai_client.py` here (§3). |
| `ModuleNotFoundError: tiktoken` | Dependency missing | `pip install -r requirements.txt`. |
| `UnicodeEncodeError: '\u2192'` | Windows cp1252 console | `$env:PYTHONUTF8="1"`. |
| Empty answers / `400 max_tokens ... limit was reached` | Token cap too low for a reasoning model | Raise `max_tokens` (already applied here). |
| `AttributeError: 'ThinkingBlock' object has no attribute 'text'` | Anthropic returns thinking blocks | Fixed in `ch01/ai_client.py`. |
| Connection refused on `localhost:11434` | Ollama not running | Install/start Ollama and `ollama pull llama3.2`. |

---

## 8. Models used

At the time of writing: `gpt-5.5`, `claude-sonnet-5`, and `llama3.2` (local).
Substitute current equivalents as needed. Pricing constants in `token_explorer.py`
are illustrative — verify against the vendor's pricing page.
