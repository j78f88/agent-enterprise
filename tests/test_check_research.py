"""Tests for scripts/check_research.py — the fail-closed research-home validator.

Two jobs:
  1. Prove the seeded container (the real repo research home) conforms.
  2. Demonstrate the core guarantee — unconformed material cannot be canonical:
     a bare record dropped into sources/ FAILS the gate until it conforms.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_research.py"

spec = importlib.util.spec_from_file_location("check_research", SCRIPT)
assert spec and spec.loader
cr = importlib.util.module_from_spec(spec)
sys.modules["check_research"] = cr
spec.loader.exec_module(cr)  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FM = (
    "---\n"
    "title: \"{title}\"\n"
    "status: {status}\n"
    "trust: {trust}\n"
    "classification: OFFICIAL\n"
    "date: 2026-06-01\n"
    "---\n\n# {title}\n"
)


def _fails(home: Path) -> list:
    return [f for f in cr.run(home) if f.severity == cr.FAIL]


def _valid_source_note(sid: str = "SRC-test") -> dict:
    return {
        "id": sid,
        "title": "Test source",
        "source_tier": "primary",
        "publisher": "Test Publisher",
        "retrieval_date": "2026-06-01",
        "classification": "OFFICIAL",
        "trust": "trusted",
        "locator": {"kind": "document", "ref": "Test Standard §1"},
        "content_hash": "sha256:" + "a" * 64,
    }


def _valid_claim(cid: str = "CLM-test", source_id: str = "SRC-test") -> dict:
    return {
        "id": cid,
        "statement": "This is a sufficiently long falsifiable statement.",
        "verdict": "plausible",
        "evidence": [{"source_id": source_id, "retrieval_date": "2026-06-01"}],
        "classification": "OFFICIAL",
        "trust": "trusted",
    }


def _minimal_home(tmp_path: Path, registered_ids: list[str] | None = None) -> Path:
    """Build a minimal conforming research home (container only, no records)."""
    home = tmp_path / "research"
    (home / "_meta").mkdir(parents=True)
    (home / "sources").mkdir()
    (home / "claims").mkdir()
    (home / "_staging").mkdir()

    (home / "_meta" / "charter.md").write_text(
        _FM.format(title="Charter", status="proposal", trust="trusted"), encoding="utf-8"
    )
    ids_block = "\n".join(registered_ids or [])
    (home / "INDEX.md").write_text(
        _FM.format(title="INDEX", status="proposal", trust="trusted") + "\n" + ids_block + "\n",
        encoding="utf-8",
    )
    return home


# ---------------------------------------------------------------------------
# Schema validity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", ["source-note.schema.json", "claim.schema.json"])
def test_research_schema_is_valid_draft7(name: str) -> None:
    schema = cr.load_schema(name)
    assert schema is not None, f"{name} not found"
    jsonschema.Draft7Validator.check_schema(schema)


# ---------------------------------------------------------------------------
# The real repo container conforms (integration)
# ---------------------------------------------------------------------------

def test_repo_research_home_conforms() -> None:
    """The seeded container must pass the gate with zero hard-fails."""
    home = cr.default_research_home(cr.ROOT)
    assert home.is_dir(), f"research home missing: {home}"
    fails = _fails(home)
    assert not fails, "real research home has contract violations:\n" + "\n".join(
        f"  {f.path}: {f.message}" for f in fails
    )


# ---------------------------------------------------------------------------
# Baseline + positive promotion
# ---------------------------------------------------------------------------

def test_minimal_home_passes(tmp_path: Path) -> None:
    assert not _fails(_minimal_home(tmp_path))


def test_conformed_records_pass(tmp_path: Path) -> None:
    """A fully conformed source-note + claim, registered in INDEX, passes."""
    home = _minimal_home(tmp_path, registered_ids=["SRC-test", "CLM-test"])
    (home / "sources" / "SRC-test.json").write_text(json.dumps(_valid_source_note()), encoding="utf-8")
    (home / "claims" / "CLM-test.json").write_text(json.dumps(_valid_claim()), encoding="utf-8")
    assert not _fails(home)


# ---------------------------------------------------------------------------
# Core guarantee: unconformed material cannot be canonical
# ---------------------------------------------------------------------------

def test_bare_source_note_fails(tmp_path: Path) -> None:
    """A bare record (missing required provenance) dropped into sources/ FAILS —
    this is the 'process followed regardless of slash command' guarantee."""
    home = _minimal_home(tmp_path)
    (home / "sources" / "SRC-bare.json").write_text(json.dumps({"id": "SRC-bare"}), encoding="utf-8")
    msgs = [f.message for f in _fails(home)]
    assert any("schema" in m for m in msgs), msgs


def test_untrusted_source_note_in_canonical_fails(tmp_path: Path) -> None:
    home = _minimal_home(tmp_path, registered_ids=["SRC-test"])
    note = _valid_source_note()
    note["trust"] = "untrusted"
    (home / "sources" / "SRC-test.json").write_text(json.dumps(note), encoding="utf-8")
    assert any("untrusted source-note" in f.message for f in _fails(home))


def test_dangling_evidence_fails(tmp_path: Path) -> None:
    home = _minimal_home(tmp_path, registered_ids=["CLM-x"])
    claim = _valid_claim(cid="CLM-x", source_id="SRC-does-not-exist")
    (home / "claims" / "CLM-x.json").write_text(json.dumps(claim), encoding="utf-8")
    assert any("source_id not found" in f.message for f in _fails(home))


def test_verified_needs_two_independent_sources(tmp_path: Path) -> None:
    home = _minimal_home(tmp_path, registered_ids=["SRC-test", "CLM-v"])
    (home / "sources" / "SRC-test.json").write_text(json.dumps(_valid_source_note()), encoding="utf-8")
    claim = _valid_claim(cid="CLM-v")
    claim["verdict"] = "verified"  # only one evidence item, not independent
    (home / "claims" / "CLM-v.json").write_text(json.dumps(claim), encoding="utf-8")
    assert any("independent sources" in f.message for f in _fails(home))


def test_quarantined_content_must_be_untrusted(tmp_path: Path) -> None:
    home = _minimal_home(tmp_path)
    # A non-README content doc in _staging mislabelled trusted -> FAIL.
    (home / "_staging" / "leak.md").write_text(
        _FM.format(title="Leak", status="proposal", trust="trusted"), encoding="utf-8"
    )
    assert any("quarantined content must be" in f.message for f in _fails(home))


def test_untrusted_doc_in_canonical_tree_fails(tmp_path: Path) -> None:
    home = _minimal_home(tmp_path)
    (home / "briefs").mkdir()
    (home / "briefs" / "draft.md").write_text(
        _FM.format(title="Draft", status="proposal", trust="untrusted"), encoding="utf-8"
    )
    assert any("untrusted doc in canonical tree" in f.message for f in _fails(home))


def test_markdown_missing_frontmatter_fails(tmp_path: Path) -> None:
    home = _minimal_home(tmp_path)
    (home / "sources" / "README.md").write_text("# No frontmatter here\n", encoding="utf-8")
    assert any("frontmatter" in f.message for f in _fails(home))


def test_missing_index_fails(tmp_path: Path) -> None:
    home = _minimal_home(tmp_path)
    (home / "INDEX.md").unlink()
    assert any("INDEX.md is missing" in f.message for f in _fails(home))


# ---------------------------------------------------------------------------
# Scanners degrade gracefully — never hard-fail
# ---------------------------------------------------------------------------

def test_scanners_never_hard_fail() -> None:
    findings = cr.check_scanners()
    assert findings, "expected the optional scanners to be probed"
    assert all(f.severity != cr.FAIL for f in findings)


def test_main_returns_zero_on_conforming_home(tmp_path: Path) -> None:
    assert cr.main([str(_minimal_home(tmp_path))]) == 0


def test_main_usage_error() -> None:
    assert cr.main(["a", "b"]) == 2
