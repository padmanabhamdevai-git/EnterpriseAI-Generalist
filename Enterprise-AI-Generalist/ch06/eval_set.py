"""eval_set.py — labeled questions over the ch05 corpus (book 6.11.3).

Each case: a real-shaped question, the chunk(s) that answer it (labeled by
doc + section, resolved to chunk IDs at runtime), and absent=True for the
refusal traps.

Fifty of these over YOUR corpus is one afternoon and prices every future
change. These twelve over the seed corpus demonstrate the machinery.
"""

EVAL_SET = [
    {"question": "Can I book business class on a flight to Singapore?",
     "relevant": [("TE-Policy", "5.2")], "absent": False},

    {"question": "Who approves long-haul business class travel?",
     "relevant": [("TE-Policy", "5.2")], "absent": False},

    {"question": "What happens if my travel approval request gets no response for two days?",
     "relevant": [("TE-Policy", "5.4")], "absent": False},

    {"question": "Do I need a receipt for a 20 dollar taxi ride?",
     "relevant": [("TE-Policy", "6.1")], "absent": False},

    {"question": "How do I declare a Sev-1 incident?",
     "relevant": [("Sev1-Runbook", "2.1")], "absent": False},

    {"question": "What is the acknowledgment SLA for the on-call responder?",
     "relevant": [("Sev1-Runbook", "2.1")], "absent": False},

    {"question": "Who opens the voice bridge during an incident?",
     "relevant": [("Sev1-Runbook", "2.4")], "absent": False},

    {"question": "Who is allowed to escalate to the cloud provider during a Sev-1?",
     "relevant": [("Sev1-Runbook", "3.1")], "absent": False},

    {"question": "How many days per year can I work from another country?",
     "relevant": [("Remote-Policy", "2.3")], "absent": False},

    {"question": "What internet stipend do hybrid employees get?",
     "relevant": [("Remote-Policy", "3.1")], "absent": False},

    # Absent questions — the refusal traps (adjacent but uncovered):
    {"question": "What is the per-diem rate for Antarctica field work?",
     "relevant": [], "absent": True},

    {"question": "What is Meridian's policy on bringing dogs to the office?",
     "relevant": [], "absent": True},
]
