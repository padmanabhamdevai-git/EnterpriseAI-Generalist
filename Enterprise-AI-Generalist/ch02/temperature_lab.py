"""temperature_lab.py — measure, don't believe: sampling behavior by temperature (2.11.2).

Runs a factual prompt and a creative prompt at three temperatures, eight samples
each, and shows the spread of answers. Expected result: the factual answer barely
varies (the distribution is peaked); the creative one fans out with temperature.

Lesson: temperature controls variance where the model is uncertain — which is
exactly where factual tasks can least afford it.
"""
from collections import Counter

from ai_client import ask  # Chapter 1's wrapper — see ch02/README.md for path setup

FACTUAL = "What HTTP status code indicates 'resource not found'? Answer with the code only."
CREATIVE = "Invent a two-word codename for a project migrating invoices to the cloud."

SAMPLES = 8

for label, prompt in (("FACTUAL", FACTUAL), ("CREATIVE", CREATIVE)):
    print(f"\n=== {label} ===")
    for temp in (0.0, 0.7, 1.0):
        answers = Counter(
            ask(prompt, provider="openai", temperature=temp, max_tokens=20).text.strip()
            for _ in range(SAMPLES)
        )
        spread = ", ".join(f"'{a}'×{n}" for a, n in answers.most_common())
        print(f"  T={temp}: {spread}")
