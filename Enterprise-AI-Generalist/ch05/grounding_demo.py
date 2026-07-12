"""grounding_demo.py — the same question, three ways (book 5.11.3).

1. Ungrounded: the model answers from its weights (Priya's incident).
2. Grounded: mini_rag answers from the corpus, with citations.
3. Absent: a question the corpus can't answer — refusal, not invention.

This is Chapter 5's argument as an experiment you can re-run forever.
The corpus's Sev-1 runbook deliberately differs from plausible defaults
(20-minute SLA, an "Incident Conductor", a chat-first bridge) so the
ungrounded answer's fabrications are checkable, not debatable.
"""
from ai_client import ask
from mini_rag import answer

QUESTION = "What's the escalation path for a Sev-1 outage at Meridian Systems?"
ABSENT = "What is Meridian's policy on bringing dogs to the office?"

print("=" * 70)
print("1 · UNGROUNDED — the closed-book exam:")
print(ask(QUESTION,
          system="You are Meridian Systems' helpful internal assistant.",
          provider="anthropic", temperature=0.3, max_tokens=300).text)
print("\n   ^ Fluent. Specific. Fabricated. Check any 'fact' above against")
print("     corpus.py — the real runbook says something else entirely.\n")

print("=" * 70)
print("2 · GROUNDED — the open-book exam:")
print(answer(QUESTION))

print("\n" + "=" * 70)
print("3 · ABSENT — the honest refusal:")
print(answer(ABSENT))
