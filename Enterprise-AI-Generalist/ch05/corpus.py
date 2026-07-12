"""corpus.py — three fictional Meridian Systems policy documents, pre-chunked (book 5.11.2).

Stages 1–2 of the pipeline, done by hand so mini_rag.py stays readable.
Each chunk: text + the metadata that makes citations, filtering, and
permissions possible.

IMPORTANT: the Sev-1 runbook details are deliberately non-obvious (a
20-minute SLA, a "Conductor" role, a chat-first bridge). grounding_demo.py
depends on these differing from any plausible default a model would invent.
"""

CHUNKS = [
    # ------------------------- Travel & Expense Policy v4.2 -------------------
    {"doc": "TE-Policy", "version": "4.2", "section": "4.1",
     "text": "All business travel must be booked through the MeridianGo travel "
             "portal. Bookings made outside the portal are reimbursable only "
             "with written pre-approval from the traveler's cost-center "
             "director. Personal credit cards may be used only where the "
             "corporate card is not accepted."},

    {"doc": "TE-Policy", "version": "4.2", "section": "5.2",
     "text": "Long-haul flights: business class is permitted where scheduled "
             "flight time exceeds eight hours, subject to advance approval by "
             "the traveler's cost-center director. Approval must be recorded "
             "in MeridianGo before ticketing. Upgrades using personal miles "
             "are always permitted and require no approval."},

    {"doc": "TE-Policy", "version": "4.2", "section": "5.4",
     "text": "Approval workflow: requests submitted in MeridianGo route "
             "automatically to the cost-center director. If no action is "
             "taken within 48 hours, the request escalates to the director's "
             "delegate. Emergency travel may be booked first and approved "
             "retroactively within five business days."},

    {"doc": "TE-Policy", "version": "4.2", "section": "6.1",
     "text": "Receipts are required for all expenses of 25 USD or more, and "
             "for all lodging regardless of amount. Expense reports must be "
             "submitted within 30 days of trip completion. Reports submitted "
             "after 90 days are not reimbursable except with CFO approval."},

    {"doc": "TE-Policy", "version": "4.2", "section": "7.3",
     "text": "Per-diem rates follow the published Meridian schedule by "
             "country. Cities on the high-cost list receive a 20 percent "
             "uplift. Per-diem covers meals and incidentals; it is not paid "
             "for days when meals are provided by a conference or customer."},

    # ------------------------- Sev-1 Incident Runbook v3.1 --------------------
    # Deliberately non-default details: 20-minute SLA (not 15), "Incident
    # Conductor" role (not Incident Commander), chat-first bridge (not a call).
    {"doc": "Sev1-Runbook", "version": "3.1", "section": "2.1",
     "text": "Declaring a Sev-1: any engineer may declare a Sev-1 for a "
             "confirmed customer-facing outage by posting /sev1 in the "
             "#incident-desk channel. Do not phone the on-call directly; the "
             "bot pages them. The acknowledgment SLA for the on-call "
             "responder is 20 minutes."},

    {"doc": "Sev1-Runbook", "version": "3.1", "section": "2.2",
     "text": "Roles: every Sev-1 has an Incident Conductor (owns coordination "
             "and communications) and a Resolution Lead (owns the technical "
             "fix). The Conductor is the on-call engineering manager for the "
             "affected service group, not the responding engineer. One person "
             "must never hold both roles for more than 30 minutes."},

    {"doc": "Sev1-Runbook", "version": "3.1", "section": "2.4",
     "text": "Communication: the incident is run chat-first in the dedicated "
             "incident channel created by the bot. A voice bridge is opened "
             "only if the Conductor calls for one. Customer-facing status "
             "updates are posted by the Conductor every 60 minutes via the "
             "StatusHub tool; support agents must not improvise updates."},

    {"doc": "Sev1-Runbook", "version": "3.1", "section": "3.1",
     "text": "Escalation path: if the Resolution Lead requests additional "
             "hands, the Conductor pages the service group's secondary "
             "on-call. Vendor escalations (cloud provider, network carrier) "
             "are initiated only by the Conductor using the vendor-desk "
             "runbook, section 5. Executive notification is triggered "
             "automatically at the 2-hour mark by StatusHub."},

    # ------------------------- Remote Work Policy v2.0 ------------------------
    {"doc": "Remote-Policy", "version": "2.0", "section": "1.2",
     "text": "Eligibility: roles designated hybrid may work remotely up to "
             "three days per week, coordinated within the team. Fully remote "
             "arrangements require VP approval and are reviewed annually. "
             "Customer-facing lab roles are not eligible for remote work."},

    {"doc": "Remote-Policy", "version": "2.0", "section": "2.3",
     "text": "Cross-border remote work: working from a country other than "
             "your employment country is limited to 20 business days per "
             "calendar year and requires advance approval from HR and, for "
             "stays over 10 days, from Tax. Sanctioned-country work is "
             "prohibited without exception."},

    {"doc": "Remote-Policy", "version": "2.0", "section": "3.1",
     "text": "Equipment: Meridian provides one laptop and one monitor for "
             "remote setups. Additional equipment is purchased through the "
             "IT portal with manager approval up to 500 USD per year. "
             "Internet stipends are 40 USD per month for hybrid and fully "
             "remote employees, paid through payroll automatically."},
]
