"""Tests for scripts/check_build_command.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_build_command.py"

spec = importlib.util.spec_from_file_location("check_build_command", SCRIPT)
assert spec and spec.loader
cbc = importlib.util.module_from_spec(spec)
sys.modules["check_build_command"] = cbc
spec.loader.exec_module(cbc)  # type: ignore[union-attr]


def _write_md(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "test.md"
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# check_file — unit tests
# ---------------------------------------------------------------------------


def test_canonical_config_not_flagged(tmp_path: Path) -> None:
    """Lines with config/project.config.example.yml should not be flagged."""
    md = _write_md(
        tmp_path,
        "Run `python init.py --config config/project.config.example.yml`\n",
    )
    assert cbc.check_file(md) == []


def test_private_config_flagged(tmp_path: Path) -> None:
    """Lines with config/project.config.yml (non-example) should be flagged."""
    md = _write_md(
        tmp_path,
        "Run `python init.py --config config/project.config.yml`\n",
    )
    findings = cbc.check_file(md)
    assert len(findings) == 1
    lineno, config_arg = findings[0]
    assert lineno == 1
    assert config_arg == "config/project.config.yml"


def test_init_without_config_not_flagged(tmp_path: Path) -> None:
    """`python init.py` without --config should not be flagged."""
    md = _write_md(tmp_path, "Run `python init.py` to build.\n")
    assert cbc.check_file(md) == []


def test_violation_line_number_correct(tmp_path: Path) -> None:
    """The reported line number should match the violating line."""
    md = _write_md(
        tmp_path,
        "# Title\n\nSome prose.\n\npython init.py --config other/config.yml\n",
    )
    findings = cbc.check_file(md)
    assert len(findings) == 1
    assert findings[0][0] == 5


# ---------------------------------------------------------------------------
# check_tree — exclusion tests
# ---------------------------------------------------------------------------


def test_check_tree_excludes_resolved(tmp_path: Path) -> None:
    """Files under resolved/ should not be scanned."""
    resolved = tmp_path / "resolved"
    resolved.mkdir()
    (resolved / "docs.md").write_text(
        "python init.py --config config/project.config.yml\n", encoding="utf-8"
    )
    assert not cbc.check_tree(tmp_path)


def test_check_tree_excludes_sprints(tmp_path: Path) -> None:
    """Files under sprints/ should not be scanned."""
    sprints = tmp_path / "sprints"
    sprints.mkdir()
    (sprints / "plan.md").write_text(
        "python init.py --config config/project.config.yml\n", encoding="utf-8"
    )
    assert not cbc.check_tree(tmp_path)


def test_check_tree_excludes_docs_archive(tmp_path: Path) -> None:
    """Files under docs/archive/ should not be scanned."""
    archive = tmp_path / "docs" / "archive"
    archive.mkdir(parents=True)
    (archive / "old.md").write_text(
        "python init.py --config config/project.config.yml\n", encoding="utf-8"
    )
    assert not cbc.check_tree(tmp_path)


def test_check_tree_detects_violation_in_skills(tmp_path: Path) -> None:
    """check_tree should find violations in skills/ markdown files."""
    skills = tmp_path / "skills"
    skills.mkdir()
    md = skills / "guide.md"
    md.write_text(
        "python init.py --config config/project.config.yml\n", encoding="utf-8"
    )
    findings = cbc.check_tree(tmp_path)
    assert md in findings
    assert findings[md][0][1] == "config/project.config.yml"


def test_check_tree_clean_when_no_violations(tmp_path: Path) -> None:
    """check_tree returns empty dict when all --config refs are canonical."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "readme.md").write_text(
        "python init.py --config config/project.config.example.yml\n",
        encoding="utf-8",
    )
    assert not cbc.check_tree(tmp_path)


# ---------------------------------------------------------------------------
# check_tree — GitHub collaboration template exclusion tests
# ---------------------------------------------------------------------------


def test_check_tree_excludes_github_issue_template(tmp_path: Path) -> None:
    """Files under .github/ISSUE_TEMPLATE/ should not be scanned."""
    tmpl_dir = tmp_path / ".github" / "ISSUE_TEMPLATE"
    tmpl_dir.mkdir(parents=True)
    (tmpl_dir / "bug_report.md").write_text(
        "python init.py --config config/project.config.yml\n", encoding="utf-8"
    )
    assert not cbc.check_tree(tmp_path)


def test_check_tree_excludes_github_pull_request_template(tmp_path: Path) -> None:
    """The .github/PULL_REQUEST_TEMPLATE.md file should not be scanned."""
    github_dir = tmp_path / ".github"
    github_dir.mkdir(parents=True)
    (github_dir / "PULL_REQUEST_TEMPLATE.md").write_text(
        "python init.py --config config/project.config.yml\n", encoding="utf-8"
    )
    assert not cbc.check_tree(tmp_path)


def test_check_tree_excludes_github_pull_request_template_dir(tmp_path: Path) -> None:
    """Files under .github/PULL_REQUEST_TEMPLATE/ directory should not be scanned."""
    pr_template_dir = tmp_path / ".github" / "PULL_REQUEST_TEMPLATE"
    pr_template_dir.mkdir(parents=True)
    (pr_template_dir / "feature.md").write_text(
        "python init.py --config config/project.config.yml\n", encoding="utf-8"
    )
    assert not cbc.check_tree(tmp_path)


def test_check_tree_excludes_github_workflows(tmp_path: Path) -> None:
    """Files under .github/workflows/ should not be scanned."""
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "ci.md").write_text(
        "python init.py --config config/project.config.yml\n", encoding="utf-8"
    )
    assert not cbc.check_tree(tmp_path)


def test_check_tree_still_scans_github_agents(tmp_path: Path) -> None:
    """Files under .github/agents/ (not excluded) should still be scanned."""
    agents_dir = tmp_path / ".github" / "agents"
    agents_dir.mkdir(parents=True)
    md = agents_dir / "guide.md"
    md.write_text(
        "python init.py --config config/project.config.yml\n", encoding="utf-8"
    )
    findings = cbc.check_tree(tmp_path)
    assert md in findings
