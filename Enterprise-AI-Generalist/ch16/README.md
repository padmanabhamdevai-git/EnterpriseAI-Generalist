# Chapter 16 — Agentic Development with Cursor and Modern IDEs

The discipline layer of agentic coding — the part that makes agent-mode speed
survive review. **Everything runs standalone: no API keys.**

```
ch16/
├── rules/
│   ├── org-rules.md      # Layer 1: security, deps, licensing, provenance, stop conditions
│   └── repo-rules.md     # Layer 2: this estate's patterns (ch09 shapes, test rules, frozen zones)
├── diff_review.py        # the Diff Review Protocol's mechanical checks (1-5) as a pre-reviewer
├── sample_diffs/
│   ├── clean.diff        # a well-behaved slice: scoped, tested, env-driven config
│   └── trouble.diff      # five planted AI-diff failures — find them all
└── README.md
```

## Run

```bash
python diff_review.py     # reviews both samples with the default scope
python diff_review.py sample_diffs/trouble.diff --scope "app/client.py,tests/test_client.py"
```

`trouble.diff`'s planted findings: out-of-scope edit (`app/utils.py`), unknown
dependency (`retryflowx` — verify it even exists), hardcoded API key, swallowed
exception, and an assertion-free test. The tool catches the mechanical five;
checks 6 (simplification) and 7 (the 2 a.m. comprehension bar) are printed as
reminders because they are yours.

## The shape that matters

1. **The pre-reviewer annotates; humans rule.** Wire it into CI as a PR comment,
   never as an auto-approve.
2. **The rules are templates to edit, not gospel to adopt.** Their value is the
   structure — and the stop conditions ("STOP and propose it — do not import and
   proceed"), which convert agent eagerness into a request queue.
3. **Rules are code:** version them, sharpen them within the hour of every
   repeated agent mistake, and occasionally test them by asking the agent to
   violate one.

## Adapt to your organization

Copy `rules/` into your repos (Cursor: `.cursor/rules/`; Claude Code: fold into
`CLAUDE.md`; other tools: their rules location). Replace the repo-rules content
with YOUR architecture, test conventions, frozen zones, and vocabulary. Extend
`diff_review.py`'s `KNOWN_STDLIB`/patterns for your stack, and point its
dependency check at your real allow-list.
