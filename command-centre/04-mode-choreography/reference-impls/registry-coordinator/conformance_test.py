"""Conformance test for the registry coordinator.

Drives the coordinator against a mixed-fleet fixture registry and
asserts every checkbox in ``mode-3-contract-v1``:

* Registry loads and validates (single file).
* Each entry validates against ``project-v1``.
* Drift detection flags the project pinned to an older substrate version.
* Impact-of-bump returns the right projects per contract tag.
* Mixed fleet (team + orchestration) is handled by construction.
* Three meta-agents are present.
* Harvest cycle runs and writes an audit record.

Exit code 0 = pass.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from coordinator import Coordinator  # noqa: E402


def assert_(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def run() -> int:
    registry = HERE / "fixtures" / "registry.yml"
    coord = Coordinator(registry_path=registry, current_substrate_version="2.0.0")

    # Checkbox: registry loads + validates.
    assert_(len(coord.registry["projects"]) == 2, "registry must hold 2 projects")

    # Checkbox: drift detection.
    drift = coord.detect_drift()
    by_id = {d.project_id: d for d in drift}
    assert_(by_id["project-team-a"].drift is False, "team-a must not be in drift")
    assert_(by_id["project-orch-b"].drift is True, "orch-b must be flagged as drifted")

    # Checkbox: impact-of-bump.
    impact = coord.impact_of_contract_bump("mode-2-contract-v1")
    assert_(impact == ["project-orch-b"], f"unexpected impact set: {impact}")

    impact_all = coord.impact_of_contract_bump("protocol-v1")
    assert_(
        set(impact_all) == {"project-team-a", "project-orch-b"},
        f"protocol-v1 must touch both projects: {impact_all}",
    )

    # Checkbox: mixed-fleet by construction.
    assert_(coord.list_by_mode_level("team") == ["project-team-a"], "team fleet wrong")
    assert_(
        coord.list_by_mode_level("orchestration") == ["project-orch-b"],
        "orchestration fleet wrong",
    )

    # Checkbox: meta-agents present (3 minimum).
    metas = coord.meta_agents()
    assert_(
        {"framework-dev", "harvest", "audit"}.issubset(metas.keys()),
        f"missing required meta-agents: {metas.keys()}",
    )

    # Checkbox: harvest cycle writes an audit record.
    with tempfile.TemporaryDirectory(prefix="mode3-audit-") as tmp:
        audit_path = coord.harvest(out_dir=Path(tmp))
        assert_(audit_path.exists(), "harvest must write an audit record")
        assert_(audit_path.stat().st_size > 0, "audit record must be non-empty")

    print("OK — mode-3-contract-v1 conformance: all checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(run())
