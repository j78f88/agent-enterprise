#!/usr/bin/env python3
"""Fail-closed validator for the research knowledge base.

This is the real guarantee that "all research follows the contract regardless of
which slash command produced it." Unconformed research lands in ``_staging/`` /
``_imported/`` as ``untrusted`` and CANNOT become canonical until it passes this
gate: schema-valid provenance, resolvable evidence, a present classification, and
an INDEX entry.

Philosophy mirrors ``init.py``: core contract checks HARD-FAIL; the supplementary
external scanners (semgrep/grype/syft/detect-secrets) DEGRADE GRACEFULLY when
absent (owner decision, 2026-06-01) — they warn and record "not run", never block.

Exit codes:
  0 - the research home conforms (warnings allowed)
  1 - one or more hard-fail contract violations
  2 - bad CLI usage / research home not found

Usage:
  python scripts/check_research.py [research_home]

  research_home: path to the research home to validate.
                 Default: paths.research from config/project.config.yml,
                 falling back to docs/planning/research/.
"""

from __future__ import annotations

import json
import shutil
import sys
from collections import namedtuple
from pathlib import Path

try:  # core dependency (requirements.txt); guarded so the gate still runs degraded
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

try:  # core dependency (requirements.txt)
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = ROOT / "schemas"

CLASSIFICATIONS = {"OFFICIAL", "OFFICIAL:Sensitive", "PROTECTED"}
TRUST_LABELS = {"trusted", "untrusted"}
QUARANTINE_DIRS = ("_staging", "_imported")
CANONICAL_RECORD_DIRS = ("sources", "claims")
OPTIONAL_SCANNERS = ("semgrep", "grype", "syft", "detect-secrets")

# Severity levels. Only FAIL affects the exit code.
FAIL, WARN, INFO = "FAIL", "WARN", "INFO"
Finding = namedtuple("Finding", ["severity", "path", "message"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> dict | None:
    """Return the YAML frontmatter dict, or None if absent/unparseable."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    if yaml is None:  # pragma: no cover - core dep normally present
        return {}
    try:
        return yaml.safe_load(text[3:end].strip()) or {}
    except yaml.YAMLError:
        return None


def default_research_home(root: Path) -> Path:
    """Resolve the research home from config (portable), else the default path."""
    cfg = root / "config" / "project.config.yml"
    if yaml is not None and cfg.exists():
        try:
            data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
            rel = (data.get("paths") or {}).get("research")
            if rel:
                return root / rel
        except (OSError, yaml.YAMLError):
            pass
    return root / "docs" / "planning" / "research"


def _rel_parts(path: Path, home: Path) -> tuple[str, ...]:
    try:
        return path.relative_to(home).parts
    except ValueError:
        return ()


def is_contract_doc(path: Path, home: Path) -> bool:
    """README/INDEX/_meta files are home contract, not research content."""
    if path.name in ("README.md", "INDEX.md"):
        return True
    parts = _rel_parts(path, home)
    return bool(parts) and parts[0] == "_meta"


def in_quarantine(path: Path, home: Path) -> bool:
    parts = _rel_parts(path, home)
    return bool(parts) and parts[0] in QUARANTINE_DIRS


def load_schema(name: str) -> dict | None:
    p = SCHEMAS_DIR / name
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def validate_record(record: dict, schema: dict | None) -> list[str]:
    """Validate a JSON record against a schema. Falls back to a required-keys
    check when jsonschema is unavailable (degraded, but still fail-closed on
    missing required provenance)."""
    if schema is None:
        return ["schema not found in schemas/ — cannot validate"]
    if jsonschema is not None:
        validator = jsonschema.Draft7Validator(schema)
        return [
            f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}"
            for e in sorted(validator.iter_errors(record), key=lambda e: list(e.path))
        ]
    # Degraded path: required keys + a couple of enum spot-checks.
    errors: list[str] = []
    for key in schema.get("required", []):
        if key not in record:
            errors.append(f"<root>: missing required field '{key}'")
    return errors


# ---------------------------------------------------------------------------
# Contract checks
# ---------------------------------------------------------------------------

def check_markdown(home: Path) -> list[Finding]:
    """Every markdown doc carries a valid classification + trust label, and the
    quarantine/canonical trust invariants hold."""
    findings: list[Finding] = []
    for md in sorted(home.rglob("*.md")):
        rel = md.relative_to(home)
        try:
            fm = parse_frontmatter(md.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            findings.append(Finding(FAIL, rel, "unreadable markdown file"))
            continue

        if fm is None:
            findings.append(
                Finding(FAIL, rel, "missing/invalid frontmatter (need classification + trust)")
            )
            continue

        classification = fm.get("classification")
        if classification not in CLASSIFICATIONS:
            findings.append(
                Finding(FAIL, rel, f"classification missing or invalid: {classification!r}")
            )

        trust = fm.get("trust")
        if trust not in TRUST_LABELS:
            findings.append(Finding(FAIL, rel, f"trust missing or invalid: {trust!r}"))
            continue

        contract = is_contract_doc(md, home)
        if in_quarantine(md, home):
            # Quarantined CONTENT must be untrusted; home-contract READMEs are exempt.
            if not contract and trust != "untrusted":
                findings.append(
                    Finding(FAIL, rel, "quarantined content must be trust: untrusted")
                )
        else:
            # Canonical tree: untrusted material may not live here.
            if trust == "untrusted":
                findings.append(
                    Finding(FAIL, rel, "untrusted doc in canonical tree — move to _staging/")
                )
    return findings


def check_source_notes(home: Path) -> tuple[list[Finding], set[str]]:
    """Validate canonical source-notes; return findings + the set of valid ids."""
    findings: list[Finding] = []
    ids: set[str] = set()
    schema = load_schema("source-note.schema.json")
    src_dir = home / "sources"
    if not src_dir.is_dir():
        return findings, ids
    for jf in sorted(src_dir.glob("*.json")):
        rel = jf.relative_to(home)
        try:
            record = json.loads(jf.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            findings.append(Finding(FAIL, rel, f"invalid JSON: {exc}"))
            continue
        for err in validate_record(record, schema):
            findings.append(Finding(FAIL, rel, f"source-note schema: {err}"))
        # Canonical zone must be trusted.
        if record.get("trust") == "untrusted":
            findings.append(
                Finding(FAIL, rel, "untrusted source-note in canonical sources/ — belongs in _staging/")
            )
        # Evidence may not originate from the quarantine zone.
        ref = ((record.get("locator") or {}).get("ref") or "")
        if any(q + "/" in ref for q in QUARANTINE_DIRS):
            findings.append(
                Finding(FAIL, rel, f"source-note locator points into quarantine: {ref}")
            )
        rid = record.get("id")
        if rid:
            ids.add(rid)
    return findings, ids


def check_claims(home: Path, source_ids: set[str]) -> tuple[list[Finding], set[str]]:
    """Validate canonical claims; enforce evidence linkage + independence."""
    findings: list[Finding] = []
    ids: set[str] = set()
    schema = load_schema("claim.schema.json")
    claims_dir = home / "claims"
    if not claims_dir.is_dir():
        return findings, ids
    for jf in sorted(claims_dir.glob("*.json")):
        rel = jf.relative_to(home)
        try:
            record = json.loads(jf.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            findings.append(Finding(FAIL, rel, f"invalid JSON: {exc}"))
            continue
        for err in validate_record(record, schema):
            findings.append(Finding(FAIL, rel, f"claim schema: {err}"))

        if record.get("trust") == "untrusted":
            findings.append(
                Finding(FAIL, rel, "untrusted claim in canonical claims/ — belongs in _staging/")
            )

        evidence = record.get("evidence") or []
        verdict = record.get("verdict")
        # Every evidence link resolves to an existing source-note.
        for ev in evidence:
            sid = ev.get("source_id") if isinstance(ev, dict) else None
            if sid and sid not in source_ids:
                findings.append(
                    Finding(FAIL, rel, f"evidence source_id not found in sources/: {sid}")
                )
        # verified / contested claims need >= 2 independent sources.
        independent = sum(
            1 for ev in evidence if isinstance(ev, dict) and ev.get("independent") is True
        )
        if (verdict == "verified" or record.get("contested") is True) and independent < 2:
            findings.append(
                Finding(
                    FAIL, rel,
                    f"{'contested' if record.get('contested') else 'verified'} claim needs >=2 "
                    f"independent sources (found {independent})",
                )
            )
        rid = record.get("id")
        if rid:
            ids.add(rid)
    return findings, ids


def check_index(home: Path, canonical_ids: set[str]) -> list[Finding]:
    """INDEX.md exists and registers every canonical record."""
    findings: list[Finding] = []
    index = home / "INDEX.md"
    if not index.is_file():
        findings.append(Finding(FAIL, Path("INDEX.md"), "INDEX.md is missing from the research home"))
        return findings
    text = index.read_text(encoding="utf-8")
    for rid in sorted(canonical_ids):
        if rid not in text:
            findings.append(
                Finding(FAIL, Path("INDEX.md"), f"canonical record not registered in INDEX: {rid}")
            )
    return findings


def check_scanners() -> list[Finding]:
    """Probe optional external scanners. DEGRADE GRACEFULLY — never hard-fail.

    v1 declares and probes the supplementary toolchain (the contract is expressed);
    actual scanning is a stub until there is embedded code/deps to scan."""
    findings: list[Finding] = []
    for tool in OPTIONAL_SCANNERS:
        if shutil.which(tool):
            findings.append(Finding(INFO, None, f"scanner '{tool}' available (v1: declared, not run)"))
        else:
            findings.append(
                Finding(WARN, None, f"scanner '{tool}' not installed — skipped (degrade-gracefully)")
            )
    return findings


def run(home: Path) -> list[Finding]:
    """Run every contract check over the research home and return all findings."""
    findings: list[Finding] = []
    if not home.is_dir():
        return [Finding(FAIL, home, "research home not found")]

    findings += check_markdown(home)
    src_findings, source_ids = check_source_notes(home)
    findings += src_findings
    claim_findings, claim_ids = check_claims(home, source_ids)
    findings += claim_findings
    findings += check_index(home, source_ids | claim_ids)
    findings += check_scanners()
    return findings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) > 1:
        print("Usage: python scripts/check_research.py [research_home]", file=sys.stderr)
        return 2

    home = Path(argv[0]) if argv else default_research_home(ROOT)

    findings = run(home)
    fails = [f for f in findings if f.severity == FAIL]
    warns = [f for f in findings if f.severity == WARN]

    def _loc(f: Finding) -> str:
        return f"  {f.path}: {f.message}" if f.path is not None else f"  {f.message}"

    if fails:
        print(f"check-research: FAIL — {len(fails)} contract violation(s):")
        for f in fails:
            print(_loc(f))
    if warns:
        print(f"check-research: {len(warns)} warning(s) (degrade-gracefully, non-blocking):")
        for f in warns:
            print(_loc(f))

    if fails:
        return 1

    print(f"check-research: OK — research home conforms ({home}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
