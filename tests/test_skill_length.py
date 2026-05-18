"""Enforce the 200-line cap on ``*.skill.md`` files.

Authored as part of the v3.0.1 enforcement release. The cap is documented
in ``docs/SKILL_AUTHORING_GUIDE.md`` under "Length Rules." Skills that
need more space must extract reference material into supporting files in
the same skill directory; supporting files do not count toward the cap.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_GLOB = "skills/*/*.skill.md"
MAX_LINES = 200


def _skill_files() -> list[Path]:
    return sorted(REPO_ROOT.glob(SKILL_GLOB))


@pytest.mark.parametrize("skill_path", _skill_files(), ids=lambda p: p.parent.name)
def test_skill_file_under_line_cap(skill_path: Path) -> None:
    line_count = sum(1 for _ in skill_path.read_text(encoding="utf-8").splitlines())
    assert line_count <= MAX_LINES, (
        f"{skill_path.relative_to(REPO_ROOT)} is {line_count} lines; "
        f"cap is {MAX_LINES}. Extract reference material into a supporting "
        f"file in the same directory (see SKILL_AUTHORING_GUIDE.md)."
    )


def test_at_least_one_skill_discovered() -> None:
    # Guard against the glob silently matching nothing if the layout changes.
    assert _skill_files(), "no *.skill.md files discovered under skills/"
