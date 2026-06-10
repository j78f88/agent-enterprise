"""Callable discovery for the Mode 2 dispatcher.

Two discovery sources, both validated against
``schemas/callable-v1.schema.json``:

* ``*.callable.yml`` sidecar manifests — the non-enterprise path per the
  example in ``command-centre/01-protocols/callable-contract.md``.
* ``callable-v1`` frontmatter in ``*.skill.md`` files — the enterprise
  path. The read-side ``scope -> applies_to`` alias (ADR-0012) is applied
  before validation, matching ``tests/test_protocol_v1_conformance.py``.

Guarantees:

* **Deterministic order.** Candidates are processed sorted by path, so
  repeated runs discover identically.
* **Nothing silently skipped.** Every invalid candidate is reported as a
  :class:`CallableViolation` with its path and the schema violation.

The frontmatter parser is a minimal local mirror of ``init.py``'s
``parse_frontmatter`` rather than an import: ``dispatch.py`` is the Mode 2
runtime and must work in a repo that never ran (or never shipped) the
Mode 1 build tool.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import jsonschema
import yaml

__all__ = [
    "CallableViolation",
    "DiscoveredCallable",
    "discover_callables",
    "parse_frontmatter",
]

#: Repo root (src/mode2_dispatcher/discovery.py -> parents[2]).
_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = _REPO_ROOT / "schemas" / "callable-v1.schema.json"

SIDECAR_SUFFIX = ".callable.yml"
FRONTMATTER_SUFFIX = ".skill.md"


@dataclass(frozen=True)
class DiscoveredCallable:
    """A valid callable manifest and where it came from."""

    path: Path
    source: str  # "sidecar" | "frontmatter"
    manifest: dict


@dataclass(frozen=True)
class CallableViolation:
    """An invalid callable candidate: path + human-readable violation."""

    path: Path
    message: str


def parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter from a markdown file (minimal, local).

    Mirrors ``init.py``'s ``parse_frontmatter`` semantics for the
    frontmatter dict (body text is not needed here). Returns ``{}`` when
    no frontmatter block is present or the YAML is malformed.
    """
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    try:
        fm = yaml.safe_load(text[3:end].strip()) or {}
    except yaml.YAMLError:
        return {}
    return fm if isinstance(fm, dict) else {}


def _normalize(fm: dict) -> dict:
    """Apply the read-side ``scope -> applies_to`` alias (ADR-0012)."""
    if fm and "applies_to" not in fm and "scope" in fm:
        fm = dict(fm)
        fm["applies_to"] = fm["scope"]
    return fm


def _load_validator(schema_path: Path) -> jsonschema.Draft7Validator:
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    return jsonschema.Draft7Validator(schema)


def _candidates(search_paths: Iterable[Path]) -> list[tuple[Path, str]]:
    """Collect (path, source) candidates, sorted by path for determinism."""
    seen: dict[Path, str] = {}
    for raw in search_paths:
        root = Path(raw)
        if root.is_file():
            name = root.name
            if name.endswith(SIDECAR_SUFFIX):
                seen[root.resolve()] = "sidecar"
            elif name.endswith(FRONTMATTER_SUFFIX):
                seen[root.resolve()] = "frontmatter"
            continue
        for path in root.rglob(f"*{SIDECAR_SUFFIX}"):
            seen[path.resolve()] = "sidecar"
        for path in root.rglob(f"*{FRONTMATTER_SUFFIX}"):
            seen[path.resolve()] = "frontmatter"
    return sorted(seen.items(), key=lambda pair: str(pair[0]))


def _load_manifest(path: Path, source: str) -> tuple[dict | None, str | None]:
    """Load one candidate's manifest. Returns (manifest, error)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"unreadable: {exc}"

    if source == "sidecar":
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            return None, f"invalid YAML: {exc}"
        if not isinstance(data, dict):
            return None, (
                f"sidecar manifest must be a YAML mapping, got "
                f"{type(data).__name__}"
            )
        return data, None

    fm = parse_frontmatter(text)
    if not fm:
        return None, "no YAML frontmatter found (expected callable-v1 fields)"
    return _normalize(fm), None


def discover_callables(
    search_paths: Iterable[Path],
    schema_path: Path | None = None,
) -> tuple[list[DiscoveredCallable], list[CallableViolation]]:
    """Discover and validate every callable under ``search_paths``.

    Args:
        search_paths: Directories searched recursively (individual manifest
            files are also accepted, which keeps test fixtures simple).
        schema_path: callable-v1 schema location; defaults to the canonical
            ``schemas/callable-v1.schema.json``.

    Returns:
        ``(callables, violations)``. Discovery order is deterministic
        (sorted by resolved path). Invalid candidates — unreadable files,
        malformed YAML, schema violations, duplicate ids — appear in
        ``violations`` with path + violation text; they are never silently
        skipped.
    """
    validator = _load_validator(schema_path or DEFAULT_SCHEMA_PATH)
    callables: list[DiscoveredCallable] = []
    violations: list[CallableViolation] = []
    ids_seen: dict[str, Path] = {}

    for path, source in _candidates(search_paths):
        manifest, error = _load_manifest(path, source)
        if manifest is None:
            violations.append(CallableViolation(path=path, message=error or "unknown"))
            continue

        schema_errors = sorted(
            validator.iter_errors(manifest), key=lambda e: list(e.absolute_path)
        )
        if schema_errors:
            for err in schema_errors:
                pointer = "/".join(str(p) for p in err.absolute_path) or "(root)"
                violations.append(
                    CallableViolation(
                        path=path,
                        message=f"callable-v1 violation at '{pointer}': {err.message}",
                    )
                )
            continue

        callable_id = manifest["id"]
        if callable_id in ids_seen:
            violations.append(
                CallableViolation(
                    path=path,
                    message=(
                        f"duplicate callable id '{callable_id}' "
                        f"(first declared in {ids_seen[callable_id]})"
                    ),
                )
            )
            continue

        ids_seen[callable_id] = path
        callables.append(
            DiscoveredCallable(path=path, source=source, manifest=manifest)
        )

    return callables, violations
