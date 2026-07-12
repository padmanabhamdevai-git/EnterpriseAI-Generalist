# Chapter 19 — Security, Governance, and Compliance for Enterprise AI

The governance model, executable — the answer to "who approves what, on what
basis, written where." **Everything runs standalone: no API keys.**

```
ch19/
├── threat_ledger.py   # the 5 threat families + the lethal-trifecta check over an agent spec (§19.5.1)
├── risk_tiering.py    # the governance model's Element 1: rubric -> tier -> gates + evidence (§19.8)
├── arb_package.py     # the evidence package: "no gate without its evidence", enforced (§19.10)
└── README.md
```

## Run

```bash
python threat_ledger.py   # quoting assistant before/after the leg removal; the shadow pilot
python risk_tiering.py    # tiers five systems, incl. the surprising-high and surprising-low
python arb_package.py     # assembles the elevated package; the board won't convene without the threat model
```

## The shape that matters

1. **The lethal trifecta is the check to run first.** Confidential access +
   untrusted content + exfiltration in one agent = one poisoned input from
   disaster. The quoting assistant's v0→v1 removes the exfiltration leg *before
   build* — the entire argument for a design gate.
2. **Tier by factors, not by vibe.** The rubric's surprises — the "harmless"
   auto-responder tiering elevated, the "scary" code explainer tiering minimal —
   are the point: reversibility, data sensitivity, autonomy, consequence, and
   regulatory trigger decide the tier, and the tier decides the gates.
3. **No gate without its evidence.** `arb_package.py` refuses to convene the
   board on an incomplete package — the governance model's central rule, in code,
   and the fix for "the architect decides."

## Adapt to your organization

Replace the agent specs in `threat_ledger.py` and the profiles in `risk_tiering.py`
with your systems; tune the tiering weights and the per-tier evidence to your
risk appetite and regulator; wire `arb_package.py`'s completeness gate into CI
(§19.13) so a system cannot reach production without its tier's evidence present.
Add an override log to the tiering (Exercise / prompt pack) so any manual
tier change is auditable — silent overrides are "the architect decides" with
extra steps.
