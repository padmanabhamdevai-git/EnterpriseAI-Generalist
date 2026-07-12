"""eval_notes.py — the 12-note evaluation set for the plane comparison (book 4.11.3).

Each entry: an inspection note plus the expected key facts. Three traps:
  #7  liquid damage present alongside a confirmed defect (rule 3 must win)
  #9  defect reported by customer but NOT bench-confirmed
  #11 purchase outside the coverage window (date arithmetic)
"""

EVAL_NOTES = [
    # (note_text, expected: dict of the fields worth scoring)
    ("Unit MS-88213 (ThermaSense 4) received 24 June. Bench test confirms sensor "
     "drift of 3.1C above tolerance; board shows no liquid damage. Purchased "
     "11 Feb 2026, 24-month coverage. Recommend sensor assembly TS4-SA-011.",
     {"defect_category": "sensor_drift", "defect_confirmed": True}),

    ("Unit MS-90144 (FlowGuard 2) received 2 May. Bench confirms main board "
     "failure, error code E44 reproducible. Purchased 3 Jan 2025, 24-month "
     "coverage. Recommend board FG2-MB-003.",
     {"defect_category": "board_failure", "defect_confirmed": True}),

    ("Unit MS-77020 received 12 June. No fault found across 48h soak test. "
     "Customer reported intermittent shutdowns. Purchased 9 Sep 2025, 24-month "
     "coverage.",
     {"defect_category": "no_defect_found", "defect_confirmed": False}),

    ("Unit MS-81555 (ThermaSense 4) received 30 April. Bench confirms sensor "
     "drift 2.2C over tolerance. Purchased 15 Mar 2026, 24-month coverage. "
     "Recommend TS4-SA-011.",
     {"defect_category": "sensor_drift", "defect_confirmed": True}),

    ("Unit MS-66301 received 18 May. Corrosion on connector pins; moisture "
     "ingress evident under board coating. Purchased 20 Nov 2025, 24-month "
     "coverage.",
     {"defect_category": "liquid_damage", "defect_confirmed": True}),

    ("Unit MS-92808 (FlowGuard 2) received 6 June. Bench reproduces valve "
     "actuator fault. Purchased 28 Feb 2026, 24-month coverage. Recommend "
     "FG2-VA-007.",
     {"defect_category": "board_failure", "defect_confirmed": True}),

    # TRAP 7: confirmed defect AND liquid damage — rule 3 must void coverage.
    ("Unit MS-70443 received 9 June. Bench confirms sensor drift 4.0C over "
     "tolerance. Note: board shows clear liquid damage staining; customer "
     "mentions a kitchen installation. Purchased 5 Apr 2026, 24-month coverage.",
     {"defect_category": "liquid_damage", "defect_confirmed": True}),

    ("Unit MS-85172 received 21 May. Display flicker confirmed on bench, "
     "traced to ribbon connector. Purchased 30 Dec 2025, 24-month coverage. "
     "Recommend TS4-RC-002.",
     {"defect_category": "other", "defect_confirmed": True}),

    # TRAP 9: customer-reported only; bench did NOT confirm.
    ("Unit MS-79910 received 15 June. Customer reports readings freeze daily. "
     "Bench could not reproduce across 72h; all telemetry nominal. Purchased "
     "7 Oct 2025, 24-month coverage.",
     {"defect_category": "no_defect_found", "defect_confirmed": False}),

    ("Unit MS-88427 (ThermaSense 4) received 1 June. Bench confirms sensor "
     "drift 2.9C over tolerance. Purchased 19 May 2026, 24-month coverage. "
     "Recommend TS4-SA-011.",
     {"defect_category": "sensor_drift", "defect_confirmed": True}),

    # TRAP 11: purchase date far outside coverage window (assessment must catch).
    ("Unit MS-51209 received 10 June. Bench confirms board failure, error E12. "
     "Purchased 2 Mar 2023, standard 24-month coverage. Recommend FG1-MB-009.",
     {"defect_category": "board_failure", "defect_confirmed": True}),

    ("Unit MS-93361 received 25 June. Bench confirms intermittent sensor "
     "dropout under thermal cycling. Purchased 14 Jan 2026, 24-month coverage. "
     "Recommend TS4-SA-011.",
     {"defect_category": "sensor_drift", "defect_confirmed": True}),
]
