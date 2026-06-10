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
* The SAME ``mode-2-contract-v1`` checklist passes against BOTH Mode 2
  implementations — the frozen reference impl and the supported
  ``src/mode2_dispatcher/`` package (Sprint 5, Task Group 6) — and the
  reference impl stays byte-frozen (ADR 0008 criterion 5).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import runpy
import subprocess
import sys
import time
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


# ---------------------------------------------------------------------------
# Mode 2: one checklist, BOTH implementations (Sprint 5, Task Group 6)
#
# The mode-2-contract-v1 checklist encoded by the frozen reference impl's
# conformance_test.py, parametrized over the reference impl AND the
# supported src/mode2_dispatcher/ package — same fixtures, same assertions.
# Any semantic divergence between the two fails here.
# ---------------------------------------------------------------------------

MODE2_REFERENCE_DIR = (
    ROOT
    / "command-centre"
    / "03-mode-orchestration"
    / "reference-impls"
    / "file-queue-dispatcher"
)

MODE2_IMPLS = ["reference", "supported"]


def _mode2_module(impl: str):
    """Load the dispatcher module for one Mode 2 implementation."""
    if impl == "reference":
        name = "mode2_reference_dispatcher"
        if name in sys.modules:
            return sys.modules[name]
        spec = importlib.util.spec_from_file_location(
            name, MODE2_REFERENCE_DIR / "dispatcher.py"
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        # Register before exec: the reference impl's dataclasses resolve
        # their annotations through sys.modules[cls.__module__].
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    from src.mode2_dispatcher import dispatcher as supported

    return supported


def _mode2_fixture_registry(module, tmp: Path) -> dict:
    """Three callables — pass, ghost (verifier-fail), input-fail — mirroring
    the frozen conformance_test.py fixtures."""

    def write_report(inputs: dict) -> dict:
        path = Path(inputs["report_path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# Report for {inputs['task']}\n", encoding="utf-8")
        return {"tier": 1, "status": "success"}

    def claim_to_write_but_dont(inputs: dict) -> dict:
        # Deliberately do nothing — the verifier must reject (ghost-done).
        return {"tier": 1, "status": "success"}

    return {
        "fixture.write-report": module.Callable_(
            id="fixture.write-report",
            inputs_schema={
                "type": "object",
                "required": ["task", "report_path"],
                "properties": {
                    "task": {"type": "string"},
                    "report_path": {"type": "string"},
                },
            },
            outputs=[{"path": str(tmp / "out" / "report.md"), "required": True}],
            verifier=None,
            fn=write_report,
        ),
        "fixture.ghost-report": module.Callable_(
            id="fixture.ghost-report",
            inputs_schema={
                "type": "object",
                "required": ["task"],
                "properties": {"task": {"type": "string"}},
            },
            outputs=[{"path": str(tmp / "out" / "ghost.md"), "required": True}],
            verifier=None,
            fn=claim_to_write_but_dont,
        ),
        "fixture.bad-input": module.Callable_(
            id="fixture.bad-input",
            inputs_schema={
                "type": "object",
                "required": ["count"],
                "properties": {"count": {"type": "integer"}},
            },
            outputs=[{"return_tier": 1}],
            verifier=None,
            fn=lambda i: {"tier": 1, "status": "success"},
        ),
    }


def _mode2_seed_inbox(queue_root: Path, tmp: Path) -> None:
    inbox = queue_root / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    (inbox / "01-good.yml").write_text(
        yaml.safe_dump(
            {
                "id": "wi-001",
                "callable_id": "fixture.write-report",
                "inputs": {
                    "task": "draft release notes",
                    "report_path": str(tmp / "out" / "report.md"),
                },
            }
        ),
        encoding="utf-8",
    )
    (inbox / "02-ghost.yml").write_text(
        yaml.safe_dump(
            {
                "id": "wi-002",
                "callable_id": "fixture.ghost-report",
                "inputs": {"task": "would-be ghost-done"},
            }
        ),
        encoding="utf-8",
    )
    (inbox / "03-bad.yml").write_text(
        yaml.safe_dump(
            {
                "id": "wi-003",
                "callable_id": "fixture.bad-input",
                "inputs": {"count": "not-an-integer"},
            }
        ),
        encoding="utf-8",
    )


def _mode2_run_checklist(module, tmp: Path) -> dict:
    """Run the full mode-2-contract-v1 checklist; return the tier-3 summary."""
    queue_root = tmp / "queue"
    _mode2_seed_inbox(queue_root, tmp)
    registry = _mode2_fixture_registry(module, tmp)

    # Sleep one tick so the session_start clock is *before* artifact mtimes.
    time.sleep(0.01)

    dispatcher = module.Dispatcher(queue_root=queue_root, registry=registry)
    summary = dispatcher.run()

    # Checkbox 1: inbox sourced from files (3 items loaded).
    assert len(summary["dispatched"]) == 3, "expected 3 dispatched items"

    good, ghost, bad = summary["dispatched"]

    # Checkbox 2 + 4 + 5: resolved, invoked, return captured.
    assert good["state"] == "done", f"good item did not reach done: {good}"
    assert good["verifier_passed"] is True, "good item verifier should pass"
    assert any(
        a["present"] for a in good["artifacts"]
    ), "good item should produce an artifact"

    # Checkbox 6: verifier rejects ghost-done (no artifact written).
    assert ghost["state"] == "rejected", f"ghost item must be rejected: {ghost}"
    assert ghost["verifier_passed"] is False, "ghost verifier must fail"
    assert any(
        "missing required artifact" in r for r in ghost["verifier_reasons"]
    ), f"ghost item reasons missing artifact-existence failure: {ghost}"

    # Checkbox 3: input validation short-circuits.
    assert bad["state"] == "failed", f"bad-input item must fail: {bad}"
    assert any(
        "input validation" in e for e in bad["errors"]
    ), f"bad-input must report a validation error: {bad}"

    # Checkbox 7: FSM forbids illegal transitions.
    with pytest.raises(module.TransitionError):
        dispatcher._transition("wi-001", "done", "in-progress")

    # Checkbox 8: tier-3 summary shape.
    assert summary["tier"] == 3, "summary must be tier 3"
    assert summary["status"] == "complete", "summary status must be 'complete'"
    assert "session_start" in summary, "summary must include session_start"

    # Checkbox: persisted state file matches in-memory state.
    on_disk = yaml.safe_load((queue_root / "state.yml").read_text(encoding="utf-8"))
    assert on_disk["wi-001"] == "done", "state.yml should record wi-001=done"
    assert on_disk["wi-002"] == "rejected", "state.yml should record wi-002=rejected"
    assert on_disk["wi-003"] == "failed", "state.yml should record wi-003=failed"

    return summary


@pytest.mark.parametrize("impl", MODE2_IMPLS)
def test_mode2_contract_checklist_passes_for_both_impls(
    impl: str, tmp_path: Path
) -> None:
    _mode2_run_checklist(_mode2_module(impl), tmp_path)


def test_mode2_summary_shape_parity_between_impls(tmp_path: Path) -> None:
    """The supported impl's tier-3 summary is a strict superset of the
    reference impl's, and per-item entries are shape-identical.

    NOTE the summary is deliberately NOT validated against
    ``subagent-return-tier3.schema.json``: that schema is the planner
    composition shape (agent const "planner", sprintNumber, composition)
    and the frozen reference impl's summary fails it identically. The
    contract checklist pins tier == 3 / status == "complete" /
    session_start instead; this test pins parity between the two impls.
    """
    ref = _mode2_run_checklist(_mode2_module("reference"), tmp_path / "reference")
    sup = _mode2_run_checklist(_mode2_module("supported"), tmp_path / "supported")

    # Every reference summary key survives in the supported summary.
    assert set(ref) <= set(sup), f"supported summary lost keys: {set(ref) - set(sup)}"
    assert (sup["tier"], sup["status"]) == (ref["tier"], ref["status"])

    # Per-item dispatch entries: identical key sets and identical outcomes.
    assert len(ref["dispatched"]) == len(sup["dispatched"]) == 3
    for ref_entry, sup_entry in zip(ref["dispatched"], sup["dispatched"]):
        assert set(ref_entry) == set(sup_entry)
        assert ref_entry["item_id"] == sup_entry["item_id"]
        assert ref_entry["state"] == sup_entry["state"]
        assert ref_entry["verifier_passed"] == sup_entry["verifier_passed"]
        assert ref_entry["errors"] == sup_entry["errors"]


# ---------------------------------------------------------------------------
# Mode 2 reference impl byte-freeze (ADR 0008 criterion 5)
# ---------------------------------------------------------------------------

MODE2_REFERENCE_FROZEN_SHA256 = {
    "dispatcher.py": "5a982b8e26eb593d4a21142a22366b8e924fc8dbfbd0aabeb194fcb221769aab",
    "conformance_test.py": "41c2b576ed35c42961a93578cddd30b8873b581eab5bbd91fa6a0112b09ff936",
    "README.md": "e199eb2738554121063e5ef2b3f06abc0a8fbcfa852027c7d9c4fa366d546e85",
}


@pytest.mark.parametrize("name", sorted(MODE2_REFERENCE_FROZEN_SHA256))
def test_mode2_reference_impl_is_byte_frozen(name: str) -> None:
    path = MODE2_REFERENCE_DIR / name
    # Normalize CRLF before hashing: Windows checkouts (core.autocrlf)
    # rewrite line endings, which is checkout policy, not a content change.
    # The pinned hashes are over LF bytes; any real edit still fails.
    content = path.read_bytes().replace(b"\r\n", b"\n")
    actual = hashlib.sha256(content).hexdigest()
    expected = MODE2_REFERENCE_FROZEN_SHA256[name]
    assert actual == expected, (
        f"{path} has been modified (sha256 {actual}, pinned {expected}). "
        "ADR 0008 criterion 5 (Non-displacing): 'The reference implementation "
        "stays frozen byte-unchanged as contract pedagogy.' Revert the change "
        "and apply it to the supported implementation in src/mode2_dispatcher/ "
        "instead; a genuinely breaking contract need escalates to -v2 per ADR 0003."
    )
