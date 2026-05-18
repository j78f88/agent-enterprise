"""Enforce skill frontmatter ``description`` format rules.

Authored as part of the v3.0.1 enforcement release. Rules are documented
in ``docs/SKILL_AUTHORING_GUIDE.md`` under "Description":

1. Maximum 1024 characters.
2. First sentence: what the skill does (third person, present tense).
3. Second sentence: "Use when [trigger conditions]." (trigger phrase
   required; we accept ``Use when``, ``Use after``, ``Use to``, or
   ``Use this skill`` as the trigger marker).
4. Do not repeat the skill name as the first word.
5. First character is a capital letter.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_GLOB = "skills/*/*.skill.md"
MAX_CHARS = 1024
# Any sentence beginning ``Use <word>`` is treated as a trigger phrase:
# ``Use when``, ``Use after``, ``Use to``, ``Use with``, ``Use on``,
# ``Use during``, ``Use this skill``, etc. The leading capital is required
# so inline lowercase ``use`` and substrings like ``useful`` do not match.
TRIGGER_RE = re.compile(r"\bUse [a-z]")


def _skill_files() -> list[Path]:
    return sorted(REPO_ROOT.glob(SKILL_GLOB))


def _parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    return yaml.safe_load(text[4:end]) or {}


def _read_description(skill_path: Path) -> tuple[str, str]:
    """Return (description, skill_name)."""
    fm = _parse_frontmatter(skill_path.read_text(encoding="utf-8"))
    return (fm.get("description", "") or "").strip(), (fm.get("name", "") or "").strip()


@pytest.mark.parametrize("skill_path", _skill_files(), ids=lambda p: p.parent.name)
def test_description_under_char_cap(skill_path: Path) -> None:
    desc, _ = _read_description(skill_path)
    assert desc, f"{skill_path.relative_to(REPO_ROOT)} has no description"
    assert len(desc) <= MAX_CHARS, (
        f"{skill_path.relative_to(REPO_ROOT)} description is {len(desc)} chars; "
        f"cap is {MAX_CHARS}."
    )


@pytest.mark.parametrize("skill_path", _skill_files(), ids=lambda p: p.parent.name)
def test_description_starts_with_capital(skill_path: Path) -> None:
    desc, _ = _read_description(skill_path)
    assert desc[:1].isupper(), (
        f"{skill_path.relative_to(REPO_ROOT)} description must start with a "
        f"capital letter; got: {desc[:40]!r}"
    )


@pytest.mark.parametrize("skill_path", _skill_files(), ids=lambda p: p.parent.name)
def test_description_has_trigger_phrase(skill_path: Path) -> None:
    desc, _ = _read_description(skill_path)
    assert TRIGGER_RE.search(desc), (
        f"{skill_path.relative_to(REPO_ROOT)} description must contain a "
        f"'Use <when|after|to|with|on|...>' trigger sentence. Got: {desc[:120]!r}"
    )


@pytest.mark.parametrize("skill_path", _skill_files(), ids=lambda p: p.parent.name)
def test_description_does_not_start_with_skill_name(skill_path: Path) -> None:
    desc, name = _read_description(skill_path)
    if not name:
        pytest.skip("skill has no 'name' field; nothing to compare")
    first_word = desc.split(maxsplit=1)[0].strip(".,:;").lower()
    assert first_word != name.lower(), (
        f"{skill_path.relative_to(REPO_ROOT)} description starts with the skill "
        f"name {name!r}. Open with a verb instead."
    )
