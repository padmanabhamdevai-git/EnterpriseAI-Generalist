# Chapter 18 — The Enterprise AI Architecture Blueprint

The book's capstone framework, executable. **Everything runs standalone: no API keys.**

```
ch18/
├── blueprint.py   # 7 layers + plane as data; Meridian's estate mapped; the boundary validator (§18.5-18.6)
├── placement.py   # the three placement rules over four workloads (§18.7.2)
└── README.md
```

## Run

```bash
python blueprint.py   # layer contracts, the estate map, and 3 amnesty-find violations flagged
python placement.py   # gravity / latency / egress over four workloads — incl. the analytics-copilot surprise
```

## The shape that matters

1. **Layers carry decisions; the validator enforces their boundaries.** Credentials
   above Layer 4, knowledge outside Layer 5, direct model calls outside Layer 6,
   components without plane hooks or owners — each finding maps to a §18.5
   anti-pattern, and each anti-pattern is the first brick of "the second estate."
2. **The request trace is the review method.** The validator is the trace as code;
   run it over a component inventory and the gap analysis writes itself.
3. **Place by the three rules, in order.** The analytics-copilot example is the
   one to internalize: data gravity overrides the "AI cloud" default, because a
   standing cross-cloud stream is an egress subscription with a chat interface.

## Adapt to your organization

Replace `MERIDIAN_ESTATE` with your amnesty inventory (Cursor can draft it from
IaC/configs — §18.12); extend the validator with your environment's risks
(vendor-connector detection, unmarked-AI-write checks — Exercise 5); wire it
into CI so the blueprint enforces itself; and render your one-page poster from
the same validated inventory, so the wall art and the enforcement never drift.
`placement.py`'s workloads become yours by swapping the data homes and latency
classes — the rules don't change.
