#!/usr/bin/env python3
"""
dispatch.py — Mode 2 (orchestration) runtime CLI.

Runs the supported file-queue dispatcher (``src/mode2_dispatcher/``,
``mode-2-contract-v1``) against a local queue directory:

    python dispatch.py run                 # drain inbox, emit tier-3 summary
    python dispatch.py status              # queue state report (read-only)
    python dispatch.py requeue <item-id>   # contract-legal re-queue
    python dispatch.py validate-callables  # discovery + callable-v1 check

This is the Mode 2 runtime entry point. It is deliberately a separate
tool from ``init.py`` (the Mode 1 build tool) and works in a repo that
has never run ``init.py`` — it needs only ``src/`` and ``schemas/`` from
a clean clone.

Queue layout (relative to --queue-root, default ``queue/``):

    inbox/*.yml       work items: {id, callable_id, inputs}
    state.yml         atomic snapshot of item states
    journal.ndjson    append-only transition journal (crash-resume source)
    .mode-2-pins      contract pins (also honoured at the parent directory)

``--queue-root`` is contained to the working directory — paths with
``..`` or that resolve outside the working directory are refused,
mirroring the init.py deploy guard posture.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make src/ importable when dispatch.py is run from any working directory.
_REPO_ROOT = Path(__file__).resolve().parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.mode2_dispatcher import (  # noqa: E402
    Dispatcher,
    QueueStateError,
    QueueStore,
    TransitionError,
    discover_callables,
    registry_from_manifests,
    write_summary,
)

#: Default callable search paths, used when --callables is not given.
DEFAULT_CALLABLE_DIRS = ("callables", "skills")


def fail(message: str) -> None:
    """Print a clear error to stderr and exit non-zero (init.py convention)."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def resolve_queue_root(arg: str) -> Path:
    """Containment check for --queue-root, mirroring the init.py deploy guard.

    Refuses ``..`` components and any path (relative or absolute) that
    resolves outside the current working directory — the dispatcher never
    operates on queue state outside the project it is run from.
    """
    candidate = Path(arg)
    if ".." in candidate.parts:
        fail(
            f"--queue-root '{arg}' contains '..' — refusing path traversal "
            "(mirrors the init.py deploy guard)."
        )
    base = Path.cwd().resolve()
    resolved = (candidate if candidate.is_absolute() else base / candidate).resolve()
    if resolved != base and base not in resolved.parents:
        fail(
            f"--queue-root '{arg}' escapes the working directory '{base}' — "
            "refusing to operate outside the project root "
            "(mirrors the init.py deploy guard)."
        )
    return resolved


def resolve_callable_paths(args: argparse.Namespace) -> list[Path]:
    """Resolve --callables search paths (or the existing defaults)."""
    if args.callables:
        paths = [Path(p) for p in args.callables]
        missing = [str(p) for p in paths if not p.exists()]
        if missing:
            fail(f"callable search path(s) not found: {', '.join(missing)}")
        return paths
    defaults = [Path(d) for d in DEFAULT_CALLABLE_DIRS if Path(d).is_dir()]
    if not defaults:
        fail(
            "no callable search paths found — pass --callables PATH or create "
            f"one of: {', '.join(DEFAULT_CALLABLE_DIRS)}/"
        )
    return defaults


def _report_violations(violations, *, as_warning: bool) -> None:
    label = "WARNING" if as_warning else "VIOLATION"
    for violation in violations:
        print(f"{label}: {violation.path}: {violation.message}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------


def cmd_run(args: argparse.Namespace) -> int:
    """Drain queued inbox items; print the tier-3 summary as JSON."""
    queue_root = resolve_queue_root(args.queue_root)
    inbox = queue_root / "inbox"
    if not inbox.is_dir():
        fail(f"no inbox directory at {inbox} — nothing to dispatch.")

    callables, violations = discover_callables(resolve_callable_paths(args))
    _report_violations(violations, as_warning=True)
    registry, problems = registry_from_manifests(c.manifest for c in callables)
    for problem in problems:
        print(f"WARNING: {problem}", file=sys.stderr)

    try:
        dispatcher = Dispatcher(queue_root, registry)
        summary = dispatcher.run()
    except (QueueStateError, TransitionError) as exc:
        fail(str(exc))

    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.summary_out:
        write_summary(summary, Path(args.summary_out))
        print(f"summary written: {args.summary_out}", file=sys.stderr)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Read-only queue state report (never mutates state or journal)."""
    queue_root = resolve_queue_root(args.queue_root)
    try:
        store = QueueStore(queue_root, recover=False)
    except QueueStateError as exc:
        fail(str(exc))

    print(f"queue root: {queue_root}")
    pins = ", ".join(store.pins) if store.pins else "(none recorded)"
    print(f"pins: {pins}")

    states = store.states
    if not states:
        print("queue is empty.")
        return 0

    counts = store.counts()
    print("counts: " + ", ".join(f"{k}={counts[k]}" for k in sorted(counts)))
    for item_id in sorted(states):
        print(f"  {item_id}: {states[item_id]}")
    if store.pending_recovery:
        print(
            "in-flight (no terminal record; will re-queue on next run): "
            + ", ".join(store.pending_recovery)
        )
    return 0


def cmd_requeue(args: argparse.Namespace) -> int:
    """Re-queue one item via contract-legal transitions only."""
    queue_root = resolve_queue_root(args.queue_root)
    try:
        store = QueueStore(queue_root, recover=False)
        store.requeue(args.item_id)
    except (QueueStateError, TransitionError) as exc:
        fail(str(exc))
    print(f"OK: {args.item_id} -> queued")
    return 0


def cmd_validate_callables(args: argparse.Namespace) -> int:
    """Discover callables and validate against callable-v1; non-zero on violations."""
    callables, violations = discover_callables(resolve_callable_paths(args))
    for found in callables:
        print(f"OK: {found.manifest['id']} ({found.source}) {found.path}")
    _report_violations(violations, as_warning=False)
    if violations:
        fail(
            f"{len(violations)} callable-v1 violation(s) across the search "
            "paths (see above)."
        )
    print(f"{len(callables)} callable(s) valid.")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="dispatch.py",
        description=(
            "Mode 2 (orchestration) file-queue dispatcher — runtime CLI for "
            "src/mode2_dispatcher/ (mode-2-contract-v1)."
        ),
    )

    queue_parent = argparse.ArgumentParser(add_help=False)
    queue_parent.add_argument(
        "--queue-root",
        default="queue",
        help=(
            "Queue directory, relative to the working directory "
            "(default: queue). Must not escape the working directory."
        ),
    )
    callables_parent = argparse.ArgumentParser(add_help=False)
    callables_parent.add_argument(
        "--callables",
        action="append",
        metavar="PATH",
        help=(
            "Callable search path: directories scanned recursively for "
            "*.callable.yml sidecars and *.skill.md frontmatter (repeatable). "
            f"Default: {' and '.join(DEFAULT_CALLABLE_DIRS)} when present."
        ),
    )

    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser(
        "run",
        parents=[queue_parent, callables_parent],
        help="Drain queued inbox items and emit a tier-3 dispatch summary (JSON on stdout).",
    )
    run_parser.add_argument(
        "--summary-out",
        metavar="FILE",
        help="Also write the tier-3 summary JSON to this file.",
    )
    run_parser.set_defaults(func=cmd_run)

    status_parser = sub.add_parser(
        "status",
        parents=[queue_parent],
        help="Report queue state (read-only; flags crash-interrupted items).",
    )
    status_parser.set_defaults(func=cmd_status)

    requeue_parser = sub.add_parser(
        "requeue",
        parents=[queue_parent],
        help="Re-queue a failed or rejected item (contract-legal transitions only).",
    )
    requeue_parser.add_argument("item_id", help="Work item id to re-queue.")
    requeue_parser.set_defaults(func=cmd_requeue)

    validate_parser = sub.add_parser(
        "validate-callables",
        parents=[callables_parent],
        help="Discover callables and validate them against callable-v1 (non-zero exit on violations).",
    )
    validate_parser.set_defaults(func=cmd_validate_callables)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
