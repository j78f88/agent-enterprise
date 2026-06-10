"""
Mode 2 dispatcher tests (Sprint 5, Task Group 5).

Covers the supported implementation in ``src/mode2_dispatcher/`` plus the
root CLI ``dispatch.py``:

- State machine: the full state x state matrix — every contract-legal
  transition succeeds, every other pair raises ``TransitionError``;
  stale ``from_state`` and unknown items raise; ``done`` is terminal.
- Ghost-done: session end is never evidence — missing/stale artifacts and
  invalid declared-tier returns always reject, never ``done``.
- Crash-resume: a simulated crash mid-dispatch (journaled ``in-progress``
  with no terminal record + torn final journal line) re-queues exactly
  once, heals the journal, and never double-dispatches; snapshots are
  written atomically via ``os.replace`` with no ``.tmp`` residue;
  ``recover=False`` loads are strictly read-only.
- Non-enterprise end-to-end: a ``*.callable.yml`` sidecar with a python
  entry round-trips discovery -> registry -> dispatch -> ``done`` with
  zero enterprise-substrate coupling (no init.py build, no skills/).
- CLI: ``validate-callables`` exit codes + violation reporting,
  ``requeue`` legality, read-only ``status``, ``--queue-root`` containment.
- Discovery: deterministic order, frontmatter path (incl. the ADR-0012
  ``scope -> applies_to`` alias), duplicate-id reporting.

Run with: pytest tests/test_mode2_dispatcher.py -v
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mode2_dispatcher import (
    ALLOWED_TRANSITIONS,
    Callable_,
    Dispatcher,
    QueueStateError,
    QueueStore,
    TransitionError,
    discover_callables,
    registry_from_manifests,
)
from src.mode2_dispatcher import dispatcher as dispatcher_module
from src.mode2_dispatcher import queue_file as queue_file_module

ROOT = Path(__file__).resolve().parents[1]
DISPATCH_CLI = ROOT / "dispatch.py"

STATES = ["queued", "in-progress", "done", "rejected", "failed"]

ALLOWED_PAIRS = [
    (frm, to) for frm in STATES for to in sorted(ALLOWED_TRANSITIONS[frm])
]
ILLEGAL_PAIRS = [
    (frm, to) for frm in STATES for to in STATES
    if to not in ALLOWED_TRANSITIONS[frm]
]

#: A return that satisfies schemas/subagent-return-tier1.schema.json.
VALID_TIER1_RETURN = {
    "tier": 1,
    "agent": "worker",
    "status": "complete",
    "summary": "Completed the assigned work item.",
    "findings": [],
}

#: A return that satisfies schemas/subagent-return-tier2.schema.json —
#: used to prove a tier *mismatch* alone is rejected.
VALID_TIER2_RETURN = {
    "tier": 2,
    "agent": "worker",
    "status": "complete",
    "summary": "Produced the research artifact.",
    "findings": [],
    "artifactPath": "docs/research/note.md",
    "artifactType": "research",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

#: Contract-legal route from a fresh enqueue to each state.
_ROUTE_TO = {
    "queued": [],
    "in-progress": [("queued", "in-progress")],
    "done": [("queued", "in-progress"), ("in-progress", "done")],
    "rejected": [("queued", "in-progress"), ("in-progress", "rejected")],
    "failed": [("queued", "in-progress"), ("in-progress", "failed")],
}


def drive_to(store: QueueStore, item_id: str, state: str) -> None:
    """Put ``item_id`` into ``state`` using only contract-legal transitions."""
    store.ensure(item_id)
    for frm, to in _ROUTE_TO[state]:
        store.transition(item_id, frm, to)
    assert store.get(item_id) == state


def write_inbox(queue_root: Path, items: list[dict]) -> None:
    inbox = queue_root / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    for index, item in enumerate(items, 1):
        (inbox / f"{index:02d}-{item['id']}.yml").write_text(
            yaml.safe_dump(item), encoding="utf-8"
        )


def fabricate_crash(queue_root: Path, item_id: str = "wi-1", torn_tail: bool = True) -> None:
    """Simulate a crash mid-dispatch.

    The journal records the item entering ``in-progress`` with no terminal
    record, the snapshot is stale (still ``queued``), and — when
    ``torn_tail`` — the process died mid-append, leaving a torn final line.
    """
    queue_root.mkdir(parents=True, exist_ok=True)
    records = [
        {"seq": 1, "at": 1.0, "item": item_id, "from": None, "to": "queued", "note": "enqueued"},
        {"seq": 2, "at": 2.0, "item": item_id, "from": "queued", "to": "in-progress", "note": ""},
    ]
    text = "".join(json.dumps(r, sort_keys=True) + "\n" for r in records)
    if torn_tail:
        text += '{"seq": 3, "at": 3.0, "item": "wi-'  # crash mid-append: no newline
    (queue_root / "journal.ndjson").write_text(text, encoding="utf-8")
    # Stale snapshot: the crash happened after the journal append but the
    # snapshot never caught up past "queued".
    (queue_root / "state.yml").write_text(
        yaml.safe_dump({item_id: "queued"}), encoding="utf-8"
    )


def run_cli(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run(
        [sys.executable, str(DISPATCH_CLI), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )


WORKER_MODULE_SOURCE = '''\
"""Plain-python worker used by Mode 2 dispatcher tests (no substrate)."""

import pathlib


def run(inputs):
    path = pathlib.Path(inputs["note_path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("note: " + inputs["note_path"] + "\\n", encoding="utf-8")
    return {
        "tier": 1,
        "agent": "note-worker",
        "status": "complete",
        "summary": "Wrote the requested note artifact.",
        "findings": [],
    }
'''


def make_sidecar_manifest(
    callable_id: str = "acme.write-note",
    entry: str | None = None,
    outputs: list[dict] | None = None,
) -> dict:
    """A sidecar manifest per callable-contract.md's non-enterprise example,
    completed with the fields callable-v1 requires (kind/version/applies_to)."""
    manifest = {
        "id": callable_id,
        "kind": "callable",
        "version": "1.0.0",
        "applies_to": "**",
        "name": "Write note",
        "description": "Write a note artifact from inputs.",
        "inputs": {
            "type": "object",
            "required": ["note_path"],
            "properties": {"note_path": {"type": "string"}},
        },
        "outputs": outputs or [{"path": "out/note.md", "required": True}],
        "verifier": None,
    }
    if entry is not None:
        manifest["runtime_hints"] = {"invocation": {"type": "python", "entry": entry}}
    return manifest


def make_project(project: Path, module_name: str = "note_worker") -> Path:
    """A minimal non-enterprise project: sidecar + worker module + queue.

    Deliberately contains NO enterprise substrate: no init.py, no skills/,
    no resolved/, no config/.
    """
    project.mkdir(parents=True, exist_ok=True)
    callables = project / "callables"
    callables.mkdir()
    (callables / "write-note.callable.yml").write_text(
        yaml.safe_dump(
            make_sidecar_manifest(
                entry=f"{module_name}:run",
                outputs=[
                    {"path": "out/note.md", "required": True},
                    {"return_tier": 1},
                ],
            )
        ),
        encoding="utf-8",
    )
    (project / f"{module_name}.py").write_text(WORKER_MODULE_SOURCE, encoding="utf-8")
    write_inbox(
        project / "queue",
        [
            {
                "id": "wi-note-1",
                "callable_id": "acme.write-note",
                "inputs": {"note_path": "out/note.md"},
            }
        ],
    )
    return project


# ---------------------------------------------------------------------------
# 1. State machine
# ---------------------------------------------------------------------------


class TestStateMachine:
    """The mode-2-contract-v1 FSM, enforced by the durable store."""

    def test_matrix_is_fully_partitioned(self):
        """Sanity: allowed + illegal pairs cover the whole 5x5 matrix."""
        assert len(ALLOWED_PAIRS) == 6
        assert len(ILLEGAL_PAIRS) == 19
        assert sorted(ALLOWED_PAIRS + ILLEGAL_PAIRS) == sorted(
            (f, t) for f in STATES for t in STATES
        )

    @pytest.mark.parametrize(
        "frm,to", ALLOWED_PAIRS, ids=[f"{f}->{t}" for f, t in ALLOWED_PAIRS]
    )
    def test_allowed_transition_succeeds(self, tmp_path, frm, to):
        store = QueueStore(tmp_path / "queue")
        drive_to(store, "wi-1", frm)
        store.transition("wi-1", frm, to)
        assert store.get("wi-1") == to

    @pytest.mark.parametrize(
        "frm,to", ILLEGAL_PAIRS, ids=[f"{f}->{t}" for f, t in ILLEGAL_PAIRS]
    )
    def test_illegal_transition_raises(self, tmp_path, frm, to):
        store = QueueStore(tmp_path / "queue")
        drive_to(store, "wi-1", frm)
        with pytest.raises(TransitionError):
            store.transition("wi-1", frm, to)
        assert store.get("wi-1") == frm  # state untouched on refusal

    def test_stale_from_state_raises(self, tmp_path):
        store = QueueStore(tmp_path / "queue")
        drive_to(store, "wi-1", "queued")
        with pytest.raises(TransitionError, match="stale transition"):
            store.transition("wi-1", "in-progress", "done")
        assert store.get("wi-1") == "queued"

    def test_unknown_item_raises(self, tmp_path):
        store = QueueStore(tmp_path / "queue")
        with pytest.raises(TransitionError, match="unknown item"):
            store.transition("wi-ghost", "queued", "in-progress")
        with pytest.raises(TransitionError, match="unknown item"):
            store.requeue("wi-ghost")

    def test_done_is_terminal_requeue_refused(self, tmp_path):
        store = QueueStore(tmp_path / "queue")
        drive_to(store, "wi-1", "done")
        with pytest.raises(TransitionError, match="illegal transition"):
            store.requeue("wi-1")
        assert store.get("wi-1") == "done"

    @pytest.mark.parametrize("frm", ["failed", "rejected"])
    def test_requeue_paths_are_legal(self, tmp_path, frm):
        store = QueueStore(tmp_path / "queue")
        drive_to(store, "wi-1", frm)
        store.requeue("wi-1")
        assert store.get("wi-1") == "queued"

    def test_dispatcher_reexports_reference_state_machine_api(self):
        """The port keeps the reference impl's names; queue_file is the
        single source of truth."""
        assert dispatcher_module._ALLOWED_TRANSITIONS is queue_file_module.ALLOWED_TRANSITIONS
        assert dispatcher_module.TransitionError is queue_file_module.TransitionError


# ---------------------------------------------------------------------------
# 2. Ghost-done
# ---------------------------------------------------------------------------


class TestGhostDone:
    """Session end is never evidence — verification decides ``done``."""

    @staticmethod
    def _dispatch(tmp_path: Path, callable_: Callable_) -> tuple[Dispatcher, dict]:
        queue_root = tmp_path / "queue"
        write_inbox(
            queue_root,
            [{"id": "wi-1", "callable_id": callable_.id, "inputs": {}}],
        )
        dispatcher = Dispatcher(queue_root, {callable_.id: callable_})
        return dispatcher, dispatcher.run()

    def test_session_end_without_artifact_is_rejected_never_done(self, tmp_path):
        artifact = tmp_path / "out" / "report.md"
        ghost = Callable_(
            id="fixture.ghost",
            inputs_schema={"type": "object"},
            outputs=[{"path": str(artifact), "required": True}],
            verifier=None,
            fn=lambda inputs: dict(VALID_TIER1_RETURN),  # claims success, writes nothing
        )
        dispatcher, summary = self._dispatch(tmp_path, ghost)
        (entry,) = summary["dispatched"]
        assert entry["state"] == "rejected"
        assert entry["state"] != "done"
        assert entry["verifier_passed"] is False
        assert any("missing required artifact" in r for r in entry["verifier_reasons"])
        assert dispatcher.store.get("wi-1") == "rejected"
        on_disk = yaml.safe_load(
            (tmp_path / "queue" / "state.yml").read_text(encoding="utf-8")
        )
        assert on_disk["wi-1"] == "rejected"

    def test_stale_artifact_is_rejected(self, tmp_path):
        """An artifact from a *previous* session is not this session's evidence."""
        artifact = tmp_path / "out" / "report.md"
        artifact.parent.mkdir(parents=True)
        artifact.write_text("old content\n", encoding="utf-8")
        old = time.time() - 3600
        os.utime(artifact, (old, old))
        lazy = Callable_(
            id="fixture.lazy",
            inputs_schema={"type": "object"},
            outputs=[{"path": str(artifact), "required": True}],
            verifier=None,
            fn=lambda inputs: dict(VALID_TIER1_RETURN),  # does not rewrite it
        )
        _, summary = self._dispatch(tmp_path, lazy)
        (entry,) = summary["dispatched"]
        assert entry["state"] == "rejected"
        assert any("stale artifact" in r for r in entry["verifier_reasons"])

    def test_invalid_declared_tier_return_rejected_with_schema_reasons(self, tmp_path):
        """A return that fails the declared tier schema can never ghost-done."""
        bad_return = Callable_(
            id="fixture.bad-return",
            inputs_schema={"type": "object"},
            outputs=[{"return_tier": 1}],
            verifier=None,
            fn=lambda inputs: {"tier": 1, "status": "success"},  # not tier-1 valid
        )
        _, summary = self._dispatch(tmp_path, bad_return)
        (entry,) = summary["dispatched"]
        assert entry["state"] == "rejected"
        assert entry["verifier_passed"] is False
        tier_reasons = [r for r in entry["verifier_reasons"] if "invalid tier-1 return" in r]
        assert tier_reasons, entry["verifier_reasons"]
        assert any("Schema violation" in r for r in tier_reasons)

    def test_tier_mismatch_alone_is_rejected(self, tmp_path):
        """A schema-valid return at the WRONG tier is a contract violation."""
        mismatched = Callable_(
            id="fixture.tier-mismatch",
            inputs_schema={"type": "object"},
            outputs=[{"return_tier": 1}],
            verifier=None,
            fn=lambda inputs: dict(VALID_TIER2_RETURN),  # valid tier 2, declared tier 1
        )
        _, summary = self._dispatch(tmp_path, mismatched)
        (entry,) = summary["dispatched"]
        assert entry["state"] == "rejected"
        assert any(
            "declared return tier 1" in r and "tier 2" in r
            for r in entry["verifier_reasons"]
        )

    def test_real_evidence_reaches_done(self, tmp_path):
        """Positive control: artifact + valid declared-tier return == done."""
        artifact = tmp_path / "out" / "report.md"

        def fn(inputs):
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text("# report\n", encoding="utf-8")
            return dict(VALID_TIER1_RETURN)

        worker = Callable_(
            id="fixture.worker",
            inputs_schema={"type": "object"},
            outputs=[{"path": str(artifact), "required": True}, {"return_tier": 1}],
            verifier=None,
            fn=fn,
        )
        dispatcher, summary = self._dispatch(tmp_path, worker)
        (entry,) = summary["dispatched"]
        assert entry["state"] == "done"
        assert entry["verifier_passed"] is True
        assert dispatcher.store.get("wi-1") == "done"


# ---------------------------------------------------------------------------
# 3. Crash-resume + durability
# ---------------------------------------------------------------------------


class TestCrashResume:
    """Journal + atomic snapshot semantics (the headline upgrade over the
    reference impl's plain state.yml rewrite)."""

    def test_in_flight_item_requeued_exactly_once(self, tmp_path):
        queue_root = tmp_path / "queue"
        fabricate_crash(queue_root, "wi-1")
        store = QueueStore(queue_root, recover=True)
        assert store.recovered == ["wi-1"]
        assert store.get("wi-1") == "queued"
        # Exactly one crash-resume requeue in the journal.
        records = [
            json.loads(line)
            for line in (queue_root / "journal.ndjson")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]
        requeues = [r for r in records if r["note"] == "crash-resume: requeued"]
        assert len(requeues) == 1
        # A second restart finds nothing in flight: recovery is not repeated.
        store2 = QueueStore(queue_root, recover=True)
        assert store2.recovered == []
        assert store2.get("wi-1") == "queued"

    def test_journal_heals_torn_tail(self, tmp_path):
        queue_root = tmp_path / "queue"
        fabricate_crash(queue_root, "wi-1", torn_tail=True)
        QueueStore(queue_root, recover=True)
        text = (queue_root / "journal.ndjson").read_text(encoding="utf-8")
        assert text.endswith("\n")
        for line in text.splitlines():
            json.loads(line)  # every surviving line is a complete record
        assert '{"seq": 3, "at": 3.0' not in text  # the torn fragment is gone

    def test_corruption_other_than_torn_tail_raises(self, tmp_path):
        queue_root = tmp_path / "queue"
        queue_root.mkdir(parents=True)
        good = json.dumps(
            {"seq": 2, "at": 2.0, "item": "wi-1", "from": None, "to": "queued", "note": ""}
        )
        (queue_root / "journal.ndjson").write_text(
            "{this is not json}\n" + good + "\n", encoding="utf-8"
        )
        with pytest.raises(QueueStateError, match="corrupt journal"):
            QueueStore(queue_root)

    def test_no_duplicate_dispatch_after_crash_resume(self, tmp_path):
        queue_root = tmp_path / "queue"
        artifact = tmp_path / "out" / "note.md"
        calls: list[dict] = []

        def fn(inputs):
            calls.append(inputs)
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text("note\n", encoding="utf-8")
            return dict(VALID_TIER1_RETURN)

        registry = {
            "fixture.worker": Callable_(
                id="fixture.worker",
                inputs_schema={"type": "object"},
                outputs=[{"path": str(artifact), "required": True}],
                verifier=None,
                fn=fn,
            )
        }
        write_inbox(queue_root, [{"id": "wi-1", "callable_id": "fixture.worker", "inputs": {}}])
        fabricate_crash(queue_root, "wi-1")

        # Restart after the crash: the item is recovered and dispatched ONCE.
        summary = Dispatcher(queue_root, registry).run()
        assert summary["recovered"] == ["wi-1"]
        assert [e["item_id"] for e in summary["dispatched"]] == ["wi-1"]
        assert summary["dispatched"][0]["state"] == "done"
        assert len(calls) == 1

        # Re-running the drained queue dispatches nothing (idempotent).
        summary2 = Dispatcher(queue_root, registry).run()
        assert summary2["dispatched"] == []
        assert summary2["skipped"] == [{"item_id": "wi-1", "state": "done"}]
        assert len(calls) == 1

    def test_snapshot_written_atomically_via_replace(self, tmp_path, monkeypatch):
        """state.yml is only ever produced by os.replace from a .tmp file,
        and the .tmp never survives — a torn snapshot is impossible."""
        queue_root = tmp_path / "queue"
        replaces: list[tuple[str, str]] = []
        real_replace = os.replace

        def recording_replace(src, dst, *args, **kwargs):
            replaces.append((str(src), str(dst)))
            return real_replace(src, dst, *args, **kwargs)

        monkeypatch.setattr(queue_file_module.os, "replace", recording_replace)
        store = QueueStore(queue_root)
        drive_to(store, "wi-1", "done")
        drive_to(store, "wi-2", "failed")
        store.requeue("wi-2")

        snapshot_writes = [
            (src, dst) for src, dst in replaces if dst.endswith("state.yml")
        ]
        assert snapshot_writes, "snapshot was never written through os.replace"
        assert all(src.endswith("state.yml.tmp") for src, _ in snapshot_writes)
        assert list(queue_root.glob("*.tmp")) == []  # no residue
        on_disk = yaml.safe_load((queue_root / "state.yml").read_text(encoding="utf-8"))
        assert on_disk == {"wi-1": "done", "wi-2": "queued"}

    def test_recover_false_is_read_only_and_reports_pending(self, tmp_path):
        queue_root = tmp_path / "queue"
        fabricate_crash(queue_root, "wi-1")
        state_before = (queue_root / "state.yml").read_bytes()
        journal_before = (queue_root / "journal.ndjson").read_bytes()
        mtimes_before = {
            name: (queue_root / name).stat().st_mtime_ns
            for name in ("state.yml", "journal.ndjson")
        }

        store = QueueStore(queue_root, recover=False)
        assert store.pending_recovery == ["wi-1"]
        assert store.recovered == []
        # The in-memory view reflects the journal (in-progress)...
        assert store.get("wi-1") == "in-progress"
        # ...but nothing on disk moved: bytes and mtimes identical.
        assert (queue_root / "state.yml").read_bytes() == state_before
        assert (queue_root / "journal.ndjson").read_bytes() == journal_before
        assert {
            name: (queue_root / name).stat().st_mtime_ns
            for name in ("state.yml", "journal.ndjson")
        } == mtimes_before
        assert list(queue_root.glob("*.tmp")) == []


# ---------------------------------------------------------------------------
# 4. Non-enterprise end-to-end
# ---------------------------------------------------------------------------


class TestNonEnterpriseEndToEnd:
    """A *.callable.yml sidecar round-trips with zero substrate coupling."""

    E2E_MODULE = "e2e_note_worker"

    @pytest.fixture
    def isolated_imports(self):
        saved_path = list(sys.path)
        yield
        sys.path[:] = saved_path
        sys.modules.pop(self.E2E_MODULE, None)

    def test_sidecar_callable_round_trip(self, tmp_path, monkeypatch, isolated_imports):
        project = make_project(tmp_path / "proj", module_name=self.E2E_MODULE)

        # Zero enterprise coupling: no Mode 1 build tool, no substrate dirs.
        assert not (project / "init.py").exists()
        assert not (project / "skills").exists()
        assert not (project / "resolved").exists()

        monkeypatch.chdir(project)

        callables, violations = discover_callables([project / "callables"])
        assert violations == []
        assert [c.manifest["id"] for c in callables] == ["acme.write-note"]
        assert callables[0].source == "sidecar"

        registry, problems = registry_from_manifests(c.manifest for c in callables)
        assert problems == []

        summary = Dispatcher(Path("queue"), registry).run()
        (entry,) = summary["dispatched"]
        assert entry["item_id"] == "wi-note-1"
        assert entry["state"] == "done"
        assert entry["verifier_passed"] is True
        assert entry["artifacts"] == [
            {"path": "out/note.md", "required": True, "present": True}
        ]
        assert summary["tier"] == 3
        assert summary["status"] == "complete"
        assert summary["inbox_errors"] == []
        assert (project / "out" / "note.md").read_text(encoding="utf-8").startswith("note:")
        on_disk = yaml.safe_load((project / "queue" / "state.yml").read_text(encoding="utf-8"))
        assert on_disk == {"wi-note-1": "done"}


# ---------------------------------------------------------------------------
# 5. CLI (subprocess against dispatch.py)
# ---------------------------------------------------------------------------


class TestDispatchCli:
    """python dispatch.py, run with cwd at a non-enterprise tmp project."""

    def test_validate_callables_exit_0_on_valid(self, tmp_path):
        project = make_project(tmp_path / "proj")
        result = run_cli(["validate-callables"], cwd=project)
        assert result.returncode == 0, result.stderr
        assert "OK: acme.write-note (sidecar)" in result.stdout
        assert "1 callable(s) valid." in result.stdout

    def test_validate_callables_exit_1_with_path_and_violation(self, tmp_path):
        project = tmp_path / "proj"
        bad = project / "callables" / "broken.callable.yml"
        bad.parent.mkdir(parents=True)
        bad.write_text(
            yaml.safe_dump({"id": "acme.broken", "inputs": {"type": "object"}}),
            encoding="utf-8",
        )
        result = run_cli(["validate-callables"], cwd=project)
        assert result.returncode == 1
        assert "VIOLATION:" in result.stderr
        assert str(bad.resolve()) in result.stderr
        assert "callable-v1 violation" in result.stderr
        assert "ERROR:" in result.stderr

    def test_run_drains_queue_then_skips_on_rerun(self, tmp_path):
        project = make_project(tmp_path / "proj")
        result = run_cli(["run", "--callables", "callables"], cwd=project)
        assert result.returncode == 0, result.stderr
        summary = json.loads(result.stdout)
        assert summary["tier"] == 3
        assert summary["dispatched"][0]["state"] == "done"
        assert (project / "out" / "note.md").is_file()

        rerun = run_cli(["run", "--callables", "callables"], cwd=project)
        assert rerun.returncode == 0, rerun.stderr
        summary2 = json.loads(rerun.stdout)
        assert summary2["dispatched"] == []
        assert summary2["skipped"] == [{"item_id": "wi-note-1", "state": "done"}]

    def test_requeue_failed_item_exit_0(self, tmp_path):
        project = tmp_path / "proj"
        queue = project / "queue"
        queue.mkdir(parents=True)
        (queue / "state.yml").write_text(
            yaml.safe_dump({"wi-1": "failed"}), encoding="utf-8"
        )
        result = run_cli(["requeue", "wi-1"], cwd=project)
        assert result.returncode == 0, result.stderr
        assert "OK: wi-1 -> queued" in result.stdout
        on_disk = yaml.safe_load((queue / "state.yml").read_text(encoding="utf-8"))
        assert on_disk == {"wi-1": "queued"}

    @pytest.mark.parametrize("state", ["done", "queued", "in-progress"])
    def test_requeue_rejects_illegal_transition_exit_1(self, tmp_path, state):
        project = tmp_path / "proj"
        queue = project / "queue"
        queue.mkdir(parents=True)
        (queue / "state.yml").write_text(
            yaml.safe_dump({"wi-1": state}), encoding="utf-8"
        )
        result = run_cli(["requeue", "wi-1"], cwd=project)
        assert result.returncode == 1
        assert "ERROR:" in result.stderr
        assert "illegal transition" in result.stderr
        on_disk = yaml.safe_load((queue / "state.yml").read_text(encoding="utf-8"))
        assert on_disk == {"wi-1": state}  # nothing moved

    def test_status_is_read_only(self, tmp_path):
        project = tmp_path / "proj"
        queue = project / "queue"
        queue.mkdir(parents=True)
        (queue / "state.yml").write_text(
            yaml.safe_dump({"wi-1": "in-progress", "wi-2": "done"}), encoding="utf-8"
        )
        bytes_before = (queue / "state.yml").read_bytes()

        result = run_cli(["status"], cwd=project)
        assert result.returncode == 0, result.stderr
        assert "wi-1: in-progress" in result.stdout
        assert "wi-2: done" in result.stdout
        assert "in-flight" in result.stdout and "wi-1" in result.stdout
        # Read-only: snapshot untouched, no journal created, no tmp residue.
        assert (queue / "state.yml").read_bytes() == bytes_before
        assert not (queue / "journal.ndjson").exists()
        assert list(queue.glob("*.tmp")) == []

    @pytest.mark.parametrize(
        "queue_root,needle",
        [
            ("../outside", "refusing path traversal"),
            ("sub/../../outside", "refusing path traversal"),
        ],
    )
    def test_queue_root_traversal_refused(self, tmp_path, queue_root, needle):
        project = tmp_path / "proj"
        project.mkdir()
        result = run_cli(["status", "--queue-root", queue_root], cwd=project)
        assert result.returncode == 1
        assert needle in result.stderr

    def test_queue_root_absolute_escape_refused(self, tmp_path):
        project = tmp_path / "proj"
        project.mkdir()
        elsewhere = tmp_path / "elsewhere"  # sibling of cwd: outside it
        result = run_cli(["status", "--queue-root", str(elsewhere)], cwd=project)
        assert result.returncode == 1
        assert "escapes the working directory" in result.stderr
        assert not elsewhere.exists()  # refused before any queue I/O


# ---------------------------------------------------------------------------
# 6. Discovery
# ---------------------------------------------------------------------------


FRONTMATTER_SKILL = """\
---
id: acme.research-skill
kind: skill
version: 1.0.0
scope: "docs/**"
name: Research Skill
description: Research a topic and report findings.
inputs:
  type: object
  required: [topic]
  properties:
    topic: { type: string }
outputs:
  - return_tier: 1
verifier: null
---

# Research Skill

Body text (not part of the manifest).
"""


class TestDiscovery:
    def _seed(self, root: Path) -> None:
        (root / "b-dir").mkdir(parents=True)
        (root / "a-dir").mkdir(parents=True)
        (root / "b-dir" / "zeta.callable.yml").write_text(
            yaml.safe_dump(make_sidecar_manifest("acme.zeta")), encoding="utf-8"
        )
        (root / "a-dir" / "alpha.callable.yml").write_text(
            yaml.safe_dump(make_sidecar_manifest("acme.alpha")), encoding="utf-8"
        )
        (root / "a-dir" / "research.skill.md").write_text(
            FRONTMATTER_SKILL, encoding="utf-8"
        )

    def test_discovery_order_is_deterministic_across_runs(self, tmp_path):
        self._seed(tmp_path)
        first, v1 = discover_callables([tmp_path])
        second, v2 = discover_callables([tmp_path])
        assert [c.path for c in first] == [c.path for c in second]
        assert v1 == v2 == []
        paths = [str(c.path) for c in first]
        assert paths == sorted(paths)
        assert [c.manifest["id"] for c in first] == [
            "acme.alpha",
            "acme.research-skill",
            "acme.zeta",
        ]

    def test_frontmatter_skill_discovered_with_scope_alias(self, tmp_path):
        skill = tmp_path / "research.skill.md"
        skill.write_text(FRONTMATTER_SKILL, encoding="utf-8")
        callables, violations = discover_callables([tmp_path])
        assert violations == []
        (found,) = callables
        assert found.source == "frontmatter"
        assert found.manifest["id"] == "acme.research-skill"
        # ADR-0012 read-side alias: scope surfaced as applies_to, so the
        # manifest validated against callable-v1.
        assert found.manifest["applies_to"] == "docs/**"

    def test_duplicate_callable_id_is_a_violation(self, tmp_path):
        first = tmp_path / "one.callable.yml"
        second = tmp_path / "two.callable.yml"
        first.write_text(
            yaml.safe_dump(make_sidecar_manifest("acme.same")), encoding="utf-8"
        )
        second.write_text(
            yaml.safe_dump(make_sidecar_manifest("acme.same")), encoding="utf-8"
        )
        callables, violations = discover_callables([tmp_path])
        assert [c.manifest["id"] for c in callables] == ["acme.same"]
        assert callables[0].path == first.resolve()
        (violation,) = violations
        assert violation.path == second.resolve()
        assert "duplicate callable id 'acme.same'" in violation.message
        assert str(first.resolve()) in violation.message

    def test_invalid_sidecar_reported_with_path_and_violation(self, tmp_path):
        bad = tmp_path / "broken.callable.yml"
        bad.write_text(
            yaml.safe_dump({"id": "acme.broken", "inputs": {"type": "object"}}),
            encoding="utf-8",
        )
        callables, violations = discover_callables([tmp_path])
        assert callables == []
        assert violations  # never silently skipped
        assert all(v.path == bad.resolve() for v in violations)
        assert any("callable-v1 violation" in v.message for v in violations)

    def test_skill_without_frontmatter_reported(self, tmp_path):
        bare = tmp_path / "bare.skill.md"
        bare.write_text("# Just a heading, no frontmatter\n", encoding="utf-8")
        callables, violations = discover_callables([tmp_path])
        assert callables == []
        (violation,) = violations
        assert violation.path == bare.resolve()
        assert "no YAML frontmatter" in violation.message
