# Chapter 20 — Operating AI at Scale: LLMOps, Cost, and the Road Ahead

The book's finale — the operations disciplines that make every prior capability
pay off over time, and the two frameworks that turn them into a trajectory.
**Everything runs standalone: no API keys.**

```
ch20/
├── unified_trace.py   # one correlation ID -> one timeline -> the four signal classes (§20.6.1)
├── finops.py          # cost per outcome + the four levers in priority order (§20.7)
├── maturity.py        # the Capability Maturity Model self-assessment -> the next rung (§20.8)
└── README.md
```

## Run

```bash
python unified_trace.py   # Mira's call as one unified trace; the four signals derived
python finops.py          # the four levers on a real workload, cost per outcome before/after
python maturity.py        # the 5-level model; Meridian assessed at Level 4, climbing
```

## The shape that matters

1. **The unified trace is the foundation.** One correlation ID threaded through
   every layer turns four logs into one timeline — the substrate for debugging,
   costing, evaluation, and audit alike. The three signals that don't throw
   errors (quality, cost, safety) are where systems fail silently.
2. **FinOps in priority order.** Don't call the model, route to the right model,
   compress the context, batch — measured as cost per *outcome*, not per token.
   Caching + routing take the majority of the cost out; observability pays for
   itself out of the waste it reveals.
3. **Locate honestly, build the next rung, never skip.** `maturity.py`'s rule
   enforces it: you can't claim Level 4's observability while failing Level 3's
   enforced platform. The book is the sequence of next-rungs.

## Adapt to your organization

Instrument your estate for the unified trace (§20.10 Step 2 — the highest-leverage
change) on your existing observability platform; wire the eval pipeline as CI;
model your real workload in `finops.py` and apply the levers; run `maturity.py`'s
assessment honestly and build the one next thing it names. This is the Level-3→4
move for a real estate — and, with the improve loop closed, the 4→5 move.

## The whole book

The `ch01`–`ch20` companion collection is the maturity ladder in code: the
gateway (ch02) is the 1→2 move, the platform (ch07–ch18) is 2→3, these
operations are 3→4, the improve flywheel is 4→5. Run them in order and you have
built, in miniature, the estate the book describes.
