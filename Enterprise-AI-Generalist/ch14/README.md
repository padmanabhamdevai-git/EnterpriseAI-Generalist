# Chapter 14 — Voice Agents and Conversational Interfaces

The design and QA layer of a voice program — the part that outlives any platform
dashboard. **Everything runs standalone: no API keys, no audio hardware.**

```
ch14/
├── turn_budget.py        # the latency ledger: three stacks vs the 900-1500 ms window (§14.7)
├── voice_brief.py        # the VOICE brief as validated data; renders the system prompt (§14.5)
├── call_evaluator.py     # post-call QA checks over transcripts — the brief, checked (§14.11.3)
├── sample_calls/
│   ├── call_good.txt                  # containment done right (passes all checks)
│   ├── call_missing_disclosure.txt    # operationally perfect, unlaunchable (compliance fail)
│   └── call_should_have_escalated.txt # red-line engaged + human request argued with
└── README.md
```

## Run

```bash
python turn_budget.py       # untuned vs tuned vs over-tuned: the §14.20 tuning story in numbers
python voice_brief.py       # validates Meridian's RMA-line brief, renders the prompt skeleton
python call_evaluator.py    # QA over sample_calls/: 1 pass, 2 flagged — read the annotations
```

## The shape that matters

1. **The VOICE brief is the source of truth** — persona, objective, information
   contract, flow, escalation — in git, not in a platform text box. `voice_brief.py`
   validates the chapter's non-negotiables (disclosure, human-on-request,
   tool-gated confirmation, readbacks) and renders the prompt you paste anywhere.
2. **The QA rubric is the brief, checked.** `call_evaluator.py`'s checks map
   one-to-one onto the brief's sections. The string heuristics are deliberately
   naive teaching versions — production uses the pinned, caged LLM judge of
   Chapter 6 on the same rubric, over **every** transcript, every day.
3. **Latency is a ledger, not a vibe.** `turn_budget.py` shows why the frontier
   demo dragged, how streaming + model right-sizing fixed it, and why tuning
   *below* the window makes the agent interrupt callers.

## Adapt to your organization

Copy `MERIDIAN_RMA_LINE` in `voice_brief.py` and replace every field with your
own call's design; keep the validator honest (fix the brief, never the checks).
Measure real per-component latencies from platform logs and put them into
`turn_budget.py`'s component lists — p95, not just p50. Add your own golden-call
transcripts to `sample_calls/` as they accumulate: the failures are the roadmap.

Platform note: the chapter builds on a Vapi/Retell-class platform with Twilio-class
SIP trunking; these files deliberately contain nothing platform-specific, which is
the Chapter 13 portability discipline applied to voice.
