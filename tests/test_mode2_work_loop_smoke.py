"""Permanent smoke tests for Mode 2 work-loop ingestion and reconciliation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SMOKE = ROOT / "scripts" / "smoke_mode2_work_loop.py"


def test_mode2_work_loop_smoke_reconciles_ledger(tmp_path: Path) -> None:
    workdir = tmp_path / "workspace"
    result = subprocess.run(
        [sys.executable, str(SMOKE), "--workdir", str(workdir)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    summary = json.loads(result.stdout)

    assert summary["status"] == "pass"
    assert summary["ledger_id"] == "ITEM-042"
    assert summary["queue_state"] == "done"
    assert summary["dispatch_summary"]["tier"] == 3
    assert summary["dispatch_summary"]["status"] == "complete"
    assert summary["dispatch_summary"]["dispatched"][0]["state"] == "done"
    assert summary["artifact_path"].endswith("docs/WORK_LOOP_RESULT.md")

    ledger = (workdir / "docs" / "planning" / "BACKLOG_LEDGER.md").read_text(
        encoding="utf-8"
    )
    assert "| ITEM-042 | debt | CHAT-2026-06-19 | 13 | 0 | Sprint 13 | done |" in ledger
    assert "Mode 2 smoke completed" in ledger

    state = yaml.safe_load((workdir / "queue" / "state.yml").read_text(encoding="utf-8"))
    assert state == {"ITEM-042-docs-bridge": "done"}
    assert (workdir / "docs" / "WORK_LOOP_RESULT.md").read_text(encoding="utf-8").startswith("# Mode 2 smoke")


def test_mode2_work_loop_smoke_refuses_non_empty_workdir(tmp_path: Path) -> None:
    (tmp_path / "keep.txt").write_text("do not delete me", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SMOKE), "--workdir", str(tmp_path)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 2
    assert "must be empty or absent" in result.stderr
    assert (tmp_path / "keep.txt").read_text(encoding="utf-8") == "do not delete me"
