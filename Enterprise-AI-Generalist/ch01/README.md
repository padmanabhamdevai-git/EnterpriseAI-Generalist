# Chapter 1 — The Rise of the Enterprise AI Generalist

Code for sections 1.10–1.12 of the book.

| File | Book section | Purpose |
|---|---|---|
| `first_call_openai.py` | 1.11.1 | Minimal professional OpenAI call (system role, low temperature, token accounting) |
| `first_call_anthropic.py` | 1.11.2 | Same request via the Anthropic SDK |
| `ai_client.py` | 1.11.3 | Provider-agnostic wrapper — tool independence in code |
| `ai_client_async.py` | Exercise 4 solution | Concurrent multi-provider fan-out with latency comparison |
| `.env.example` | 1.10.1 | Template for API keys (copy to `.env`) |
| `.cursor/rules/project.mdc` | 1.12 | Cursor project rules file |

## Run

```bash
cd ch01
cp .env.example .env       # add your keys
python first_call_openai.py
python first_call_anthropic.py
python ai_client.py
python ai_client_async.py
```

Models used at time of writing: `gpt-5.5` (OpenAI), `claude-sonnet-5` (Anthropic). Substitute the current mid-tier flagship if these have been superseded.
