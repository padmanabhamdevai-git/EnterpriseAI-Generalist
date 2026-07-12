"""media_pipeline.py — the Governed Media Pipeline's Stage 4 checks and gate
(Chapter 17, sections 17.5, 17.11.2).

brief -> generate -> select -> CHECK (brand/rights/claims/disclosure) -> APPROVE
-> publish (DAM) -> provenance. The checks pre-annotate; the named human rules —
Chapter 16's topology, for pixels. Nothing publishes ungated; nothing publishes
unprovenanced.

Runs standalone: no API keys, no image models — assets are metadata records,
which is exactly what the governance layer sees.

    python media_pipeline.py
"""
from asset_brief import AssetBrief, HERO_IMAGE
from likeness_register import REGISTER

FORBIDDEN_MARKS = {"CE-style mark", "UL-style mark", "safety certification badge"}
UNSAFE_DEPICTIONS = {"bare hands on live wiring", "missing safety gloves", "blocked fire exit"}


def check_brand(asset: dict, brief: AssetBrief) -> tuple[bool, str]:
    missing = [e for e in brief.mandatory_elements if e not in asset.get("elements", [])]
    return (not missing,
            "brand: mandatory elements present" if not missing
            else f"brand: MISSING {missing} — the brand kit's rules are not suggestions")


def check_rights(asset: dict, brief: AssetBrief, register) -> tuple[bool, str]:
    if asset["generated_by"] not in brief.sanctioned_tools:
        return False, (f"rights: '{asset['generated_by']}' not sanctioned for this asset class "
                       "— personal seats are how product IP leaks")
    for lid in asset.get("likenesses", []):
        ok, why = register.consent_valid(lid, use=asset["intended_use"])
        if not ok:
            return False, f"rights: likeness {lid} — {why}"
    return True, "rights: tool sanctioned; likeness consents current"


def check_claims(asset: dict, brief: AssetBrief) -> tuple[bool, str]:
    """The gate most teams forget an IMAGE can trip: anything a regulator could
    read off the pixels — marks, safety depictions, implied outcomes."""
    hits = [m for m in asset.get("detected_marks", []) if m in FORBIDDEN_MARKS]
    unsafe = [d for d in asset.get("depictions", []) if d in UNSAFE_DEPICTIONS]
    problems = hits + unsafe
    return (not problems,
            "claims: clean" if not problems
            else f"claims: {problems} — a compliance violation renders in seconds; "
                 "this check is the pipeline argument in one line")


def check_disclosure(asset: dict, brief: AssetBrief) -> tuple[bool, str]:
    if brief.disclosure_required and not asset.get("content_credentials"):
        return False, "disclosure: no content credentials — nothing publishes unprovenanced"
    return True, "disclosure: credentials embedded"


def stage4(asset: dict, brief: AssetBrief, register) -> bool:
    print("-" * 74)
    print(f"ASSET: {asset['name']}   (brief: {brief.name})")
    results = [check_brand(asset, brief), check_rights(asset, brief, register),
               check_claims(asset, brief), check_disclosure(asset, brief)]
    ok = all(r[0] for r in results)
    for passed, msg in results:
        print(f"  [{'pass' if passed else 'FAIL'}] {msg}")
    print(f"  => {'TO THE APPROVAL GATE (named human, recorded)' if ok else 'REJECTED — back to Stage 1 with the reason'}")
    return ok


# ---------------------------------------------------------------------------
# Three sample assets from the launch kit run (section 17.9, day 5).
# ---------------------------------------------------------------------------
ASSETS = [
    {   # the clean survivor
        "name": "hero-16x9-v04 (curated survivor)",
        "generated_by": "imggen-enterprise-A",
        "intended_use": "distributor-portal",
        "elements": ["M-340 port layout per reference", "brand palette"],
        "detected_marks": [], "depictions": ["gloved hands on cabinet"],
        "likenesses": [], "content_credentials": "c2pa:embedded",
    },
    {   # palette drift — brand check catches it
        "name": "social-1x1-v02 (palette drift)",
        "generated_by": "imggen-enterprise-A",
        "intended_use": "social",
        "elements": ["M-340 port layout per reference"],       # brand palette missing
        "detected_marks": [], "depictions": [],
        "likenesses": [], "content_credentials": "c2pa:embedded",
    },
    {   # THE one — the model "enhanced" the label with a cert mark (17.9 step 4)
        "name": "hero-16x9-v07 (the enhanced label)",
        "generated_by": "imggen-enterprise-A",
        "intended_use": "paid-display",
        "elements": ["M-340 port layout per reference", "brand palette"],
        "detected_marks": ["CE-style mark"],
        "depictions": [],
        "likenesses": [], "content_credentials": "c2pa:embedded",
    },
]


if __name__ == "__main__":
    print("THE GOVERNED MEDIA PIPELINE — Stage 4 checks (section 17.5)")
    print("Checks pre-annotate; the named human rules. Nothing publishes ungated.\n")
    passed = sum(stage4(a, HERO_IMAGE, REGISTER) for a in ASSETS)
    print("=" * 74)
    print(f"{passed}/{len(ASSETS)} assets forwarded to the approval gate.")
    print("The rejected cert-mark asset goes three places: the reject pile, the")
    print("negative list (sharpened: mask labels in reference images), and the")
    print("all-hands slide — a violation caught in seconds is the whole argument.")
