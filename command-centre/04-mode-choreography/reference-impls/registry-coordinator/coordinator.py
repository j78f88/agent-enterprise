"""Registry reference coordinator — Mode 3.

Implements every responsibility in
``command-centre/04-mode-choreography/contract.md``:

* Loads ``registry.yml`` (one file, single source of truth).
* Validates every entry against ``project-v1.schema.json``.
* Detects substrate-version and contract-pin drift.
* Surfaces impact of a contract bump across the fleet.
* Runs a harvest cycle and writes an audit record.
* Hosts three meta-agent stubs (``meta_agents/``).
* Handles mixed-fleet (team + orchestration) registries by construction.

Pure stdlib + jsonschema + PyYAML.
"""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass
from pathlib import Path

import jsonschema
import yaml


# ---------------------------------------------------------------------------
# Schema loading
# ---------------------------------------------------------------------------

# Resolve the repo's ``schemas/`` directory relative to this file.
# command-centre/04-mode-choreography/reference-impls/registry-coordinator/coordinator.py
# -> ../../../../schemas/
_SCHEMAS_DIR = Path(__file__).resolve().parents[4] / "schemas"


def _load_schema(name: str) -> dict:
    return json.loads((_SCHEMAS_DIR / name).read_text(encoding="utf-8"))


def _registry_resolver() -> jsonschema.RefResolver:
    registry = _load_schema("registry-v1.schema.json")
    project = _load_schema("project-v1.schema.json")
    # Seed the resolver store so $ref lookups resolve locally rather
    # than trying to fetch the canonical $id over the network.
    store = {
        registry["$id"]: registry,
        project["$id"]: project,
        # Relative reference used in registry-v1.schema.json.
        "project-v1.schema.json": project,
    }
    return jsonschema.RefResolver(base_uri=registry["$id"], referrer=registry, store=store)


# ---------------------------------------------------------------------------
# Domain
# ---------------------------------------------------------------------------


@dataclass
class DriftReport:
    project_id: str
    current_pin: str
    declared_pin: str
    drift: bool


class Coordinator:
    """A single registry coordinator instance."""

    def __init__(self, registry_path: Path, current_substrate_version: str):
        self.registry_path = Path(registry_path)
        self.current_substrate_version = current_substrate_version
        self.registry = self._load()

    # -- load + validate ----------------------------------------------------

    def _load(self) -> dict:
        text = self.registry_path.read_text(encoding="utf-8")
        data = yaml.safe_load(text)
        jsonschema.validate(
            instance=data,
            schema=_load_schema("registry-v1.schema.json"),
            resolver=_registry_resolver(),
        )
        # Per-entry project-v1 validation (single source of truth).
        project_schema = _load_schema("project-v1.schema.json")
        for entry in data["projects"]:
            jsonschema.validate(instance=entry, schema=project_schema)
        return data

    # -- responsibilities ---------------------------------------------------

    def detect_drift(self) -> list[DriftReport]:
        reports: list[DriftReport] = []
        for entry in self.registry["projects"]:
            declared = entry["substrate_version"]
            drift = declared not in ("custom", self.current_substrate_version)
            reports.append(
                DriftReport(
                    project_id=entry["id"],
                    current_pin=self.current_substrate_version,
                    declared_pin=declared,
                    drift=drift,
                )
            )
        return reports

    def impact_of_contract_bump(self, contract_tag: str) -> list[str]:
        """Return ids of every project pinned to ``contract_tag``."""
        return [
            entry["id"]
            for entry in self.registry["projects"]
            if contract_tag in entry.get("contract_pins", [])
        ]

    def list_by_mode_level(self, mode_level: str) -> list[str]:
        return [
            entry["id"]
            for entry in self.registry["projects"]
            if entry["mode_level"] == mode_level
        ]

    def harvest(self, out_dir: Path) -> Path:
        """Run a (toy) harvest cycle and write an audit record."""
        out_dir.mkdir(parents=True, exist_ok=True)
        audit = {
            "tier": 3,
            "kind": "harvest-audit",
            "performed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "coordinator": self.registry.get("coordinator", {}),
            "scanned_projects": [e["id"] for e in self.registry["projects"]],
            "drift": [d.__dict__ for d in self.detect_drift()],
            "promotion_candidates": [],
            "decisions": [],
        }
        path = out_dir / f"audit-{int(dt.datetime.now(dt.timezone.utc).timestamp())}.json"
        path.write_text(json.dumps(audit, indent=2, sort_keys=True), encoding="utf-8")
        return path

    # -- meta-agent registry ------------------------------------------------

    def meta_agents(self) -> dict[str, Path]:
        base = Path(__file__).resolve().parent / "meta_agents"
        return {p.stem.replace(".agent", ""): p for p in sorted(base.glob("*.agent.md"))}
