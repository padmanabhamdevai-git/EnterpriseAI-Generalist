"""prompt_template.py — prompts as versioned templates, not strings (book 3.11.1).

The pattern that scales: a template with declared variables, validated at
render time, split into system (durable) and user (per-request) parts.
"""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PromptTemplate:
    """A versioned prompt template with a declared variable schema."""

    name: str
    version: str
    system: str          # durable: role, constraints, output contract
    user: str            # per-request: the {{variables}} live here
    description: str = ""

    @property
    def variables(self) -> set[str]:
        """All {{variable}} names declared in the template."""
        return set(re.findall(r"\{\{(\w+)\}\}", self.system + self.user))

    def render(self, **values) -> tuple[str, str]:
        """Fill variables; fail loudly on missing or unexpected ones."""
        missing = self.variables - values.keys()
        extra = values.keys() - self.variables
        if missing:
            raise ValueError(f"{self.name}@{self.version}: missing {sorted(missing)}")
        if extra:
            raise ValueError(f"{self.name}@{self.version}: unexpected {sorted(extra)}")

        def fill(text: str) -> str:
            return re.sub(r"\{\{(\w+)\}\}", lambda m: str(values[m.group(1)]), text)

        return fill(self.system), fill(self.user)


# --- The Meridian returns email, as an artifact -------------------------------
RETURNS_STATUS_EMAIL = PromptTemplate(
    name="returns/status-email",
    version="1.0.0",
    description="Customer-facing return status update. Copilot flow: agent reviews.",
    system=(
        "You are a returns specialist at Meridian Systems writing to a customer.\n"
        "Voice: plain, warm, specific, never gushing.\n"
        "Hard rules:\n"
        "- Never promise a delivery date; say tracking will follow.\n"
        "- Never offer a refund; this is a replacement flow.\n"
        "- Apologize at most once. Keep under 150 words.\n"
        "Output contract: a subject line on the first line, then the email body:\n"
        "greeting with first name, three short paragraphs (what we received and "
        "found; what happens next; one-line closing with {{support_link}}). "
        "No signature block."
    ),
    user=(
        "Write the status-update email for this return:\n"
        "- Customer: {{customer_name}}\n"
        "- Order: {{order_id}}, {{product}}\n"
        "- Return received: {{received_date}}. Inspection: {{inspection_result}}.\n"
        "- Replacement ships {{ship_date}} from {{warehouse}}."
    ),
)


if __name__ == "__main__":
    system, user = RETURNS_STATUS_EMAIL.render(
        customer_name="Dana Whitfield",
        order_id="MS-88213",
        product="ThermaSense 4 controller",
        received_date="June 24",
        inspection_result="confirmed defect (sensor drift)",
        ship_date="June 30",
        warehouse="Dallas",
        support_link="meridian.example/support",
    )
    print("--- SYSTEM ---\n" + system)
    print("\n--- USER ---\n" + user)

    from ai_client import ask

    resp = ask(user, system=system, provider="anthropic", temperature=0.4)
    print(f"\n--- DRAFT ({resp.input_tokens}+{resp.output_tokens} tokens) ---")
    print(resp.text)
