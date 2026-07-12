"""diff_review.py — the Diff Review Protocol's mechanical checks
(Chapter 16, sections 16.7.1, 16.11.1).

A PRE-reviewer over unified diffs: it annotates; humans rule. Automates checks
1-5 (scope, dependencies, security seams, silent failures, test evidence);
prints checks 6-7 (simplification, the 2 a.m. comprehension bar) as reminders,
because they cannot be automated.

Runs standalone: no API keys.

    python diff_review.py sample_diffs/trouble.diff --scope "app/client.py,tests/test_client.py"
"""
import re
import sys
from pathlib import Path

SECRET_PATTERNS = [
    re.compile(r"""(api[_-]?key|secret|token|password)\s*[:=]\s*['"][A-Za-z0-9_\-]{12,}""", re.I),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]
SILENT_FAILURE_PATTERNS = [
    re.compile(r"except\s*(Exception)?\s*:\s*(pass|continue|\.\.\.)"),
    re.compile(r"except[^\n]*:\s*\n\s*(pass|return None)"),
]
KNOWN_STDLIB = {"os", "re", "sys", "json", "pathlib", "dataclasses", "typing",
                "collections", "itertools", "functools", "datetime", "math",
                "unittest", "logging", "abc", "enum", "time"}


def parse_diff(text: str) -> dict[str, list[str]]:
    """{filename: [added lines]} from a unified diff."""
    files: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
            files[current] = []
        elif current and line.startswith("+") and not line.startswith("+++"):
            files[current].append(line[1:])
    return files


def check_scope(files: dict, declared: set[str]) -> list[str]:
    return [f"SCOPE: '{f}' modified but not in declared scope — split it out or revert it "
            "(however correct it looks; hidden changes ride unrelated reviews)"
            for f in sorted(set(files) - declared)]


def check_dependencies(files: dict) -> list[str]:
    findings = []
    for f, lines in files.items():
        for l in lines:
            m = re.match(r"^\s*(?:import|from)\s+([A-Za-z_][A-Za-z0-9_]*)", l)
            if m and m.group(1) not in KNOWN_STDLIB:
                findings.append(f"DEPS: new import '{m.group(1)}' in {f} — verify it EXISTS on the "
                                "official registry (hallucinated packages are an attack surface), "
                                "is allow-listed, and is actually needed")
        if any(name in f for name in ("requirements", "pyproject", "package.json")):
            for l in lines:
                if l.strip() and not l.strip().startswith("#"):
                    findings.append(f"DEPS: dependency file change in {f}: '{l.strip()}' — "
                                    "a supply-chain decision; treat as its own review item")
    return findings


def check_secrets(files: dict) -> list[str]:
    findings = []
    for f, lines in files.items():
        for l in lines:
            for pat in SECRET_PATTERNS:
                if pat.search(l):
                    findings.append(f"SECRET: credential-shaped content in {f}: "
                                    f"'{l.strip()[:60]}...' — env files, never source")
    return findings


def check_silent_failures(files: dict) -> list[str]:
    findings = []
    for f, lines in files.items():
        blob = "\n".join(lines)
        if any(pat.search(blob) for pat in SILENT_FAILURE_PATTERNS):
            findings.append(f"SILENT: swallowed-exception pattern in {f} — the classic AI-diff "
                            "signature; error paths are where plausible and correct diverge")
    return findings


def check_test_evidence(files: dict) -> list[str]:
    src = [f for f in files if "test" not in f.lower() and f.endswith((".py", ".ts", ".js"))]
    tests = [f for f in files if "test" in f.lower()]
    if src and not tests:
        return [f"TESTS: source changes in {len(src)} file(s) with NO test changes — "
                "what contract was this diff steered by?"]
    findings = []
    assert_stmt = re.compile(r"^\s*assert\b")           # the STATEMENT, not the word in a comment
    for f in tests:
        lines = files[f]
        if any("def test" in l for l in lines) and not any(assert_stmt.match(l) for l in lines):
            findings.append(f"TESTS: '{f}' adds tests with no assertions — coverage theater; "
                            "mutate the code and watch nothing fail")
    return findings


HUMAN_CHECKS = """
  human checks (cannot be automated — the tool only reminds):
    [6] SIMPLIFY: ask the agent to remove abstraction with only one user; review what it deletes
    [7] THE 2 A.M. BAR: could you maintain this without the agent? If no — it doesn't merge.
        The accept key is a signature; you own every line you take.
"""


def review(diff_path: Path, declared_scope: set[str]) -> int:
    files = parse_diff(diff_path.read_text(encoding="utf-8"))
    print("=" * 78)
    print(f"PRE-REVIEW: {diff_path.name}   (declared scope: {', '.join(sorted(declared_scope))})")
    print("-" * 78)
    findings = (check_scope(files, declared_scope) + check_dependencies(files)
                + check_secrets(files) + check_silent_failures(files)
                + check_test_evidence(files))
    if findings:
        for x in findings:
            print(f"  [!] {x}")
    else:
        print("  [ok] no mechanical findings (checks 1-5)")
    print(HUMAN_CHECKS)
    print(f"  => {len(findings)} finding(s). This annotates the review; it never replaces it.\n")
    return len(findings)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        path = Path(args[0])
        scope = set()
        if "--scope" in args:
            scope = set(s.strip() for s in args[args.index("--scope") + 1].split(","))
        review(path, scope)
    else:
        base = Path(__file__).parent / "sample_diffs"
        scope = {"app/client.py", "tests/test_client.py"}
        print("THE DIFF REVIEW PROTOCOL — mechanical pre-pass (section 16.7.1)\n")
        clean = review(base / "clean.diff", scope)
        trouble = review(base / "trouble.diff", scope)
        print(f"clean.diff: {clean} findings — trouble.diff: {trouble} findings.")
        print("The planted problems in trouble.diff: scope creep, unknown dependency,")
        print("hardcoded key, swallowed exception, assertion-free test. Find them all above.")
