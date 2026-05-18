"""Enforce voice and prohibition-style conventions across agent-facing files.

Authored as part of the v3.0.1 enforcement release. Rules are documented
in ``docs/SKILL_AUTHORING_GUIDE.md`` under "Voice" and
"Prohibition Style in List Items":

1. All-caps prohibitions (``MUST``, ``NEVER``, ``DO NOT``) are not allowed
   outside code spans, links, or qualified contexts (acronyms, quoted
   user input).
2. Hedging words (``consider``, ``perhaps``, ``might``, ``it may be useful``,
   ``you could``) are forbidden in skill files. They are tolerated in
   instructions and agent bodies only when used as nouns or in conditional
   prescriptions \u2014 the test reports them as warnings, not failures, in
   those scopes.
3. The split between prose prohibitions (``**never** verb``) and
   list-item-start prohibitions (``**Never** verb phrase``) is structural,
   not arbitrary: list items beginning with ``- **Never**`` are allowed.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

SKILL_GLOB = "skills/*/*.skill.md"
AGENT_BODY_GLOB = "agents/*.body.md"
INSTRUCTION_GLOBS = ("instructions/generic/*.md", "instructions/configurable/*.md")

# Lines that the test must ignore: fenced code, indented code, inline backticks,
# markdown link targets, and YAML frontmatter.
FENCE_RE = re.compile(r"^```")
INDENTED_CODE_RE = re.compile(r"^( {4,}|\t)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
LINK_RE = re.compile(r"\[[^\]]*\]\([^)]*\)")

ALL_CAPS_PROHIBITION_RE = re.compile(r"\b(MUST|NEVER|DO NOT)\b")
HEDGING_RE = re.compile(
    r"(?<![\w-])(consider|perhaps|might|may be useful|you could)(?![\w-])",
    re.IGNORECASE,
)


def _strip_inline_noise(line: str) -> str:
    """Remove code spans and link targets so they do not produce false hits."""
    line = INLINE_CODE_RE.sub("", line)
    line = LINK_RE.sub("", line)
    return line


def _scan(path: Path, pattern: re.Pattern[str]) -> list[tuple[int, str]]:
    """Return (line_number, line) hits, skipping code and frontmatter."""
    hits: list[tuple[int, str]] = []
    in_fence = False
    in_frontmatter = False
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
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
        if in_fence or INDENTED_CODE_RE.match(raw):
            continue
        stripped = _strip_inline_noise(raw)
        if pattern.search(stripped):
            hits.append((i, raw.rstrip()))
    return hits


def _skill_files() -> list[Path]:
    return sorted(REPO_ROOT.glob(SKILL_GLOB))


def _agent_body_files() -> list[Path]:
    return sorted(REPO_ROOT.glob(AGENT_BODY_GLOB))


def _instruction_files() -> list[Path]:
    files: list[Path] = []
    for glob in INSTRUCTION_GLOBS:
        files.extend(REPO_ROOT.glob(glob))
    return sorted(files)


def _agent_facing_files() -> list[Path]:
    return _skill_files() + _agent_body_files() + _instruction_files()


@pytest.mark.parametrize(
    "path", _agent_facing_files(), ids=lambda p: str(p.relative_to(REPO_ROOT))
)
def test_no_all_caps_prohibitions(path: Path) -> None:
    hits = _scan(path, ALL_CAPS_PROHIBITION_RE)
    assert not hits, (
        f"{path.relative_to(REPO_ROOT)} contains all-caps prohibitions; use "
        f"bold lowercase (e.g. **must**, **never**, **do not**). Hits:\n"
        + "\n".join(f"  L{n}: {line}" for n, line in hits)
    )


@pytest.mark.parametrize("path", _skill_files(), ids=lambda p: p.parent.name)
def test_no_hedging_in_skills(path: Path) -> None:
    hits = _scan(path, HEDGING_RE)
    assert not hits, (
        f"{path.relative_to(REPO_ROOT)} contains hedging words in a skill file; "
        f"skills require imperative voice. Hits:\n"
        + "\n".join(f"  L{n}: {line}" for n, line in hits)
    )
