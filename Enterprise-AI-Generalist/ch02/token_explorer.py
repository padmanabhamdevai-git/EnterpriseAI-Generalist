"""token_explorer.py — make tokens visible, then price them (book section 2.11.1).

Tokens are the unit of cost, capacity, and latency. This script shows where
token boundaries actually fall, then prices a realistic system prompt at
production volume — the most persuasive FinOps number you can show a team.
"""
import tiktoken

enc = tiktoken.get_encoding("o200k_base")  # tokenizer family used by recent OpenAI models

SAMPLES = {
    "English prose": "The invoice was rejected because it exceeded the purchase order amount.",
    "Identifier-heavy": "PO-2026-004417 rejected: amount 12,450.00 EUR > approved 10,000.00 EUR.",
    "JSON": '{"po": "PO-2026-004417", "status": "rejected", "reason": "over_limit"}',
    "Non-English": "La factura fue rechazada porque excedía el monto de la orden de compra.",
}

for label, text in SAMPLES.items():
    tokens = enc.encode(text)
    pieces = [enc.decode([t]) for t in tokens]
    print(f"\n{label}: {len(text)} chars → {len(tokens)} tokens")
    print("  " + "|".join(pieces))

# --- Price a realistic system prompt at production volume ---------------------
SYSTEM_PROMPT_TOKENS = 1200  # a typical well-developed enterprise system prompt
CALLS_PER_DAY = 50_000
PRICE_PER_M_INPUT = 3.00     # USD per million input tokens — check current pricing!

daily = SYSTEM_PROMPT_TOKENS * CALLS_PER_DAY * PRICE_PER_M_INPUT / 1_000_000
print(f"\nThat system prompt alone: ${daily:,.2f}/day → ${daily * 365:,.0f}/year")
print("Now trim 400 tokens of politeness from it and re-run this script.")
