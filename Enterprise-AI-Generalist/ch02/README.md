# Chapter 2 — How Large Language Models Actually Work

Code for sections 2.10–2.11 of the book.

| File | Book section | Purpose |
|---|---|---|
| `token_explorer.py` | 2.11.1 | Visualize tokenization; price a system prompt at production volume |
| `temperature_lab.py` | 2.11.2 | Measure sampling variance by temperature (factual vs. creative) |
| `model_compare.py` | 2.11.3 | Minimal evaluation harness — seed of the Selection Matrix's Capability evidence |
| `local_model.py` | 2.11.4 | Extend the Chapter 1 wrapper to a local Ollama model |

## Setup

These scripts import `ai_client` from `../ch01`. Run them from this folder after making ch01 importable:

```bash
cd ch02
cp ../ch01/.env .
# Option A (simplest): copy the wrapper next to these scripts
cp ../ch01/ai_client.py .
# Option B: add ch01 to PYTHONPATH instead
# export PYTHONPATH=../ch01     (Windows PowerShell: $env:PYTHONPATH="..\ch01")

python token_explorer.py
python temperature_lab.py
python model_compare.py
```

For `local_model.py`, first install Ollama (https://ollama.com), then:

```bash
ollama pull llama3.2
python local_model.py
```

Models used at time of writing: `gpt-5.5`, `claude-sonnet-5`, `llama3.2`. Substitute current equivalents as needed; prices in `token_explorer.py` are illustrative — always check the vendor's pricing page.
