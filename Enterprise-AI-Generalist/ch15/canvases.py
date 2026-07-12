"""canvases.py — Meridian's three sprint canvases (Chapter 15, section 15.9).

One promoted (Install Companion), one rejected at intake on data rights
(the error-log diagnoser — the Friday demo, properly canvassed), and one that
passes validation but dies at the review board on the commodity check
(the meeting summarizer). All composites, internally consistent with the chapter.
"""
from solution_canvas import SolutionCanvas, Evidence

INSTALL_COMPANION = SolutionCanvas(
    name="Install Companion",
    problem="Certified field installers struggle with on-site setup of Meridian controllers; "
            "installation questions dominate the support queue.",
    problem_evidence=[
        Evidence("340 support tickets/quarter tagged 'installation'",
                 "ticket query TCK-INSTALL-Q1 (support system)", "2026-04"),
        Evidence("'Every install I end up on hold with support for the wiring config' — installer",
                 "distributor forum thread /installers/8812", "2026-03"),
        Evidence("Installation is the support director's standing top-3 agenda item",
                 "support quarterly review minutes", "2026-04"),
    ],
    primary_user="The ~400 certified installers at Meridian's distribution partners "
                 "(recruitable via the certification mailing list)",
    journey_moment="On-site, controller unboxed, error code or wiring question in hand, "
                   "phone available, laptop usually not",
    data_sources=[
        {"source": "install manuals (knowledge platform corpus)", "owner": "product docs team",
         "rights": "internal-confirmed", "freshness": "current release cycle"},
        {"source": "error-code reference (knowledge platform corpus)", "owner": "engineering",
         "rights": "internal-confirmed", "freshness": "current"},
    ],
    model_task_profile="Retrieval-grounded Q&A, mobile chat surface, citations mandatory, "
                       "refusal on out-of-corpus (Ch. 5 grounding contract)",
    seed_eval="40 real installer questions from the ticket archive with support-verified answers "
              "(eval file ch15-install-eval-v1)",
    integrations=["knowledge platform API (read-only, existing Ch. 7 door)",
                  "MVP2: warranty registration (governed write door, to be built)"],
    risk_quadrant="assistive/recoverable for standard lines; safety-rated lines EXCLUDED from scope",
    risk_notes=["No procedure generation for safety-rated models — lookup-and-cite only",
                "Wrong-guidance risk mitigated by mandatory citations + escalation path"],
    value_metric="Deflect 25% of installation tickets (baseline 340/quarter)",
    sponsor="Support director (named in program records)",
    commodity_check="No vendor has Meridian's manuals, error codes, or installer context — "
                    "the differentiation IS the private corpus",
    thin_slice="MVP1: error-code lookup only, grounded in current manuals, for 20 pilot "
               "installers, measured by deflected installation tickets",
    kill_criteria=["seed eval <85% on ticket-derived questions",
                   "<50% of pilot installers active in week two",
                   "citation accuracy <95% in pilot transcripts"],
)

ERROR_LOG_DIAGNOSER = SolutionCanvas(
    name="Error-Log Diagnoser (the Friday demo, canvassed)",
    problem="Support engineers and customers manually interpret controller error logs; "
            "diagnosis is slow and inconsistent.",
    problem_evidence=[
        Evidence("Diagnosis time averages 22 minutes/ticket on log-attached tickets",
                 "ticket timing analysis, support ops", "2026-05"),
        Evidence("'Half my job is reading the same six stack traces' — support engineer",
                 "internal support team retro notes", "2026-05"),
    ],
    primary_user="Meridian support engineers (tier 1-2), ~35 people",
    journey_moment="Ticket open, customer log attached, before first response drafted",
    data_sources=[
        {"source": "parts catalog", "owner": "unclear (scraped from public site + ERP export)",
         "rights": "scraped", "freshness": "one-time export, already stale"},
        {"source": "error-code reference", "owner": "engineering",
         "rights": "internal-confirmed", "freshness": "current"},
    ],
    model_task_profile="Log classification + grounded parts suggestion",
    seed_eval="30 historical tickets with verified diagnoses (to be assembled)",
    integrations=["ERP parts read (NO governed door exists yet)", "ticket system write"],
    risk_quadrant="HIGH: wrong part suggestion on safety-rated controllers",
    risk_notes=["Safety-rated suggestion risk unresolved in demo",
                "Parts data provenance unknown"],
    value_metric="Cut diagnosis time 22 -> 8 minutes on log-attached tickets",
    sponsor="VP Sales (enthusiastic)",
    commodity_check="Generic log analyzers exist; the parts-suggestion coupling is ours",
    thin_slice="Diagnosis-only (no parts suggestion) on the error-code corpus",
    kill_criteria=["licensed parts feed cannot be negotiated within two quarters"],
)
# ^ REJECTED at intake: Box 3 'scraped' rights. The verdict in the chapter: rebuild
#   the data story first. The demo returns to the island; procurement negotiates the
#   licensed feed; the canvas re-enters intake in month eleven and ships (15.20).

MEETING_SUMMARIZER = SolutionCanvas(
    name="Sales Meeting-Notes Summarizer",
    problem="Sales team spends ~4 hrs/week/person writing up call notes and follow-ups.",
    problem_evidence=[
        Evidence("Time-tracking sample: 3.8 hrs/week median on notes",
                 "sales ops time study", "2026-04"),
        Evidence("'I do my CRM notes on Sunday nights' — account exec",
                 "sales team survey, verbatims", "2026-04"),
    ],
    primary_user="Meridian account executives (~60), heavy calendar, CRM-required notes",
    journey_moment="Within an hour after each customer call",
    data_sources=[
        {"source": "call recordings/transcripts", "owner": "sales ops",
         "rights": "internal-confirmed (consent flow exists)", "freshness": "real-time"},
    ],
    model_task_profile="Transcript summarization + CRM-field extraction",
    seed_eval="20 calls with AE-approved gold summaries",
    integrations=["CRM write (governed door exists)", "calendar read"],
    risk_quadrant="assistive/recoverable (AE reviews before save)",
    risk_notes=["PII in transcripts — retention rules apply"],
    value_metric="Reclaim 2+ hrs/week/AE (baseline 3.8)",
    sponsor="Sales operations lead",
    commodity_check="Three vendors sell exactly this; the enterprise suite includes one. "
                    "Nothing in our data or process differentiates a build.",
    thin_slice="One AE team, one week of calls, suite-vendor tool trialed FIRST",
    kill_criteria=["vendor trial meets the bar (then BUY, don't build)"],
)
# ^ PASSES validation — evidence, sponsor, eval all present. Dies at the review
#   board in eight minutes when the commodity check is read aloud: buying wins.
#   The validator filters pitches; the board kills evidenced-but-buyable ideas.
