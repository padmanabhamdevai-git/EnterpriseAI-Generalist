# Chapter 17 — Generative Media for the Enterprise

The governance layer of media generation — the part that survives every model
generation. **Everything runs standalone: no API keys, no image models.**

```
ch17/
├── asset_brief.py        # the 8-slot shot prompt + brand refs + negative list, validated (§17.5 Stage 1)
├── media_pipeline.py     # Stage 4's four checks (brand/rights/claims/disclosure) + the gate (§17.5)
├── likeness_register.py  # scoped, expiring, revocable consents — the bright line (§17.7.3)
└── README.md
```

## Run

```bash
python asset_brief.py        # the launch-kit hero brief passes; the rushed brief is rejected
python likeness_register.py  # in-scope / out-of-scope / revoked / expired / unregistered
python media_pipeline.py     # 3 assets: 1 clean, 1 brand fail, 1 claims fail (the cert-mark scenario)
```

## The shape that matters

1. **The brief is a prompt with a legal department.** References required (or the
   model invents your hardware), one style direction, negative list non-empty,
   ratios decided now. The validator's rejections teach while they filter.
2. **Four checks, then a named human.** Brand, rights, claims, disclosure —
   automated pre-annotation, human ruling (Ch. 16's topology, for pixels). The
   claims check is the one most teams forget an *image* can trip.
3. **The bright line:** not in the Likeness Register, not generated. Scope,
   expiry, revocation — and revocation must actually stop the pipeline.
4. **Nothing publishes ungated; nothing publishes unprovenanced.**

## Adapt to your organization

Replace `HERO_IMAGE`'s slots, references, and negative list with your product's;
extend `FORBIDDEN_MARKS` / `UNSAFE_DEPICTIONS` with your industry's claims
surface; wire `stage4` into your Ch. 10 workflow engine as the check step before
a human approval node. In production, the metadata fields these checks read
(`detected_marks`, `elements`, `depictions`) are produced by an OCR pass and a
vision-model judge (pinned and caged per Ch. 6) — see §17.12–17.13.
