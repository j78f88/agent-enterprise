"""CLI tests for the Mode 3 choreography entry point."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "choreography.py"
REGISTRY = (
    ROOT
    / "command-centre"
    / "04-mode-choreography"
    / "reference-impls"
    / "registry-coordinator"
    / "fixtures"
    / "registry.yml"
)


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=str(cwd or ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_choreography_validate_registry_reports_ok() -> None:
    result = run_cli("validate-registry", "--registry", str(REGISTRY))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK: registry valid" in result.stdout
    assert "projects=2" in result.stdout


def test_choreography_drift_outputs_json() -> None:
    result = run_cli("drift", "--registry", str(REGISTRY), "--current-version", "2.0.0")
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["contract"] == "mode-3-contract-v1"
    assert payload["registry"] == str(REGISTRY)
    by_id = {row["project_id"]: row for row in payload["drift"]}
    assert by_id["project-team-a"]["drift"] is False
    assert by_id["project-orch-b"]["drift"] is True


def test_choreography_harvest_writes_audit(tmp_path: Path) -> None:
    result = run_cli(
        "harvest",
        "--registry",
        str(REGISTRY),
        "--current-version",
        "2.0.0",
        "--out-dir",
        str(tmp_path / "audit"),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    audit_path = Path(payload["audit_path"])
    assert audit_path.exists()
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit["kind"] == "harvest-audit"
    assert set(audit["scanned_projects"]) == {"project-team-a", "project-orch-b"}
