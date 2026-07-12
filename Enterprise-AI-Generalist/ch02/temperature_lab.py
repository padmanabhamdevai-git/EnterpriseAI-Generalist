"""temperature_lab.py — measure, don't believe: sampling variance in practice (2.11.2).

The book's original experiment swept a `temperature` parameter from 0.0 to 1.0.
The current flagship models are *reasoning* models that no longer accept a
`temperature` parameter at all, so a direct sweep is impossible (see
ch02/DOCUMENTATION.md). Instead we sample each prompt several times at the model's
default settings and observe the inherent spread.

Expected result — and the lesson — is unchanged: the factual answer barely varies
(the distribution is peaked), while the creative one fans out. Variance appears
exactly where the model is uncertain, which is where factual tasks can least
afford it.
"""
from collections import Counter

from ai_client import ask  # Chapter 1's wrapper — see ch02/README.md for path setup

FACTUAL = "What HTTP status code indicates 'resource not found'? Answer with the code only."
CREATIVE = "Invent a two-word codename for a project migrating invoices to the cloud."

SAMPLES = 8
# Reasoning models spend part of the budget "thinking" before emitting the answer,
# so a tiny cap (the book used 20) truncates the response. Keep it generous.
MAX_TOKENS = 300

for label, prompt in (("FACTUAL", FACTUAL), ("CREATIVE", CREATIVE)):
    answers = Counter(
        ask(prompt, provider="openai", max_tokens=MAX_TOKENS).text.strip()
        for _ in range(SAMPLES)
    )
    spread = ", ".join(f"'{a}'×{n}" for a, n in answers.most_common())
    print(f"\n=== {label} ({SAMPLES} samples at default settings) ===")
    print(f"  {spread}")
