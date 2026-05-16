"""File-queue reference dispatcher — Mode 2.

Implements every responsibility in
``command-centre/03-mode-orchestration/contract.md``:

* Sources work items from ``queue/inbox/*.yml``.
* Resolves each item to a callable registered in ``callable_registry``.
* Validates inputs against the callable's ``inputs`` JSON Schema.
* Invokes the callable.
* Verifies artifacts (existence + freshness) and runs any declared
  verifier hook.
* Transitions state in ``queue/state.yml``.
* Emits a tier-3 dispatcher summary.

Pure stdlib + jsonschema. No external services. No coupling to Mode 1
or Mode 3 source trees.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import jsonschema
import yaml


# ---------------------------------------------------------------------------
# Domain types
# ---------------------------------------------------------------------------


@dataclass
class Callable_:
    """An invocable unit satisfying ``callable-contract-v1``."""

    id: str
    inputs_schema: dict
    outputs: list[dict]
    verifier: Callable[[dict, Any], tuple[bool, list[str]]] | None
    fn: Callable[[dict], Any]


@dataclass
class WorkItem:
    """A single item in the dispatcher's inbox."""

    id: str
    callable_id: str
    inputs: dict


@dataclass
class DispatchResult:
    """Result of dispatching one work item."""

    item_id: str
    state: str  # queued | in-progress | done | rejected | failed
    return_tier: int = 2
    artifacts: list[dict] = field(default_factory=list)
    verifier_passed: bool | None = None
    verifier_reasons: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


_ALLOWED_TRANSITIONS = {
    "queued": {"in-progress"},
    "in-progress": {"done", "rejected", "failed"},
    "rejected": {"queued"},
    "failed": {"queued"},
    "done": set(),
}


class TransitionError(RuntimeError):
    """Raised when a state transition violates the contract."""


class Dispatcher:
    """File-queue dispatcher. One instance == one session."""

    def __init__(self, queue_root: Path, registry: dict[str, Callable_]):
        self.queue_root = Path(queue_root)
        self.registry = registry
        self.state_path = self.queue_root / "state.yml"
        self.session_start = time.time()
        self._state = self._load_state()

    # -- state I/O ----------------------------------------------------------

    def _load_state(self) -> dict[str, str]:
        if self.state_path.exists():
            return yaml.safe_load(self.state_path.read_text(encoding="utf-8")) or {}
        return {}

    def _save_state(self) -> None:
        self.state_path.write_text(
            yaml.safe_dump(self._state, sort_keys=True), encoding="utf-8"
        )

    def _transition(self, item_id: str, from_state: str, to_state: str) -> None:
        if to_state not in _ALLOWED_TRANSITIONS.get(from_state, set()):
            raise TransitionError(
                f"illegal transition for {item_id}: {from_state} -> {to_state}"
            )
        self._state[item_id] = to_state
        self._save_state()

    # -- queue ingestion ----------------------------------------------------

    def load_inbox(self) -> list[WorkItem]:
        inbox = self.queue_root / "inbox"
        items: list[WorkItem] = []
        for path in sorted(inbox.glob("*.yml")):
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            items.append(
                WorkItem(
                    id=raw["id"], callable_id=raw["callable_id"], inputs=raw.get("inputs", {})
                )
            )
            self._state.setdefault(raw["id"], "queued")
        self._save_state()
        return items

    # -- verifier -----------------------------------------------------------

    def verify(self, callable_: Callable_, result: Any) -> tuple[bool, list[str]]:
        reasons: list[str] = []

        # Artifact existence + freshness.
        for spec in callable_.outputs:
            if "path" not in spec:
                continue
            path = Path(spec["path"])
            required = spec.get("required", True)
            if not path.exists():
                if required:
                    reasons.append(f"missing required artifact: {path}")
                continue
            if path.stat().st_size == 0:
                reasons.append(f"empty artifact: {path}")
                continue
            # Freshness: mtime must be at or after session start. The
            # ghost-done check — never pass solely because the session ended.
            if path.stat().st_mtime < self.session_start - 1:
                reasons.append(f"stale artifact (not written this session): {path}")

        # Hook verifier.
        if callable_.verifier is not None:
            ok, hook_reasons = callable_.verifier(
                {"outputs": callable_.outputs}, result
            )
            reasons.extend(hook_reasons)
            if not ok and not any(r.startswith("HOOK_FAIL") for r in hook_reasons):
                reasons.append("HOOK_FAIL: verifier hook returned False")

        return (len(reasons) == 0), reasons

    # -- dispatch loop ------------------------------------------------------

    def dispatch_one(self, item: WorkItem) -> DispatchResult:
        result = DispatchResult(item_id=item.id, state=self._state[item.id])

        # 1. Resolve callable.
        callable_ = self.registry.get(item.callable_id)
        if callable_ is None:
            result.errors.append(f"unknown callable id: {item.callable_id}")
            # Stay queued; nothing to transition.
            return result

        # 2. Transition to in-progress.
        self._transition(item.id, result.state, "in-progress")
        result.state = "in-progress"

        # 3. Validate inputs.
        try:
            jsonschema.validate(instance=item.inputs, schema=callable_.inputs_schema)
        except jsonschema.ValidationError as e:
            result.errors.append(f"input validation: {e.message}")
            self._transition(item.id, "in-progress", "failed")
            result.state = "failed"
            return result

        # 4. Invoke.
        try:
            ret = callable_.fn(item.inputs)
        except Exception as exc:  # noqa: BLE001 - dispatcher boundary
            result.errors.append(f"invocation error: {exc}")
            self._transition(item.id, "in-progress", "failed")
            result.state = "failed"
            return result

        # 5. Capture artifacts.
        for spec in callable_.outputs:
            if "path" in spec:
                path = Path(spec["path"])
                result.artifacts.append(
                    {
                        "path": str(path),
                        "required": spec.get("required", True),
                        "present": path.exists(),
                    }
                )

        # 6. Verifier.
        passed, reasons = self.verify(callable_, ret)
        result.verifier_passed = passed
        result.verifier_reasons = reasons

        # 7. Transition.
        if passed:
            self._transition(item.id, "in-progress", "done")
            result.state = "done"
        else:
            self._transition(item.id, "in-progress", "rejected")
            result.state = "rejected"

        return result

    def run(self) -> dict:
        """Dispatch every inbox item; return a tier-3 summary."""
        items = self.load_inbox()
        results = [self.dispatch_one(item) for item in items]
        return {
            "tier": 3,
            "status": "complete",
            "session_start": self.session_start,
            "session_end": time.time(),
            "dispatched": [
                {
                    "item_id": r.item_id,
                    "state": r.state,
                    "verifier_passed": r.verifier_passed,
                    "verifier_reasons": r.verifier_reasons,
                    "artifacts": r.artifacts,
                    "errors": r.errors,
                }
                for r in results
            ],
        }


def write_summary(summary: dict, path: Path) -> None:
    path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
