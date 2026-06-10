"""Return-tier validation for the Mode 2 dispatcher.

Thin wrapper that REUSES :class:`SubagentReturnValidator` from
``src/phase1_verification/validator.py`` against
``schemas/subagent-return-tier{1,2,3}.schema.json`` — no duplicated
validation logic (Sprint 5 plan, Task Group 3).

The one Mode 2 tightening: the phase-1 validator treats a tier mismatch
as a warning, but per ``command-centre/01-protocols/return-schemas.md``
returning a different tier than declared is a contract violation, so the
wrapper escalates a mismatch to a failure reason.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:  # imported as part of the ``src`` package (pytest, dispatch.py)
    from ..phase1_verification.validator import (
        SubagentReturnValidator,
        ValidationResult,
    )
except ImportError:  # imported with src/mode2_dispatcher/ directly on sys.path
    sys.path.insert(
        0, str(Path(__file__).resolve().parents[1] / "phase1_verification")
    )
    from validator import SubagentReturnValidator, ValidationResult  # type: ignore

__all__ = [
    "SubagentReturnValidator",
    "ValidationResult",
    "make_return_validator",
    "validate_return",
]

#: Repo root (src/mode2_dispatcher/returns.py -> parents[2]). The canonical
#: tier schemas live at ``<root>/schemas/`` — present in a clean clone, so
#: no ``init.py`` build is required.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_SCHEMA_DIR = _REPO_ROOT / "schemas"


def make_return_validator(schema_dir: Path | None = None) -> SubagentReturnValidator:
    """Build a phase-1 return validator bound to the canonical tier schemas."""
    return SubagentReturnValidator(schema_dir=schema_dir or _DEFAULT_SCHEMA_DIR)


def validate_return(
    value: Any,
    expected_tier: int,
    validator: SubagentReturnValidator | None = None,
) -> tuple[bool, list[str]]:
    """Validate a captured callable return against its declared tier.

    Args:
        value: The captured return — a dict, or raw JSON text.
        expected_tier: The tier the callable declared (1-3).
        validator: Optional pre-built validator (avoids reloading schemas
            per call).

    Returns:
        ``(ok, reasons)`` — machine-checkable evidence for the verifier.
        ``ok`` is True only when the return parses, matches the declared
        tier, and validates against that tier's JSON Schema.
    """
    if validator is None:
        validator = make_return_validator()

    if isinstance(value, str):
        text = value
    else:
        try:
            text = json.dumps(value)
        except (TypeError, ValueError) as exc:
            return False, [f"return is not JSON-serialisable: {exc}"]

    result = validator.validate(text, expected_tier=expected_tier)
    reasons = list(result.errors)
    if result.tier != expected_tier:
        reasons.append(
            f"declared return tier {expected_tier} but callable returned "
            f"tier {result.tier!r}"
        )
    return (len(reasons) == 0), reasons
