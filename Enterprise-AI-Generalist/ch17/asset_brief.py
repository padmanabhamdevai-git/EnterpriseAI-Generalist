"""asset_brief.py — the asset brief: a prompt with a legal department
(Chapter 17, sections 17.5 Stage 1, 17.11.1).

The eight-slot shot prompt (subject/action/environment/atmosphere/camera/lens/
lighting/style) plus the enterprise additions: brand references, mandatory
elements, the negative list, rights constraints, and channel formats decided
up front. Briefs live in the registry like prompts do, because they ARE prompts.

Runs standalone: no API keys, no image models.

    python asset_brief.py
"""
from dataclasses import dataclass, field

SLOTS = ("subject", "action", "environment", "atmosphere", "camera", "lens", "lighting", "style")


@dataclass
class AssetBrief:
    name: str
    intent: str                            # campaign / channel / audience, one line
    channel_formats: list[str]             # ratios decided NOW, not at crop time
    slots: dict[str, str]                  # the 8-slot shot prompt (fill what the brief cares about)
    brand_references: list[str]            # approved product images/renders — REQUIRED
    mandatory_elements: list[str]          # e.g., "safety gloves in any hands-on depiction"
    negative_list: list[str]               # never: invented hardware, cert marks, competitor dress
    sanctioned_tools: list[str]            # which register entries may generate this asset class
    likeness_ids: list[str] = field(default_factory=list)   # Likeness Register IDs, if any
    disclosure_required: bool = True

    def validate(self) -> list[str]:
        p = []
        unknown = set(self.slots) - set(SLOTS)
        if unknown:
            p.append(f"unknown slots {sorted(unknown)} — the eight slots are {SLOTS}")
        if not self.brand_references:
            p.append("no brand references — generation without references invents hardware")
        if not self.negative_list:
            p.append("empty negative list — the launch-folder failures are not encoded")
        style = self.slots.get("style", "")
        if style.count(",") >= 3:
            p.append(f"style soup: '{style}' — pick ONE direction; a soup averages everything")
        if not self.channel_formats:
            p.append("no channel formats — 'we'll crop later' puts the key feature outside the frame")
        if not self.sanctioned_tools:
            p.append("no sanctioned tools named — personal seats on consumer tiers are how product IP leaks")
        return p

    def render_prompt(self) -> str:
        parts = [self.slots[s] for s in SLOTS if self.slots.get(s)]
        return (", ".join(parts)
                + " | reference images attached: " + "; ".join(self.brand_references)
                + " | never: " + "; ".join(self.negative_list))


# ---------------------------------------------------------------------------
# The Install Companion launch kit's hero-image brief (section 17.9).
# ---------------------------------------------------------------------------
HERO_IMAGE = AssetBrief(
    name="M-340 hero image",
    intent="Install Companion launch — paid display + product page; distributor audience",
    channel_formats=["16:9 (web hero)", "1:1 (social)", "4:5 (poster)"],
    slots={
        "subject": "the Meridian M-340 controller, front panel visible, label area NEUTRAL",
        "action": "mounted in a clean industrial control cabinet",
        "environment": "modern light-industrial facility, shallow background",
        "atmosphere": "confident, precise, uncluttered",
        "camera": "full-frame product photography rig",
        "lens": "85mm, shallow depth of field",
        "lighting": "clean studio softbox, subtle rim light",
        "style": "photorealistic product photography",
    },
    brand_references=["ref/m340-front-approved.jpg", "ref/m340-render-3q.png",
                      "ref/brand-palette-tokens.json"],
    mandatory_elements=["M-340 port layout per reference", "brand palette"],
    negative_list=[
        "invented hardware or port layouts — composite from approved references only",
        "certification or compliance marks of any kind (labels come from approved photography)",
        "competitor trade dress",
        "hands without safety gloves in any hands-on depiction",
        "readable text not present in references",
    ],
    sanctioned_tools=["imggen-enterprise-A", "aggregator-workspace-B"],
)

# A deliberately broken brief, for the validator to catch.
RUSHED_SOCIAL = AssetBrief(
    name="social teaser (rushed)",
    intent="quick teaser for the launch week",
    channel_formats=[],
    slots={"subject": "our controller looking cool",
           "style": "realistic, cartoon, cinematic, anime, photorealistic"},
    brand_references=[],
    mandatory_elements=[],
    negative_list=[],
    sanctioned_tools=[],
)


if __name__ == "__main__":
    print("THE ASSET BRIEF (section 17.5, Stage 1)\n")
    for brief in (HERO_IMAGE, RUSHED_SOCIAL):
        problems = brief.validate()
        print("=" * 74)
        print(f"BRIEF: {brief.name} — {brief.intent}")
        if problems:
            for x in problems:
                print(f"  [REJECTED] {x}")
            print("  => brief rejected at intake — a rushed brief is how fiction ships")
        else:
            print("  [ok] brief passes; rendered generation prompt:")
            print(f"  {brief.render_prompt()}")
        print()
