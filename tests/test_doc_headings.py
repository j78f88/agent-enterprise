"""Enforce heading hierarchy in top-level user-facing documentation.

Authored as part of the v3.0.1 enforcement release. The rule:

A standalone line whose entire content is a single bold span
(``**...**`` on its own line, surrounded by blank lines or document
edges) is a *pseudo-heading*. It should be a real markdown heading
(``##``, ``###``, etc.) so that the document outline, the table of
contents tooling, and screen readers can see the structure.

Inline bold field labels in lists (``- **Solution:** ...``), in step
bodies (``**Step 2 — Current:** ...``), and elsewhere in running prose
are fine and do not trigger the rule.

Scope: top-level user-facing docs only. Sprint records (since
removed) and the long-form ``sandbox-architecture.md`` design prose
are out of scope \u2014 they are write-once historical or design artifacts.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

USER_FACING_DOCS: tuple[Path, ...] = (
    REPO_ROOT / "README.md",
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "CLAUDE.md",
    REPO_ROOT / "docs" / "CONTEXT.md",
    REPO_ROOT / "CHANGELOG.md",
    REPO_ROOT / "docs" / "ANTI_FRAGILITY.md",
    REPO_ROOT / "SECURITY.md",
)

# Also enforce on every top-level docs/*.md (not docs/sprints, not
# docs/decisions, not docs/visuals).
DOCS_DIR = REPO_ROOT / "docs"


def _docs_dir_files() -> list[Path]:
    if not DOCS_DIR.is_dir():
        return []
    return sorted(p for p in DOCS_DIR.glob("*.md") if p.is_file())


def _scoped_docs() -> list[Path]:
    return [p for p in (*USER_FACING_DOCS, *_docs_dir_files()) if p.is_file()]


PSEUDO_HEADING_RE = re.compile(r"^\*\*[^*\n]+\*\*\s*$")
FENCE_RE = re.compile(r"^```")


def _pseudo_heading_hits(path: Path) -> list[tuple[int, str]]:
    """Return (line_number, line) hits for standalone bold-only lines."""
    lines = path.read_text(encoding="utf-8").splitlines()
    hits: list[tuple[int, str]] = []
    in_fence = False
    in_frontmatter = False
    for i, raw in enumerate(lines, start=1):
        if i == 1 and raw.strip() == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if raw.strip() == "---":
                in_frontmatter = False
            continue
        if FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not PSEUDO_HEADING_RE.match(raw):
            continue
        # Must be standalone: surrounded by blank lines or document edges.
        prev_blank = i == 1 or not lines[i - 2].strip()
        next_blank = i == len(lines) or not lines[i].strip()
        if prev_blank and next_blank:
            hits.append((i, raw.rstrip()))
    return hits


@pytest.mark.parametrize(
    "path", _scoped_docs(), ids=lambda p: str(p.relative_to(REPO_ROOT))
)
def test_no_pseudo_headings(path: Path) -> None:
    hits = _pseudo_heading_hits(path)
    assert not hits, (
        f"{path.relative_to(REPO_ROOT)} contains standalone bold-only lines "
        f"that look like headings. Convert each to a real markdown heading "
        f"(##, ###, ...). Hits:\n"
        + "\n".join(f"  L{n}: {line}" for n, line in hits)
    )


def test_at_least_one_doc_discovered() -> None:
    assert _scoped_docs(), "no user-facing docs discovered for hierarchy check"
