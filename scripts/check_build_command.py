#!/usr/bin/env python3
"""Build-command canonical-config guardrail.

Scans Markdown files in deployable-artifact directories for lines that invoke
  python init.py --config <path>
where <path> is NOT the canonical config file.

The canonical build command is:
  python init.py --config config/project.config.example.yml

Only the following directories are scanned (skills/, instructions/, agents/,
.github/).  User-facing docs and examples in other directories (docs/,
README.md, CHANGELOG.md, etc.) may reference private configs by design and
are intentionally excluded.

Exit codes:
  0 — no violations found
  1 — one or more violations found (details printed to stdout)
  2 — bad CLI usage

Usage:
  python scripts/check_build_command.py [root_dir]

  root_dir: project root to scan (default: current working directory)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_CANONICAL_CONFIG = "config/project.config.example.yml"

# Matches: python init.py ... --config <path>
# Captures the config path argument (non-whitespace run after --config).
_BUILD_CMD_RE = re.compile(r"python\s+init\.py\b.*?--config\s+(\S+)")

# Directories (relative to repo root) that are scanned for build-command
# references.  Everything outside these directories is intentionally ignored —
# user-facing docs and examples may reference private configs by design.
_SCAN_DIRS: list[tuple[str, ...]] = [
    ("skills",),
    ("instructions",),
    ("agents",),
    (".github",),
]

# Sub-paths under .github/ that are excluded from scanning.  These are
# user-facing GitHub collaboration templates and CI workflow config that may
# reference project-specific configs by design and are not deployable skill
# artifacts.
_GITHUB_EXCLUDED_SUBPATHS: frozenset[str] = frozenset({
    ".github/ISSUE_TEMPLATE",
    ".github/PULL_REQUEST_TEMPLATE",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/workflows",
})


def _is_github_excluded(path: Path, root: Path) -> bool:
    """Return True if path falls under a GitHub-excluded sub-path."""
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        return False
    return any(
        rel == excl or rel.startswith(excl + "/")
        for excl in _GITHUB_EXCLUDED_SUBPATHS
    )


def check_file(path: Path) -> list[tuple[int, str]]:
    """Return (line_number, config_path) for each non-canonical --config in path."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    findings: list[tuple[int, str]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for m in _BUILD_CMD_RE.finditer(line):
            config_arg = m.group(1).strip("`'\",();")
            if config_arg != _CANONICAL_CONFIG:
                findings.append((lineno, config_arg))
    return findings


def check_tree(root: Path) -> dict[Path, list[tuple[int, str]]]:
    """Scan Markdown files in deployable-artifact directories and return per-file findings.

    Only directories listed in _SCAN_DIRS are searched.  Returns a mapping of
    {file_path: [(line_number, config_path), ...]} for every file that contains
    at least one non-canonical --config reference.
    """
    all_findings: dict[Path, list[tuple[int, str]]] = {}

    for dir_parts in _SCAN_DIRS:
        scan_dir = root.joinpath(*dir_parts)
        if not scan_dir.is_dir():
            continue
        for md_file in sorted(scan_dir.rglob("*.md")):
            if _is_github_excluded(md_file, root):
                continue
            findings = check_file(md_file)
            if findings:
                all_findings[md_file] = findings

    return all_findings


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) > 1:
        print("Usage: python scripts/check_build_command.py [root_dir]", file=sys.stderr)
        return 2

    root = Path(argv[0]) if argv else Path.cwd()

    findings = check_tree(root)

    if not findings:
        print("check-build-command: OK — no non-canonical --config references found.")
        return 0

    total = sum(len(v) for v in findings.values())
    print(f"check-build-command: FAIL — {total} non-canonical --config reference(s) found:")
    for file_path, file_findings in sorted(findings.items()):
        try:
            display_path = file_path.relative_to(root)
        except ValueError:
            display_path = file_path
        for lineno, config_arg in file_findings:
            print(
                f"  {display_path}:{lineno}: --config {config_arg}"
                f"  (expected: {_CANONICAL_CONFIG})"
            )

    return 1


if __name__ == "__main__":
    sys.exit(main())
