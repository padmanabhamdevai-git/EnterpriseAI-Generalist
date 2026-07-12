# Chapter 1 — Documentation

Detailed developer documentation for the Chapter 1 code samples ("The Rise of the
Enterprise AI Generalist"). This complements the short `README.md` with setup
instructions, per-file walkthroughs, expected output, and troubleshooting.

---

## 1. What this chapter teaches

Chapter 1 gets your environment working and shows how to make your first
programmatic AI calls the *enterprise* way. Four practices are established here and
reused throughout the rest of the book:

1. **Secrets live in `.env`** (via `python-dotenv`), never hardcoded or printed.
2. **System prompts** set the model's role and constraints on every call.
3. **Token usage is surfaced** on every call — cost awareness from day one.
4. **Vendor independence** — application code depends on *your* interface, not on
   any single provider's SDK.

---

## 2. Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.10+ | Uses modern type hints (e.g. `list[TimedResponse]`). |
| OpenAI API key | For the OpenAI examples. |
| Anthropic API key | For the Anthropic examples. |
| Dependencies | `openai`, `anthropic`, `python-dotenv` (see repo `requirements.txt`). |

Install dependencies from the repository root:

```bash
pip install -r requirements.txt
```

---

## 3. Setup

1. Copy the environment template and add your real keys:

```bash
cd ch01
cp .env.example .env
```

2. Edit `.env` so it contains your keys:

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

> `.env` is git-ignored — never commit real secrets. Keep `.env.example` (the
> template with placeholder values) in version control instead.

---

## 4. Files in this chapter

| File | Book section | Purpose |
|---|---|---|
| `.env.example` | 1.10.1 | Template for API keys (copy to `.env`). |
| `first_call_openai.py` | 1.11.1 | Minimal professional OpenAI call. |
| `first_call_anthropic.py` | 1.11.2 | The same request via the Anthropic SDK. |
| `ai_client.py` | 1.11.3 | Provider-agnostic wrapper — tool independence in code. |
| `ai_client_async.py` | Exercise 4 | Concurrent multi-provider fan-out with latency comparison. |
| `.cursor/rules/project.mdc` | 1.12 | Cursor project rules file. |

### 4.1 `first_call_openai.py`

Your first programmatic AI request. Demonstrates a system message, an output cap
via `max_completion_tokens`, and printing total token usage.

Key call:

```python
response = client.chat.completions.create(
    model="gpt-5.5",
    messages=[
        {"role": "system", "content": "You are an enterprise integration analyst. ..."},
        {"role": "user", "content": "In two sentences, explain what an API gateway does, ..."},
    ],
    max_completion_tokens=200,
)
```

### 4.2 `first_call_anthropic.py`

The same request through Anthropic's SDK. Note the structural differences from
OpenAI worth learning:

- The `system` prompt is a **top-level parameter**, not a message in the list.
- Input and output tokens are reported **separately** (and priced differently).

### 4.3 `ai_client.py`

The most important file: a thin, provider-agnostic wrapper. Application code calls
`ask(...)` and receives a normalized `AIResponse`, regardless of vendor. Switching
providers is a one-word change.

```python
@dataclass
class AIResponse:
    text: str
    input_tokens: int
    output_tokens: int
    provider: str

def ask(prompt, system="", provider="anthropic", temperature=0.3, max_tokens=500) -> AIResponse:
    ...
```

- `provider`: `"openai"` or `"anthropic"` (raises `ValueError` otherwise).
- `max_tokens`: hard cap on output length (a cost and latency control).
- `temperature`: kept in the signature for interface stability, but not sent to the
  current models — see [§6 API compatibility](#6-api-compatibility-notes).

### 4.4 `ai_client_async.py`

Exercise 4 solution: reuses the synchronous `ask()` inside a `ThreadPoolExecutor`
to query both providers **concurrently**, then prints a table comparing wall-clock
latency and token usage side by side.

```python
def ask_both(prompt, system="", **kwargs) -> list[TimedResponse]:
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(_timed_ask, prompt, system, p, **kwargs)
                   for p in ("openai", "anthropic")]
        return [f.result() for f in futures]
```

---

## 5. How to run

From the `ch01` directory (after completing [§3 Setup](#3-setup)):

```bash
python first_call_openai.py
python first_call_anthropic.py
python ai_client.py
python ai_client_async.py
```

### Expected output (shape, not exact text)

`first_call_openai.py`:

```
<two-sentence explanation of an API gateway>

Tokens used: 189
```

`ai_client_async.py` prints a comparison table like:

```
provider       latency  in tok  out tok
openai           9.54s      25      128
anthropic       12.13s      29      500
```

Exact wording, token counts, and latency vary per run — model output is
non-deterministic and network-dependent.

---

## 6. API compatibility notes

The book's examples were written against an earlier version of the provider APIs.
The current flagship models (`gpt-5.5`, `claude-sonnet-5`) changed two things, and
the code in this folder has been updated accordingly:

| Change | Old | Current |
|---|---|---|
| OpenAI output cap parameter | `max_tokens=...` | `max_completion_tokens=...` |
| `temperature` parameter | `temperature=0.3` | Not supported — only the default is accepted, so the parameter is omitted. |

If you substitute a different/older model that still accepts these parameters, you
can re-add them.

---

## 7. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `AuthenticationError` / 401 | Missing or wrong key in `.env` | Verify `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` in `ch01/.env`. |
| `BadRequestError: 'max_tokens' is not supported ...` | Older parameter name on a new model | Use `max_completion_tokens` (already applied here). |
| `BadRequestError: 'temperature' ...` | Model only supports default temperature | Remove the `temperature` argument (already applied here). |
| `ModuleNotFoundError: openai / anthropic / dotenv` | Dependencies not installed | `pip install -r requirements.txt`. |
| Garbled characters (e.g. `�`) in the terminal | Windows console encoding of curly quotes/em-dashes | Cosmetic only; the underlying text is correct. Optionally set `PYTHONUTF8=1`. |

---

## 8. Models used

At the time of writing: `gpt-5.5` (OpenAI) and `claude-sonnet-5` (Anthropic).
Substitute the current mid-tier flagship if these have been superseded — model
selection is covered in Chapter 2.
