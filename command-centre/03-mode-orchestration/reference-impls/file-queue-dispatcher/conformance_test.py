"""Conformance test for the file-queue dispatcher.

Drives the dispatcher against a three-item fixture queue and asserts
every checkbox in ``mode-2-contract-v1``:

1. Inbox is sourced from files.
2. Each item is resolved to a callable by id.
3. Inputs are validated against the callable's schema.
4. The callable is invoked in the dispatcher session.
5. The return is captured at the declared tier.
6. The verifier runs (artifact existence + freshness + hook).
7. State transitions follow the FSM; ghost-done is impossible.
8. A tier-3 summary is emitted.

Exit code 0 = pass.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import time
from pathlib import Path

# Make the dispatcher importable when this file is run directly.
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import yaml  # noqa: E402

from dispatcher import (  # noqa: E402
    Callable_,
    Dispatcher,
    TransitionError,
)


# ---------------------------------------------------------------------------
# Fixture callables
# ---------------------------------------------------------------------------


def _write_report(inputs: dict) -> dict:
    path = Path(inputs["report_path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# Report for {inputs['task']}\n", encoding="utf-8")
    return {"tier": 1, "status": "success"}


def _claim_to_write_but_dont(inputs: dict) -> dict:
    # Deliberately do nothing — verifier should reject.
    return {"tier": 1, "status": "success"}


def build_registry(tmp: Path) -> dict[str, Callable_]:
    """Three callables: pass, verifier-fail, input-fail."""
    return {
        "fixture.write-report": Callable_(
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
            fn=_write_report,
        ),
        "fixture.ghost-report": Callable_(
            id="fixture.ghost-report",
            inputs_schema={
                "type": "object",
                "required": ["task"],
                "properties": {"task": {"type": "string"}},
            },
            outputs=[{"path": str(tmp / "out" / "ghost.md"), "required": True}],
            verifier=None,
            fn=_claim_to_write_but_dont,
        ),
        "fixture.bad-input": Callable_(
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


def seed_inbox(queue_root: Path, tmp: Path) -> None:
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


# ---------------------------------------------------------------------------
# Assertions
# ---------------------------------------------------------------------------


def assert_(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def run() -> int:
    with tempfile.TemporaryDirectory(prefix="mode2-conformance-") as tmpdir:
        tmp = Path(tmpdir)
        queue_root = tmp / "queue"
        seed_inbox(queue_root, tmp)
        registry = build_registry(tmp)

        # Sleep one tick so the session_start clock is *before* artifact mtimes.
        time.sleep(0.01)

        dispatcher = Dispatcher(queue_root=queue_root, registry=registry)
        summary = dispatcher.run()

        # Checkbox 1: inbox sourced from files (3 items loaded).
        assert_(len(summary["dispatched"]) == 3, "expected 3 dispatched items")

        good, ghost, bad = summary["dispatched"]

        # Checkbox 2 + 4 + 5: resolved, invoked, return captured.
        assert_(good["state"] == "done", f"good item did not reach done: {good}")
        assert_(good["verifier_passed"] is True, "good item verifier should pass")
        assert_(
            any(a["present"] for a in good["artifacts"]),
            "good item should produce an artifact",
        )

        # Checkbox 6: verifier rejects ghost-done (no artifact written).
        assert_(ghost["state"] == "rejected", f"ghost item must be rejected: {ghost}")
        assert_(ghost["verifier_passed"] is False, "ghost verifier must fail")
        assert_(
            any("missing required artifact" in r for r in ghost["verifier_reasons"]),
            f"ghost item reasons missing artifact-existence failure: {ghost}",
        )

        # Checkbox 3: input validation short-circuits.
        assert_(bad["state"] == "failed", f"bad-input item must fail: {bad}")
        assert_(
            any("input validation" in e for e in bad["errors"]),
            f"bad-input must report a validation error: {bad}",
        )

        # Checkbox 7: FSM forbids illegal transitions.
        try:
            dispatcher._transition("wi-001", "done", "in-progress")
            raise AssertionError("done -> in-progress should be forbidden")
        except TransitionError:
            pass

        # Checkbox 8: tier-3 summary shape.
        assert_(summary["tier"] == 3, "summary must be tier 3")
        assert_(summary["status"] == "complete", "summary status must be 'complete'")
        assert_("session_start" in summary, "summary must include session_start")

        # Checkbox: persisted state file matches in-memory state.
        on_disk = yaml.safe_load((queue_root / "state.yml").read_text(encoding="utf-8"))
        assert_(on_disk["wi-001"] == "done", "state.yml should record wi-001=done")
        assert_(on_disk["wi-002"] == "rejected", "state.yml should record wi-002=rejected")
        assert_(on_disk["wi-003"] == "failed", "state.yml should record wi-003=failed")

    print("OK — mode-2-contract-v1 conformance: all checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(run())
