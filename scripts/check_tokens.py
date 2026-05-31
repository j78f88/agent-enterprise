#!/usr/bin/env python3
"""Token-free guardrail for the deployed .github/ tree.

Scans .github/instructions/, .github/agents/, and .github/skills/ for
unresolved {{namespace.key}} tokens that should have been substituted by
init.py before deployment.

Exit codes:
  0 — no unresolved tokens found
  1 — one or more unresolved tokens found (with details printed to stdout)
  2 — bad CLI usage

Usage:
  python scripts/check_tokens.py [root_dir]

  root_dir: project root to scan (default: current working directory)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Stricter than init.py _TOKEN_RE: only matches real build tokens of the form
# {{namespace.key}} (at least one dot required).  Documentation examples like
# {{tokens}} (no dot) are intentional literals and must NOT be flagged.
# Group 1: optional leading backslash (escape marker — NOT flagged as unresolved).
# Group 2: token body in namespace.key form (lowercase letters, digits, underscores).
# Negative lookbehind for '$' excludes GitHub Actions ${{...}} syntax.
_TOKEN_RE = re.compile(r"(?<!\$)(\\?)\{\{([a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*)\}\}")

# Directories under project root to scan (relative paths).
_SCAN_DIRS = [
    ".github/instructions",
    ".github/agents",
    ".github/skills",
]


def check_file(path: Path) -> list[tuple[int, str]]:
    """Return a list of (line_number, token) for each unresolved token in path.

    Tokens preceded by a backslash (escaped literals like \\{{token}}) are
    intentional documentation literals and are NOT flagged.  GitHub Actions
    ${{...}} syntax is excluded by the regex negative lookbehind.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    findings: list[tuple[int, str]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for m in _TOKEN_RE.finditer(line):
            if m.group(1) != "\\":
                findings.append((lineno, "{{" + m.group(2) + "}}"))
    return findings


def check_tree(root: Path) -> dict[Path, list[tuple[int, str]]]:
    """Scan all markdown files in the deploy dirs and return per-file findings.

    Returns a mapping of {file_path: [(line_number, token), ...]} for every
    file that contains at least one unresolved token.  Files that are clean
    are not included in the returned dict.
    """
    all_findings: dict[Path, list[tuple[int, str]]] = {}

    for rel_dir in _SCAN_DIRS:
        scan_dir = root / rel_dir
        if not scan_dir.is_dir():
            continue
        for md_file in sorted(scan_dir.rglob("*.md")):
            findings = check_file(md_file)
            if findings:
                all_findings[md_file] = findings

    return all_findings


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) > 1:
        print("Usage: python scripts/check_tokens.py [root_dir]", file=sys.stderr)
        return 2

    root = Path(argv[0]) if argv else Path.cwd()

    findings = check_tree(root)

    if not findings:
        print("check-tokens: OK — no unresolved tokens found in .github/ tree.")
        return 0

    total = sum(len(v) for v in findings.values())
    print(f"check-tokens: FAIL — {total} unresolved token(s) found:")
    for file_path, file_findings in sorted(findings.items()):
        try:
            display_path = file_path.relative_to(root)
        except ValueError:
            display_path = file_path
        for lineno, token in file_findings:
            print(f"  {display_path}:{lineno}: {token}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
