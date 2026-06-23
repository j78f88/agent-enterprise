"""Tests for scripts/check_public_boundary.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_public_boundary.py"

spec = importlib.util.spec_from_file_location("check_public_boundary", SCRIPT)
assert spec and spec.loader
cpb = importlib.util.module_from_spec(spec)
sys.modules["check_public_boundary"] = cpb
spec.loader.exec_module(cpb)  # type: ignore[union-attr]


def test_posix_machine_local_path_flagged(tmp_path: Path) -> None:
    md = tmp_path / "doc.md"
    local_path = "/" + "home/example/apps/service"
    md.write_text("Use " + local_path + " for this run.\n", encoding="utf-8")
    findings = cpb.check_file(md)
    assert findings and findings[0][1] == "machine-local-posix-path"


def test_windows_machine_local_path_flagged(tmp_path: Path) -> None:
    md = tmp_path / "doc.md"
    local_path = "D:" + r"\VS\private-workbench\notes"
    md.write_text("Moved to " + local_path + "\n", encoding="utf-8")
    findings = cpb.check_file(md)
    assert findings and findings[0][1] == "machine-local-windows-path"


def test_generic_template_path_not_flagged(tmp_path: Path) -> None:
    md = tmp_path / "doc.md"
    md.write_text("Use docs/planning/ROADMAP.md or <project-root>/docs/.\n", encoding="utf-8")
    assert cpb.check_file(md) == []


def test_private_env_handling_flagged(tmp_path: Path) -> None:
    md = tmp_path / "doc.md"
    md.write_text("A live " + ".env" + " was linked into the sandbox.\n", encoding="utf-8")
    findings = cpb.check_file(md)
    assert findings and findings[0][1] == "private-env-handling"


def test_tree_excludes_archives_and_resolved(tmp_path: Path) -> None:
    archive = tmp_path / "docs" / "archive"
    archive.mkdir(parents=True)
    local_path = "/" + "home/example/apps/service"
    (archive / "old.md").write_text("Use " + local_path + ".\n", encoding="utf-8")
    resolved = tmp_path / "resolved"
    resolved.mkdir()
    (resolved / "generated.md").write_text("Use " + local_path + ".\n", encoding="utf-8")
    assert cpb.check_tree(tmp_path) == {}
