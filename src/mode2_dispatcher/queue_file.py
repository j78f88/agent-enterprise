"""Durable file-backed queue state for the Mode 2 dispatcher.

Crash-safety design (the headline improvement over the reference impl's
plain ``state.yml`` rewrite):

* **Atomic snapshot.** ``state.yml`` is written via write-temp + fsync +
  ``os.replace`` — atomic on both POSIX and Windows, so a crash never
  leaves a torn snapshot.
* **Append-only journal.** Every transition is appended (and fsynced) to
  ``journal.ndjson`` *before* the snapshot is rewritten, so the journal is
  always at least as new as the snapshot.
* **Crash-resume.** On startup the journal is replayed and reconciled
  against the snapshot (the journal wins on divergence). Items left
  ``in-progress`` with no terminal record are re-queued through
  contract-legal transitions only — ``in-progress -> failed -> queued``
  per ``mode-2-contract-v1`` — never by editing state out-of-band.
* **Torn-tail tolerance.** A corrupt *final* journal line (crash
  mid-append) is dropped; corruption anywhere else raises
  :class:`QueueStateError`.

The store also honours the ``.mode-2-pins`` contract pin file (see the
Mode 2 install contract): if pins are recorded for an unsupported
``mode-2-contract`` / ``protocol`` version, loading refuses with a clear
error.

Single-writer assumption: one dispatcher process per queue root (the same
posture as the reference impl). Contract:
``command-centre/03-mode-orchestration/contract.md``.
"""

from __future__ import annotations

import json
import os
import re
import time
from collections import Counter
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# State machine (mode-2-contract-v1, "Required state transitions")
# ---------------------------------------------------------------------------

#: Allowed transitions per the contract table. ``failed -> queued`` and
#: ``rejected -> queued`` are the only re-queue paths; ``done`` is terminal.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "queued": {"in-progress"},
    "in-progress": {"done", "rejected", "failed"},
    "rejected": {"queued"},
    "failed": {"queued"},
    "done": set(),
}


class TransitionError(RuntimeError):
    """Raised when a state transition violates the contract."""


class QueueStateError(RuntimeError):
    """Raised when persisted queue state cannot be loaded safely."""


# ---------------------------------------------------------------------------
# Contract pins (.mode-2-pins)
# ---------------------------------------------------------------------------

PIN_FILE = ".mode-2-pins"

#: Contract families this implementation supports, mapped to the supported
#: version. Breaking contract changes bump these (ADR 0003).
SUPPORTED_PINS = {"mode-2-contract": 1, "protocol": 1}

_PIN_RE = re.compile(r"\b(mode-2-contract|protocol)-v(\d+)\b")


def read_pins(queue_root: Path) -> tuple[list[str], Path | None]:
    """Read contract pins from ``.mode-2-pins``.

    Looks in ``queue_root`` first, then its parent (the typical project
    root when the queue lives at ``<project>/queue/``). Returns
    ``(sorted pin tags, pin file path or None)``.
    """
    queue_root = Path(queue_root)
    for candidate in (queue_root / PIN_FILE, queue_root.parent / PIN_FILE):
        if candidate.is_file():
            text = candidate.read_text(encoding="utf-8")
            pins = sorted({m.group(0) for m in _PIN_RE.finditer(text)})
            return pins, candidate
    return [], None


def check_pins(pins: list[str], pin_path: Path | None) -> None:
    """Refuse to operate against pins this implementation does not satisfy."""
    for pin in pins:
        match = _PIN_RE.fullmatch(pin)
        if match is None:  # pragma: no cover - read_pins only yields matches
            continue
        family, version = match.group(1), int(match.group(2))
        supported = SUPPORTED_PINS[family]
        if version != supported:
            raise QueueStateError(
                f"pin file {pin_path} records {pin}, but this dispatcher "
                f"implements {family}-v{supported} — refusing to load the queue"
            )


# ---------------------------------------------------------------------------
# Queue store
# ---------------------------------------------------------------------------


class QueueStore:
    """Durable item-state store: atomic snapshot + transition journal.

    Args:
        queue_root: Directory holding ``state.yml`` / ``journal.ndjson``
            (created if missing).
        recover: When True (dispatcher runtime), reconcile and re-queue
            in-flight items on load. When False (read-only commands such
            as ``status``), reconcile in memory only and never write;
            pending in-flight items are exposed via ``pending_recovery``.
    """

    def __init__(self, queue_root: Path, recover: bool = True):
        self.queue_root = Path(queue_root)
        self.state_path = self.queue_root / "state.yml"
        self.journal_path = self.queue_root / "journal.ndjson"
        self.queue_root.mkdir(parents=True, exist_ok=True)

        self.pins, self.pin_path = read_pins(self.queue_root)
        check_pins(self.pins, self.pin_path)

        self.recovered: list[str] = []
        self.pending_recovery: list[str] = []
        self._seq = 0
        self._state: dict[str, str] = {}
        self._load(recover=recover)

    # -- public API ----------------------------------------------------------

    @property
    def states(self) -> dict[str, str]:
        """Copy of the current ``item_id -> state`` mapping."""
        return dict(self._state)

    def get(self, item_id: str) -> str | None:
        """Current state of ``item_id``, or None if unknown."""
        return self._state.get(item_id)

    def counts(self) -> dict[str, int]:
        """Number of items per state (e.g. for ``dispatch.py status``)."""
        return dict(Counter(self._state.values()))

    def ensure(self, item_id: str) -> str:
        """Register a newly sourced work item as ``queued`` (idempotent)."""
        existing = self._state.get(item_id)
        if existing is not None:
            return existing
        self._append_journal(item_id, None, "queued", note="enqueued")
        self._state[item_id] = "queued"
        self._write_snapshot()
        return "queued"

    def transition(
        self, item_id: str, from_state: str, to_state: str, note: str = ""
    ) -> None:
        """Apply one contract-legal transition durably.

        Order of operations is the crash-safety invariant: journal append
        (fsynced) first, in-memory update second, atomic snapshot last. A
        crash between journal and snapshot is healed by replay on the next
        load.

        Raises:
            TransitionError: if ``item_id`` is unknown, ``from_state`` is
                stale, or the transition is not in ALLOWED_TRANSITIONS.
        """
        current = self._state.get(item_id)
        if current is None:
            raise TransitionError(f"unknown item: {item_id}")
        if current != from_state:
            raise TransitionError(
                f"stale transition for {item_id}: expected current state "
                f"{from_state!r}, found {current!r}"
            )
        if to_state not in ALLOWED_TRANSITIONS.get(from_state, set()):
            raise TransitionError(
                f"illegal transition for {item_id}: {from_state} -> {to_state}"
            )
        self._append_journal(item_id, from_state, to_state, note=note)
        self._state[item_id] = to_state
        self._write_snapshot()

    def requeue(self, item_id: str) -> None:
        """Re-queue a ``failed`` or ``rejected`` item (contract-legal only).

        Raises:
            TransitionError: if the item is unknown or its current state
                has no legal path to ``queued`` (e.g. ``done`` is terminal).
        """
        current = self._state.get(item_id)
        if current is None:
            raise TransitionError(f"unknown item: {item_id}")
        self.transition(item_id, current, "queued", note="manual requeue")

    # -- load + reconcile ------------------------------------------------------

    def _load(self, recover: bool) -> None:
        snapshot = self._read_snapshot()
        records, dropped_tail = self._read_journal()

        journal_state: dict[str, str] = {}
        for rec in records:
            journal_state[rec["item"]] = rec["to"]
            self._seq = max(self._seq, int(rec.get("seq", 0)))

        # Journal wins on divergence: it is fsynced before every snapshot
        # write, so it is never older than the snapshot.
        merged = dict(snapshot)
        merged.update(journal_state)
        diverged = (merged != snapshot) or dropped_tail
        self._state = merged

        in_flight = sorted(
            item for item, state in merged.items() if state == "in-progress"
        )
        if not recover:
            # Read-only load: report, never write.
            self.pending_recovery = in_flight
            return

        for item_id in in_flight:
            self.transition(
                item_id,
                "in-progress",
                "failed",
                note="crash-resume: in-flight at startup with no terminal record",
            )
            self.transition(item_id, "failed", "queued", note="crash-resume: requeued")
            self.recovered.append(item_id)

        if diverged and not self.recovered:
            # Heal a stale snapshot even when nothing needed re-queueing.
            self._write_snapshot()

    def _read_snapshot(self) -> dict[str, str]:
        if not self.state_path.exists():
            return {}
        try:
            loaded = yaml.safe_load(self.state_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            raise QueueStateError(f"corrupt state snapshot {self.state_path}: {exc}")
        if not isinstance(loaded, dict):
            raise QueueStateError(
                f"corrupt state snapshot {self.state_path}: expected a mapping, "
                f"got {type(loaded).__name__}"
            )
        return {str(k): str(v) for k, v in loaded.items()}

    def _read_journal(self) -> tuple[list[dict], bool]:
        """Parse the journal; tolerate only a torn final line.

        Returns ``(records, dropped_tail)`` where ``dropped_tail`` is True
        when a corrupt trailing line (crash mid-append) was discarded.
        """
        if not self.journal_path.exists():
            return [], False
        lines = self.journal_path.read_text(encoding="utf-8").splitlines()
        records: list[dict] = []
        for index, line in enumerate(lines):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
                if not isinstance(rec, dict) or "item" not in rec or "to" not in rec:
                    raise ValueError("missing 'item'/'to' fields")
            except ValueError as exc:
                if index == len(lines) - 1:
                    return records, True  # torn write during a crash
                raise QueueStateError(
                    f"corrupt journal {self.journal_path} at line {index + 1}: {exc}"
                )
            records.append(rec)
        return records, False

    # -- durable writes --------------------------------------------------------

    def _heal_torn_tail(self) -> None:
        """Truncate a torn (crash-interrupted) final journal line before appending.

        Safe by construction: the snapshot write always *follows* the
        journal append, so a partially written record's transition never
        took effect anywhere — dropping it loses nothing. Without this,
        the next append would concatenate onto the torn fragment and turn
        a tolerated torn tail into mid-file corruption.
        """
        if not self.journal_path.exists():
            return
        data = self.journal_path.read_bytes()
        if not data or data.endswith(b"\n"):
            return
        keep = data.rfind(b"\n") + 1  # 0 when no complete line exists
        os.truncate(self.journal_path, keep)

    def _append_journal(
        self, item_id: str, from_state: str | None, to_state: str, note: str = ""
    ) -> None:
        self._heal_torn_tail()
        self._seq += 1
        record = {
            "seq": self._seq,
            "at": time.time(),
            "item": item_id,
            "from": from_state,
            "to": to_state,
            "note": note,
        }
        line = json.dumps(record, sort_keys=True)
        with open(self.journal_path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(line + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def _write_snapshot(self) -> None:
        payload = yaml.safe_dump(self._state, sort_keys=True)
        tmp = self.state_path.with_name(self.state_path.name + ".tmp")
        with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, self.state_path)  # atomic on POSIX and Windows
