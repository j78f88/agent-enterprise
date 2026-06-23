#!/usr/bin/env python3
"""Public-repository boundary guardrail.

This check blocks portable product docs from absorbing operator-local state:
machine-specific absolute paths, private risk notes, and live environment
handling. It intentionally uses generic patterns so the public repo does not
need to name any adopter's private systems.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".json", ".toml", ".txt"}
_EXCLUDED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "resolved",
    "venv",
}
_EXCLUDED_PREFIXES = ("docs/archive/", "sprints/")
_EXCLUDED_FILES = {"pytest_output.txt"}

_RULES: list[tuple[str, re.Pattern[str]]] = [
    (
        "machine-local-posix-path",
        re.compile(r"/(?:home|Users)/[A-Za-z0-9._-]+/(?:apps|src|work|projects|private|tmp|var|\.config|\.cache)/"),
    ),
    (
        "machine-local-windows-path",
        re.compile(r"\b[A-Za-z]:\\(?:Users|VS|work|projects|private|tmp|Cowork|Code)\\", re.IGNORECASE),
    ),
    (
        "private-env-handling",
        re.compile(r"\blive\s+\.env\b|\.env\s+symlink", re.IGNORECASE),
    ),
    (
        "private-risk-acceptance-note",
        re.compile("key rotation " + "deferred|accepted-" + "risk override", re.IGNORECASE),
    ),
]


def _is_scanned(path: Path, root: Path) -> bool:
    rel = path.relative_to(root).as_posix()
    if any(part in _EXCLUDED_PARTS for part in path.relative_to(root).parts):
        return False
    if rel in _EXCLUDED_FILES:
        return False
    if rel.startswith(_EXCLUDED_PREFIXES):
        return False
    return path.is_file() and path.suffix in _TEXT_SUFFIXES


def check_file(path: Path) -> list[tuple[int, str, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    findings: list[tuple[int, str, str]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for rule_name, pattern in _RULES:
            if pattern.search(line):
                findings.append((lineno, rule_name, line.strip()[:160]))
    return findings


def check_tree(root: Path) -> dict[Path, list[tuple[int, str, str]]]:
    findings: dict[Path, list[tuple[int, str, str]]] = {}
    for path in sorted(root.rglob("*")):
        if not _is_scanned(path, root):
            continue
        file_findings = check_file(path)
        if file_findings:
            findings[path] = file_findings
    return findings


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) > 1:
        print("Usage: python scripts/check_public_boundary.py [root_dir]", file=sys.stderr)
        return 2

    root = Path(argv[0]) if argv else Path.cwd()
    findings = check_tree(root)
    if not findings:
        print("check-public-boundary: OK — no private boundary leaks found.")
        return 0

    total = sum(len(items) for items in findings.values())
    print(f"check-public-boundary: FAIL — {total} private boundary finding(s):")
    for path, items in sorted(findings.items()):
        display = path.relative_to(root)
        for lineno, rule_name, excerpt in items:
            print(f"  {display}:{lineno}: {rule_name}: {excerpt}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
