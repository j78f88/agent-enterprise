"""Supported Mode 2 file-queue dispatcher core.

Ported from the frozen reference impl
``command-centre/03-mode-orchestration/reference-impls/file-queue-dispatcher/dispatcher.py``
(byte-unchanged per ADR 0008 criterion 5 — this is a copy-and-adapt port,
not a refactor of the original). Transition semantics, the ghost-done
verifier, the ``dispatch_one``/``run`` flow, and the tier-3 summary shape
are identical. Production upgrades over the reference:

* **Durable state.** Transitions are journaled and ``state.yml`` is
  written atomically via :class:`~.queue_file.QueueStore`; in-flight
  items are crash-resumed on startup.
* **Ghost-done hardening.** Session end NEVER yields ``done``: the
  verifier demands artifact existence + freshness, the declared verifier
  hook, AND — beyond the reference — a valid return at every declared
  ``return_tier`` (validated by :mod:`.returns`, which reuses the phase-1
  ``SubagentReturnValidator``).
* **Idempotent ``run()``.** Only ``queued`` items are dispatched; items
  already in another state are reported as skipped rather than tripping
  an illegal transition on re-runs.
* **Tolerant inbox.** Malformed inbox files are captured as
  ``inbox_errors`` in the summary instead of aborting the session.

Pure stdlib + jsonschema + PyYAML. No imports from the Mode 1 build tool
(``init.py``) or Mode 3 source trees. Contract: ``mode-2-contract-v1``.
"""

from __future__ import annotations

import importlib
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

import jsonschema
import yaml

from .queue_file import ALLOWED_TRANSITIONS, QueueStore, TransitionError
from .returns import SubagentReturnValidator, make_return_validator, validate_return

# Ported state-machine API (reference impl names). The single source of
# truth lives in queue_file.ALLOWED_TRANSITIONS so the durability layer
# enforces the same table; re-exported here for API parity with the port.
_ALLOWED_TRANSITIONS = ALLOWED_TRANSITIONS

__all__ = [
    "Callable_",
    "DispatchResult",
    "Dispatcher",
    "InvocationError",
    "TransitionError",
    "WorkItem",
    "registry_from_manifests",
    "write_summary",
]


# ---------------------------------------------------------------------------
# Domain types (identical shapes to the reference impl)
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


class InvocationError(RuntimeError):
    """Raised when a callable cannot be invoked in this runtime."""


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


class Dispatcher:
    """File-queue dispatcher. One instance == one session.

    Args:
        queue_root: Directory with ``inbox/*.yml`` work items; durable
            state lives beside it (``state.yml`` + ``journal.ndjson``).
        registry: ``callable id -> Callable_`` (see
            :func:`registry_from_manifests` for building one from
            discovered manifests).
        schema_dir: Override for the return-tier schema directory
            (defaults to the canonical ``schemas/``).
        recover: Passed to :class:`~.queue_file.QueueStore` — True
            re-queues crash-interrupted items on startup.
    """

    def __init__(
        self,
        queue_root: Path,
        registry: dict[str, Callable_],
        schema_dir: Path | None = None,
        recover: bool = True,
    ):
        self.queue_root = Path(queue_root)
        self.registry = registry
        self.store = QueueStore(self.queue_root, recover=recover)
        self.state_path = self.store.state_path
        self.session_start = time.time()
        self.inbox_errors: list[dict] = []
        self._schema_dir = schema_dir
        self._return_validator: SubagentReturnValidator | None = None

    # -- state I/O ----------------------------------------------------------

    @property
    def _state(self) -> dict[str, str]:
        """Current ``item_id -> state`` view (reference-impl parity)."""
        return self.store.states

    def _transition(self, item_id: str, from_state: str, to_state: str) -> None:
        """Apply one contract transition (journaled + atomic via the store)."""
        self.store.transition(item_id, from_state, to_state)

    # -- queue ingestion ----------------------------------------------------

    def load_inbox(self) -> list[WorkItem]:
        """Source work items from ``inbox/*.yml`` (sorted, deterministic).

        Malformed inbox files are recorded in ``self.inbox_errors`` and
        surfaced in the tier-3 summary — never silently dropped, never
        fatal to the session.
        """
        inbox = self.queue_root / "inbox"
        items: list[WorkItem] = []
        for path in sorted(inbox.glob("*.yml")):
            try:
                raw = yaml.safe_load(path.read_text(encoding="utf-8"))
                item = WorkItem(
                    id=str(raw["id"]),
                    callable_id=str(raw["callable_id"]),
                    inputs=raw.get("inputs") or {},
                )
            except Exception as exc:  # noqa: BLE001 - ingestion boundary
                self.inbox_errors.append(
                    {"path": str(path), "error": f"{type(exc).__name__}: {exc}"}
                )
                continue
            items.append(item)
            self.store.ensure(item.id)
        return items

    # -- verifier -----------------------------------------------------------

    def verify(self, callable_: Callable_, result: Any) -> tuple[bool, list[str]]:
        """Ghost-done verifier: evidence decides, never session end.

        Three independent evidence checks, all of which must pass:

        1. Artifact existence + freshness (mtime at/after session start).
        2. Declared ``return_tier`` outputs validate against their tier
           schema (supported-impl hardening over the reference).
        3. The declared verifier hook, if any.
        """
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

        # Declared return tier(s) must validate (no ghost-done via an
        # unverifiable return shape).
        for spec in callable_.outputs:
            if "return_tier" not in spec:
                continue
            tier = spec["return_tier"]
            ok, tier_reasons = validate_return(result, tier, self._validator())
            if not ok:
                reasons.append(
                    f"invalid tier-{tier} return: " + "; ".join(tier_reasons)
                )

        # Hook verifier.
        if callable_.verifier is not None:
            ok, hook_reasons = callable_.verifier(
                {"outputs": callable_.outputs}, result
            )
            reasons.extend(hook_reasons)
            if not ok and not any(r.startswith("HOOK_FAIL") for r in hook_reasons):
                reasons.append("HOOK_FAIL: verifier hook returned False")

        return (len(reasons) == 0), reasons

    def _validator(self) -> SubagentReturnValidator:
        if self._return_validator is None:
            self._return_validator = make_return_validator(self._schema_dir)
        return self._return_validator

    # -- dispatch loop ------------------------------------------------------

    def dispatch_one(self, item: WorkItem) -> DispatchResult:
        """Dispatch a single queued item through the contract FSM."""
        result = DispatchResult(item_id=item.id, state=self.store.get(item.id))

        # 1. Resolve callable.
        callable_ = self.registry.get(item.callable_id)
        if callable_ is None:
            result.errors.append(f"unknown callable id: {item.callable_id}")
            # Stay queued; nothing to transition.
            return result

        # 2. Transition to in-progress (journaled before invocation, so a
        #    crash mid-invoke is recoverable on the next startup).
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
                        # Echo the manifest's declared path verbatim so
                        # summaries are byte-identical across OSes.
                        "path": spec["path"],
                        "required": spec.get("required", True),
                        "present": path.exists(),
                    }
                )

        # 6. Verifier.
        passed, reasons = self.verify(callable_, ret)
        result.verifier_passed = passed
        result.verifier_reasons = reasons

        # 7. Transition. ``done`` requires verifier pass — never session end.
        if passed:
            self._transition(item.id, "in-progress", "done")
            result.state = "done"
        else:
            self._transition(item.id, "in-progress", "rejected")
            result.state = "rejected"

        return result

    def run(self) -> dict:
        """Dispatch every queued inbox item; return a tier-3 summary.

        Idempotent: items already ``done`` / ``rejected`` / ``failed`` are
        skipped (re-queue them explicitly via ``dispatch.py requeue``).
        """
        items = self.load_inbox()
        results: list[DispatchResult] = []
        skipped: list[dict] = []
        for item in items:
            state = self.store.get(item.id)
            if state != "queued":
                skipped.append({"item_id": item.id, "state": state})
                continue
            results.append(self.dispatch_one(item))
        return {
            "tier": 3,
            "status": "complete",
            "contract": "mode-2-contract-v1",
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
            "skipped": skipped,
            "recovered": list(self.store.recovered),
            "inbox_errors": list(self.inbox_errors),
        }


def write_summary(summary: dict, path: Path) -> None:
    """Persist a dispatch summary as pretty, sorted JSON."""
    path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")


# ---------------------------------------------------------------------------
# Registry building (manifest -> Callable_)
# ---------------------------------------------------------------------------


def _resolve_python_entry(entry: str) -> Callable[[dict], Any]:
    """Resolve a ``module:function`` entry point, allowing cwd-local modules."""
    module_name, sep, attr = entry.partition(":")
    if not sep or not module_name or not attr:
        raise InvocationError(
            f"python invocation entry must be 'module:function', got {entry!r}"
        )
    cwd = str(Path.cwd())
    if cwd not in sys.path:
        sys.path.insert(0, cwd)
    try:
        module = importlib.import_module(module_name)
        fn = getattr(module, attr)
    except (ImportError, AttributeError) as exc:
        raise InvocationError(f"cannot resolve python entry {entry!r}: {exc}")
    if not callable(fn):
        raise InvocationError(f"python entry {entry!r} is not callable")
    return fn


def _runner_for(manifest: dict) -> Callable[[dict], Any]:
    """Build the invocation function for one manifest.

    Supported runtime: ``runtime_hints.invocation.type: python`` with
    ``entry: "module:function"``. Any other (or missing) invocation type
    raises :class:`InvocationError` at dispatch time, which the dispatch
    loop records as a ``failed`` item — never a crash, never a ghost-done.
    """
    hints = manifest.get("runtime_hints") or {}
    invocation = hints.get("invocation") or {}
    kind = invocation.get("type")
    callable_id = manifest.get("id")

    if kind == "python":
        entry = str(invocation.get("entry", ""))

        def invoke(inputs: dict, _entry: str = entry) -> Any:
            return _resolve_python_entry(_entry)(inputs)

        return invoke

    def unavailable(inputs: dict, _id=callable_id, _kind=kind) -> Any:
        raise InvocationError(
            f"no runtime available for callable '{_id}' "
            f"(invocation type: {_kind!r}; this dispatcher supports: 'python')"
        )

    return unavailable


def _verifier_hook(
    verifier_callable: Callable_,
) -> Callable[[dict, Any], tuple[bool, list[str]]]:
    """Adapt a verifier *callable* (per the callable contract) to a hook.

    The verifier callable is invoked with
    ``{"outputs": [...], "result": <captured return>}`` and must return a
    mapping ``{"passed": bool, "reasons": [...]}``. Anything else —
    including a raised exception — fails closed with a ``HOOK_FAIL``
    reason (ghost-done protection extends to broken verifiers).
    """

    def hook(context: dict, result: Any) -> tuple[bool, list[str]]:
        try:
            out = verifier_callable.fn(
                {"outputs": context.get("outputs", []), "result": result}
            )
        except Exception as exc:  # noqa: BLE001 - verifier boundary
            return False, [f"HOOK_FAIL: verifier '{verifier_callable.id}' raised: {exc}"]
        if isinstance(out, dict) and "passed" in out:
            return bool(out["passed"]), [str(r) for r in out.get("reasons", [])]
        if isinstance(out, tuple) and len(out) == 2:
            return bool(out[0]), [str(r) for r in out[1]]
        return False, [
            f"HOOK_FAIL: verifier '{verifier_callable.id}' returned an "
            f"unrecognised shape ({type(out).__name__})"
        ]

    return hook


def registry_from_manifests(
    manifests: Iterable[dict],
    runner: Callable[[dict], Callable[[dict], Any]] = _runner_for,
) -> tuple[dict[str, Callable_], list[str]]:
    """Build a callable registry from discovered (schema-valid) manifests.

    Args:
        manifests: callable-v1 manifests (see :mod:`.discovery`).
        runner: Strategy mapping a manifest to its invocation function;
            override to plug in custom runtimes.

    Returns:
        ``(registry, problems)``. Problems (duplicate ids, dangling
        verifier references) are reported, and dangling-verifier callables
        are registered with a fail-closed hook so their items can never
        ghost-done.
    """
    manifests = list(manifests)
    registry: dict[str, Callable_] = {}
    problems: list[str] = []

    for manifest in manifests:
        callable_id = manifest["id"]
        if callable_id in registry:
            problems.append(f"duplicate callable id ignored: {callable_id}")
            continue
        registry[callable_id] = Callable_(
            id=callable_id,
            inputs_schema=manifest.get("inputs") or {},
            outputs=list(manifest.get("outputs") or []),
            verifier=None,
            fn=runner(manifest),
        )

    # Second pass: resolve verifier references between registered callables.
    for manifest in manifests:
        callable_id = manifest["id"]
        ref = manifest.get("verifier")
        if not isinstance(ref, str) or callable_id not in registry:
            continue
        target = registry.get(ref)
        if target is None:
            problems.append(
                f"callable '{callable_id}': verifier '{ref}' not found among "
                f"discovered callables; failing closed"
            )
            registry[callable_id].verifier = (
                lambda context, result, _ref=ref: (
                    False,
                    [f"HOOK_FAIL: verifier callable '{_ref}' unavailable"],
                )
            )
        else:
            registry[callable_id].verifier = _verifier_hook(target)

    return registry, problems
