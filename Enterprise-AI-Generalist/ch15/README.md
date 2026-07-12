# Chapter 15 — From Idea to Application: AI-Native Product Development

The specification-and-governance layer of AI product work — the part that survives
every tool churn. **Everything runs standalone: no API keys.**

```
ch15/
├── solution_canvas.py   # the Canvas as an intake bar: 7 boxes, evidence-required, kill criteria (§15.5)
├── canvases.py          # Meridian's three sprint canvases: promoted / rejected / board-killed (§15.9)
├── promotion_gates.py   # Demo/Pilot/Production states + Gate 1 and Gate 2 as checklists (§15.7)
├── prd_render.py        # canvas -> PRD brief, non-goals rendered FIRST (§15.9 step 4)
└── README.md
```

## Run

```bash
python solution_canvas.py   # validates the three canvases; the diagnoser fails on data rights
python promotion_gates.py   # replays the Install Companion: demo -> pilot -> production
python prd_render.py        # renders the promoted canvas to the builder brief
```

## The shape that matters

1. **Evidence or it's a pitch.** The validator rejects canvases without dated,
   sourced evidence, a named sponsor, a seed eval, a thin slice, and kill criteria.
   Its error strings are deliberately the chapter's aphorisms — the intake bar
   teaches while it filters.
2. **The validator filters pitches; the board kills buyable ideas.** The meeting
   summarizer *passes* validation and dies at review when its commodity-check
   answer is read aloud. Both layers are the design.
3. **States, not vibes.** Demo, Pilot, Production each have entry criteria;
   `promotion_gates.py` prints exactly what blocks each crossing — and the
   standing NEVER-SHIPS list belongs on the wall.
4. **Non-goals first.** `prd_render.py` puts what the builder must NOT build at
   the top of the brief, because builder models fill every unspecified gap with
   the most plausible feature — which is exactly what your Risk box excluded.

## Adapt to your organization

Copy a canvas from `canvases.py` and replace every field with your own idea's
facts; let the validator argue with you. Wire `promotion_gates.py`'s criteria
into your review-board checklist verbatim, then edit — the edits are your
governance design. Render your PRD and hand it to an app-builder or agentic IDE
(Chapter 16) under the island rules printed in section 8 of the output.
