"""technique_lab.py — zero-shot vs few-shot vs chain-of-thought, measured (book 3.11.2).

Task: classify supplier emails by required action — with deliberately fuzzy
boundary cases, because that is where techniques differentiate.

Read the trade, not just the score: few-shot buys boundary accuracy with input
tokens; chain-of-thought buys reasoning accuracy with output tokens (and
latency). Zero-shot is free.

Reasoning-era note: the current flagship models reason internally before
answering, so explicit chain-of-thought prompting overlaps with what the model
already does — the three variants may converge more than the book describes. The
lesson (few-shot pins boundary behavior; instructions still shape output) holds.
`temperature` is no longer accepted and `max_tokens` must leave room for internal
reasoning; see ch03/DOCUMENTATION.md.
"""
import time

from ai_client import ask  # see ch03/README.md for path setup

CATEGORIES = "[invoice_issue, delivery_delay, contract_question, escalation, other]"

# Boundary-heavy evaluation set: several cases sit between categories on purpose.
EVAL = [
    ("Invoice INV-4411 remains unpaid 60 days past terms. Our CFO will contact "
     "your leadership if this is not resolved this week.", "escalation"),
    ("The shipment for PO-2026-0071 will arrive Thursday instead of Monday due "
     "to a carrier issue.", "delivery_delay"),
    ("We noticed the unit price on invoice INV-4388 doesn't match the contracted "
     "rate in our MSA section 4.", "invoice_issue"),
    ("Could you confirm whether clause 7.2 permits early termination for "
     "convenience?", "contract_question"),
    ("Thanks for the quick turnaround on last week's order — great service.", "other"),
    ("Third reminder: INV-4402. We have paused further shipments until we hear "
     "back.", "escalation"),
]

ZERO_SHOT = (
    "Classify this supplier email into exactly one of {cats}. "
    "Answer with the category only.\n\nEmail: {email}"
)

FEW_SHOT = (
    "Classify supplier emails into exactly one of {cats}. "
    "Answer with the category only.\n\n"
    "Email: 'Invoice INV-9001 was short-paid by 400 EUR, please advise.'\n"
    "Category: invoice_issue\n\n"
    # The boundary lesson: money + threat = escalation, not invoice_issue.
    "Email: 'INV-9004 is 90 days overdue; we are referring this to legal.'\n"
    "Category: escalation\n\n"
    "Email: 'Truck breakdown: PO-555 delivery moves from Tue to Fri.'\n"
    "Category: delivery_delay\n\n"
    "Email: {email}\nCategory:"
)

CHAIN_OF_THOUGHT = (
    "Classify this supplier email into exactly one of {cats}.\n"
    "First, in two or three short steps, reason about the sender's primary "
    "intent and whether any threat or relationship risk is present. "
    "Then output the final category on its own last line as: CATEGORY: <answer>\n\n"
    "Email: {email}"
)


def final_answer(text: str) -> str:
    """Extract the category from either bare or CATEGORY:-marked output."""
    last = text.strip().splitlines()[-1]
    return last.split(":", 1)[-1].strip().lower()


def run(variant_name: str, template: str) -> None:
    correct, tokens, start = 0, 0, time.perf_counter()
    for email, expected in EVAL:
        resp = ask(template.format(cats=CATEGORIES, email=email),
                   system="You are a precise procurement operations assistant.",
                   provider="openai", max_tokens=512)
        tokens += resp.output_tokens
        if final_answer(resp.text) == expected:
            correct += 1
        else:
            print(f"  MISS [{variant_name}]: expected {expected!r} ← {email[:55]!r}")
    secs = time.perf_counter() - start
    print(f"{variant_name:<18} {correct}/{len(EVAL)} correct   "
          f"{tokens:>4} output tokens   {secs:>5.1f}s\n")


if __name__ == "__main__":
    for name, tpl in (("zero-shot", ZERO_SHOT),
                      ("few-shot", FEW_SHOT),
                      ("chain-of-thought", CHAIN_OF_THOUGHT)):
        run(name, tpl)
    print("Now swap in ten emails from your own domain and re-run.")
