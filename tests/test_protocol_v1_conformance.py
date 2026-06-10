"""Conformance tests for the four protocol-v1 schemas.

Asserts:

* Each schema is itself a valid Draft-07 schema.
* Every skill in ``skills/`` satisfies ``frontmatter-v1`` AND
  ``callable-v1``.
* Every instruction in ``instructions/`` satisfies ``frontmatter-v1``.
* Every agent body in ``agents/`` satisfies ``frontmatter-v1``.
* A canonical fixture registry validates against ``registry-v1``.
* A canonical fixture project validates against ``project-v1``.
* The Mode 2 + Mode 3 conformance scripts run cleanly.
"""

from __future__ import annotations

import json
import runpy
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest
import yaml
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"


def _load_schema(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def _parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    return yaml.safe_load(text[3:end].strip()) or {}


def _normalize(fm: dict) -> dict:
    """Apply the read-side ``scope -> applies_to`` alias (ADR-0012)."""
    if fm and "applies_to" not in fm and "scope" in fm:
        fm = dict(fm)
        fm["applies_to"] = fm["scope"]
    return fm


# ---------------------------------------------------------------------------
# Schema self-validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "name",
    [
        "frontmatter-v1.schema.json",
        "callable-v1.schema.json",
        "project-v1.schema.json",
        "registry-v1.schema.json",
    ],
)
def test_schema_is_valid_draft7(name: str) -> None:
    jsonschema.Draft7Validator.check_schema(_load_schema(name))


# ---------------------------------------------------------------------------
# Substrate conformance
# ---------------------------------------------------------------------------


def _skill_files() -> list[Path]:
    return sorted(ROOT.glob("skills/*/*.skill.md"))


def _instruction_files() -> list[Path]:
    return sorted(ROOT.glob("instructions/**/*.instructions.md"))


def _agent_files() -> list[Path]:
    return sorted(ROOT.glob("agents/*.body.md"))


@pytest.mark.parametrize("path", _skill_files(), ids=lambda p: p.name)
def test_every_skill_satisfies_frontmatter_and_callable_v1(path: Path) -> None:
    fm = _normalize(_parse_frontmatter(path.read_text(encoding="utf-8")))
    jsonschema.validate(instance=fm, schema=_load_schema("frontmatter-v1.schema.json"))
    jsonschema.validate(instance=fm, schema=_load_schema("callable-v1.schema.json"))


@pytest.mark.parametrize("path", _instruction_files(), ids=lambda p: p.name)
def test_every_instruction_satisfies_frontmatter_v1(path: Path) -> None:
    fm = _normalize(_parse_frontmatter(path.read_text(encoding="utf-8")))
    jsonschema.validate(instance=fm, schema=_load_schema("frontmatter-v1.schema.json"))


@pytest.mark.parametrize("path", _agent_files(), ids=lambda p: p.name)
def test_every_agent_body_satisfies_frontmatter_v1(path: Path) -> None:
    fm = _normalize(_parse_frontmatter(path.read_text(encoding="utf-8")))
    jsonschema.validate(instance=fm, schema=_load_schema("frontmatter-v1.schema.json"))


# ---------------------------------------------------------------------------
# Project + registry conformance
# ---------------------------------------------------------------------------


def test_fixture_project_validates() -> None:
    fixture = {
        "id": "fixture-project",
        "name": "Fixture",
        "repo": "https://example.com/fixture",
        "mode_level": "team",
        "substrate_version": "2.0.0",
        "contract_pins": ["protocol-v1", "mode-1-contract-v1"],
    }
    jsonschema.validate(instance=fixture, schema=_load_schema("project-v1.schema.json"))


def test_fixture_project_orchestration_requires_dispatcher() -> None:
    fixture = {
        "id": "orch-project",
        "name": "Orch",
        "repo": "https://example.com/orch",
        "mode_level": "orchestration",
        "substrate_version": "2.0.0",
        "contract_pins": ["protocol-v1", "mode-1-contract-v1", "mode-2-contract-v1"],
        # missing dispatcher
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=fixture, schema=_load_schema("project-v1.schema.json"))


def test_fixture_registry_validates() -> None:
    fixture_path = (
        ROOT
        / "command-centre"
        / "04-mode-choreography"
        / "reference-impls"
        / "registry-coordinator"
        / "fixtures"
        / "registry.yml"
    )
    data = yaml.safe_load(fixture_path.read_text(encoding="utf-8"))

    registry_schema = _load_schema("registry-v1.schema.json")
    project_schema = _load_schema("project-v1.schema.json")
    registry = Registry().with_resources(
        [
            (registry_schema["$id"], Resource.from_contents(registry_schema)),
            (project_schema["$id"], Resource.from_contents(project_schema)),
            ("project-v1.schema.json", Resource.from_contents(project_schema)),
        ]
    )
    jsonschema.validate(instance=data, schema=registry_schema, registry=registry)


# ---------------------------------------------------------------------------
# Reference-impl conformance tests run cleanly
# ---------------------------------------------------------------------------


def test_mode2_reference_impl_passes() -> None:
    script = (
        ROOT
        / "command-centre"
        / "03-mode-orchestration"
        / "reference-impls"
        / "file-queue-dispatcher"
        / "conformance_test.py"
    )
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, f"mode-2 conformance failed:\n{result.stdout}\n{result.stderr}"


def test_mode3_reference_impl_passes() -> None:
    script = (
        ROOT
        / "command-centre"
        / "04-mode-choreography"
        / "reference-impls"
        / "registry-coordinator"
        / "conformance_test.py"
    )
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, f"mode-3 conformance failed:\n{result.stdout}\n{result.stderr}"
