# Chapter 13 — The Automation Platform Landscape

Decision tools, not model callers: **everything here runs standalone with no API
keys and no network.**

```
ch13/
├── scorecard.py           # C-FIT-S calculator: profiles + candidates as data, weighted totals + sensitivity
├── profiles.py            # Meridian's three task profiles (W, C, A) with weights and evidence strings
├── tco_model.py           # five-line TCO + credit-vs-BYO crossover calculator (§13.7)
├── portability_ledger.py  # the Portability Ledger as a checkable artifact (§13.7.3)
├── three_ways/            # the same email-triage automation in three family-native expressions
│   ├── email_triage.n8n.json      # Family 1: importable n8n export (Ch. 10 conventions)
│   ├── email_triage_agentspec.md  # Family 3: an agent-studio build spec (PACT-shaped)
│   ├── email_triage.py            # Family 5: plain code, runnable with a stub model
│   └── LOGIC.md                   # what is identical (the core) vs. costume (the platform)
└── README.md
```

## Run

```bash
python scorecard.py            # Meridian's three selections + sensitivity checks
python tco_model.py            # the credit crossover table + a five-line TCO example
python portability_ledger.py   # two example ledgers: disciplined pilot vs. accreted adoption
python three_ways/email_triage.py   # the code-first expression, incl. the injection case
```

`three_ways/email_triage.n8n.json` imports into n8n (self-hosted or cloud). Wire your
own credentials after import — the file contains none (Ch. 9). The `_comment` keys are
ignored by n8n and annotate the TIER-R properties in the node structure.

## Adapt to your organization

1. Copy `profiles.py`; replace Meridian's profiles with your own task profiles —
   one per distinct need, never one for "the enterprise" (§13.9 step 1).
2. Replace the generic candidates with your real ones, but keep the rule the code
   enforces: **every score carries an evidence string** — a pilot result, a
   document, or a measurement. `scorecard.py` rejects evidence-free scores.
3. Measure your own `credit_markup` from the vendor's credit schedule before
   running `tco_model.py`; the 4.0x default is a teaching value.
4. Open a `PortabilityLedger` for every platform **on adoption day**. The two
   examples in `portability_ledger.py` show why.

## The point

Products churn; the families hold; the method outlives any vendor list. The durable
skills are classification (the family map), evidence-based selection (C-FIT-S),
honest economics (the five-line TCO and the crossover), and portability as practiced
discipline (the Ledger). The platforms named in the book are examples, not
endorsements — verify current positioning and pricing against vendor documentation
before any real selection.
