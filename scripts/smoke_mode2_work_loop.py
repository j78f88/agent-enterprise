#!/usr/bin/env python3
"""CI-friendly smoke for Mode 2 work-loop ingestion and reconciliation.

Creates a tiny adopter-style workspace, turns one backlog ledger row into a
Mode 2 queue item, dispatches it through ``dispatch.py``, verifies the artifact,
and reconciles the ledger row back to ``done``.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISPATCH = ROOT / "dispatch.py"

LEDGER_ID = "ITEM-042"
QUEUE_ID = "ITEM-042-docs-bridge"


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    env = dict(PYTHONIOENCODING="utf-8")
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**env, **dict(**__import__("os").environ)},
    )


def write_fixture(workdir: Path) -> None:
    (workdir / "docs" / "planning").mkdir(parents=True, exist_ok=True)
    (workdir / "docs").mkdir(exist_ok=True)
    (workdir / "callables").mkdir(exist_ok=True)
    (workdir / "queue" / "inbox").mkdir(parents=True, exist_ok=True)

    (workdir / "docs" / "planning" / "BACKLOG_LEDGER.md").write_text(
        "# Backlog Ledger\n\n"
        "| ID | Type | Source | Age | Def | Sprint | Status | Blocked | Draft | Notes |\n"
        "| --- | --- | --- | ---: | ---: | --- | --- | --- | --- | --- |\n"
        "| ITEM-042 | debt | CHAT-2026-06-19 | 13 | 0 | Sprint 13 | assigned | — | docs/planning/drafts/work-loop-bridge.md | Clarify chat intake -> backlog ledger -> queue -> execution -> retro/update. |\n",
        encoding="utf-8",
    )

    (workdir / "callables" / "__init__.py").write_text("", encoding="utf-8")
    (workdir / "callables" / "worker.py").write_text(
        "from pathlib import Path\n\n"
        "def write_doc(inputs):\n"
        "    path = Path(inputs['deliverable_path'])\n"
        "    path.parent.mkdir(parents=True, exist_ok=True)\n"
        "    path.write_text('# Mode 2 smoke\\n\\n' + inputs['notes'] + '\\n', encoding='utf-8')\n"
        "    return {'tier': 1, 'agent': 'mode2-smoke', 'status': 'complete', 'summary': 'wrote deliverable', 'findings': []}\n",
        encoding="utf-8",
    )
    (workdir / "callables" / "docs-update.callable.yml").write_text(
        "id: project.docs-update\n"
        "kind: callable\n"
        "version: 1.0.0\n"
        "applies_to: '**'\n"
        "name: Docs update\n"
        "description: Write a docs artifact from a backlog item.\n"
        "inputs:\n"
        "  type: object\n"
        "  required: [ledger_id, deliverable_path, notes]\n"
        "  properties:\n"
        "    ledger_id: {type: string}\n"
        "    deliverable_path: {type: string}\n"
        "    notes: {type: string}\n"
        "outputs:\n"
        "  - path: './docs/WORK_LOOP_RESULT.md'\n"
        "    required: true\n"
        "verifier: null\n"
        "runtime_hints:\n"
        "  invocation:\n"
        "    type: python\n"
        "    entry: callables.worker:write_doc\n",
        encoding="utf-8",
    )
    (workdir / "queue" / "inbox" / f"{QUEUE_ID}.yml").write_text(
        f"id: {QUEUE_ID}\n"
        "callable_id: project.docs-update\n"
        "inputs:\n"
        f"  ledger_id: {LEDGER_ID}\n"
        "  work_type: debt\n"
        "  source_ref: CHAT-2026-06-19\n"
        "  sprint: Sprint 13\n"
        "  plan_path: docs/planning/drafts/work-loop-bridge.md\n"
        "  deliverable_path: ./docs/WORK_LOOP_RESULT.md\n"
        "  notes: Mode 2 smoke completed from backlog ledger item.\n",
        encoding="utf-8",
    )
    (workdir / "queue" / ".mode-2-pins").write_text(
        "mode-2-contract: mode-2-contract-v1\nprotocol: protocol-v1\n",
        encoding="utf-8",
    )


def reconcile_ledger(workdir: Path) -> None:
    ledger = workdir / "docs" / "planning" / "BACKLOG_LEDGER.md"
    text = ledger.read_text(encoding="utf-8")
    old = (
        "| ITEM-042 | debt | CHAT-2026-06-19 | 13 | 0 | Sprint 13 | assigned | — | "
        "docs/planning/drafts/work-loop-bridge.md | Clarify chat intake -> backlog ledger -> queue -> execution -> retro/update. |"
    )
    new = (
        "| ITEM-042 | debt | CHAT-2026-06-19 | 13 | 0 | Sprint 13 | done | — | "
        "docs/planning/drafts/work-loop-bridge.md | Mode 2 smoke completed; artifact docs/WORK_LOOP_RESULT.md verified. |"
    )
    if old not in text:
        raise RuntimeError("expected assigned ledger row not found")
    ledger.write_text(text.replace(old, new), encoding="utf-8")


def run_smoke(workdir: Path) -> dict:
    write_fixture(workdir)

    validate = run(
        [sys.executable, str(DISPATCH), "validate-callables", "--callables", "callables"],
        cwd=workdir,
    )
    if validate.returncode != 0:
        raise RuntimeError(validate.stdout + validate.stderr)

    dispatch = run(
        [
            sys.executable,
            str(DISPATCH),
            "run",
            "--queue-root",
            "queue",
            "--callables",
            "callables",
            "--summary-out",
            "summary.json",
        ],
        cwd=workdir,
    )
    if dispatch.returncode != 0:
        raise RuntimeError(dispatch.stdout + dispatch.stderr)

    summary = json.loads((workdir / "summary.json").read_text(encoding="utf-8"))
    state = (workdir / "queue" / "state.yml").read_text(encoding="utf-8")
    artifact = workdir / "docs" / "WORK_LOOP_RESULT.md"
    if f"{QUEUE_ID}: done" not in state:
        raise RuntimeError(f"queue item did not reach done: {state}")
    if not artifact.exists() or artifact.stat().st_size == 0:
        raise RuntimeError("declared artifact missing or empty")

    reconcile_ledger(workdir)

    return {
        "status": "pass",
        "ledger_id": LEDGER_ID,
        "queue_id": QUEUE_ID,
        "queue_state": "done",
        "artifact_path": str(artifact),
        "dispatch_summary": summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Mode 2 work-loop smoke.")
    parser.add_argument("--workdir", help="Workspace to populate; temp dir if omitted.")
    args = parser.parse_args()

    if args.workdir:
        workdir = Path(args.workdir)
        if workdir.exists() and any(workdir.iterdir()):
            print(
                f"ERROR: --workdir must be empty or absent, got non-empty: {workdir}",
                file=sys.stderr,
            )
            return 2
        workdir.mkdir(parents=True, exist_ok=True)
        print(json.dumps(run_smoke(workdir), indent=2, sort_keys=True))
        return 0

    with tempfile.TemporaryDirectory(prefix="ae-mode2-work-loop-") as tmp:
        print(json.dumps(run_smoke(Path(tmp)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
