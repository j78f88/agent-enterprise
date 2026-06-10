# Orchestration Guide (Mode 2)

Mode 2 takes a queue of work items and runs each one to a verified result
without continuous human supervision: the dispatcher resolves every item to
a registered callable, validates its inputs, invokes it, checks the evidence,
and transitions the item's state — never marking anything `done` just because
a session ended. The contract is the interface, not the implementation:
everything here is defined by the frozen
[`mode-2-contract-v1`](../command-centre/03-mode-orchestration/contract.md),
and any conforming dispatcher can stand in. This page documents the repo's
*supported implementation* — the `src/mode2_dispatcher/` package plus the
root CLI `dispatch.py` — promoted under the five-point contract of
[ADR 0008](../command-centre/decisions/0008-supported-mode-implementations.md).

---

## Install

Mode 2 is a standalone install. It does not assume the Mode 1 substrate and
never needs `init.py` — a clean clone is enough:

```powershell
git clone https://github.com/j78f88/agent-enterprise.git
cd agent-enterprise
pip install -r requirements.txt

python dispatch.py --help
```

`dispatch.py` is the Mode 2 runtime entry point; `init.py` is the Mode 1
build tool. They are deliberately separate: the dispatcher works in a repo
that never ran (and never ships) the Mode 1 build.

Record your contract pins in `.mode-2-pins` per the
[install contract](../command-centre/03-mode-orchestration/install-contract.md)
— see [Queue layout](#queue-layout) below for where the dispatcher reads them.

---

## Queue layout

The dispatcher operates on a queue directory (default `queue/`, overridable
with `--queue-root`):

```
queue/
├── inbox/              one work item per *.yml file
│   └── item-001.yml
├── state.yml           snapshot: item id → state (written atomically)
├── journal.ndjson      append-only transition journal (fsynced)
└── .mode-2-pins        contract pins (also honoured at the queue's parent)
```

A work item file declares the item id, the callable it resolves to, and the
inputs that callable receives:

```yaml
# queue/inbox/item-001.yml
id: item-001
callable_id: my-org.draft-prd
inputs:
  brief_path: ./briefs/dark-mode.md
```

Item states are exactly the contract's:
`queued → in-progress → done | rejected | failed`, with
`failed → queued` / `rejected → queued` as the only re-queue paths. Malformed
inbox files never abort a session — they are reported as `inbox_errors` in
the run summary.

The pin file is enforced, not decorative: if `.mode-2-pins` (in the queue
root or its parent) records a `mode-2-contract` or `protocol` version this
implementation does not support, the queue refuses to load with a clear
error rather than running against pins it cannot satisfy.

---

## Authoring callables

The dispatcher discovers callables from two sources, in deterministic
(sorted-path) order, and validates every candidate against
`schemas/callable-v1.schema.json`:

- A `*.callable.yml` sidecar manifest — the non-enterprise path, for
  wrapping anything you already have (prompt files, scripts) per the
  [callable contract](../command-centre/01-protocols/callable-contract.md).
- `callable-v1` frontmatter in a `*.skill.md` file — the enterprise path;
  every Mode 1 substrate skill already carries this and registers as-is.

Invalid callables are reported with their path and schema violation, never
silently skipped. `python dispatch.py validate-callables` runs exactly this
check and exits non-zero on any violation.

A minimal sidecar manifest:

```yaml
# callables/draft-prd.callable.yml
id: my-org.draft-prd
name: Draft PRD
description: Draft a product requirements document from a brief.
inputs:
  type: object
  required: [brief_path]
  properties:
    brief_path: { type: string }
outputs:
  - path: "./prd/draft.md"
    required: true
verifier: null
runtime_hints:
  invocation:
    type: "python"
    entry: "my_runners:draft_prd"
```

Invocation is governed by `runtime_hints.invocation`:

- `type: "python"` with `entry: "module:function"` is supported natively —
  the function is imported and called with the item's `inputs` dict.
- Any other invocation type fails the item cleanly (`failed`, with a typed
  error in the summary) — it is never guessed at and never ghost-done.
- Custom runtimes plug in programmatically: build your registry with
  `registry_from_manifests(manifests, runner=...)` from
  `src/mode2_dispatcher/` and supply your own manifest-to-function strategy.

---

## Running the dispatcher

```
python dispatch.py {run | status | requeue <item-id> | validate-callables}
```

Shared options:

| Option | Applies to | Behaviour |
|:-------|:-----------|:----------|
| `--queue-root DIR` | `run`, `status`, `requeue` | Queue directory, relative to the working directory (default `queue`). Containment-guarded: a path that escapes the working directory is rejected, mirroring the `init.py` deploy guard. |
| `--callables PATH` | `run`, `validate-callables` | Callable search path, repeatable. Directories are scanned recursively for `*.callable.yml` sidecars and `*.skill.md` frontmatter. Default: `callables/` and `skills/` when present. |

### run

Drains every `queued` inbox item and prints a tier-3 dispatch summary as
JSON on stdout; `--summary-out FILE` also writes it to a file. The summary
asserts the contract shape — `tier: 3`, `status: complete`,
`session_start`/`session_end` — matching the frozen reference
implementation, and additionally reports `skipped` (items not in `queued`
state — `run` is idempotent and re-runs never double-dispatch),
`recovered` (items re-queued by crash recovery), and `inbox_errors`.

### status

Read-only queue report: pins, per-state counts, per-item states, and a flag
on any crash-interrupted item. `status` never writes — it is safe to run
against a live or crashed queue.

### requeue

`python dispatch.py requeue <item-id>` re-queues one item through
contract-legal transitions only (`failed → queued`, `rejected → queued`).
Any other starting state is an error with a non-zero exit — the CLI never
edits state out-of-band.

### validate-callables

Runs discovery plus `callable-v1` schema validation and exits non-zero on
any violation. Use it in CI to keep callable manifests honest.

---

## Crash recovery

The durability design rests on one invariant: every state transition is
appended (and fsynced) to `journal.ndjson` *before* `state.yml` is
rewritten, and the snapshot rewrite itself is atomic (write-temp + fsync +
`os.replace`, atomic on both POSIX and Windows). The journal is therefore
always at least as new as the snapshot, and a crash can never leave a torn
`state.yml`.

After a crash, the next `run` (or any non-read-only command):

1. Replays the journal and reconciles it against the snapshot — the journal
   wins on divergence.
2. Drops a torn *final* journal line (a crash mid-append); corruption
   anywhere else raises an error instead of guessing.
3. Re-queues items left `in-progress` with no terminal record, using only
   contract-legal transitions (`in-progress → failed → queued`) — recovery
   is itself journaled, never an out-of-band state edit.
4. Reports the recovered item ids under `recovered` in the run summary.

The rollback posture from the install contract holds: stop the dispatcher
and in-flight items stay in their current queue state; `status` shows you
what recovery will do before you run it.

---

## Verified results: no ghost-done

Per the contract's most important guarantee (Anti-Fragility Pattern 1), an
item never transitions to `done` because the session ended. Three
independent evidence checks all have to pass:

1. Every declared output artifact exists, is non-empty, and is fresh
   (written at or after session start).
2. Outputs that declare a `return_tier` validate against the corresponding
   `schemas/subagent-return-tier{1,2,3}.schema.json` — enforced by reusing
   the `SubagentReturnValidator` from `src/phase1_verification/`, with a
   tier mismatch escalated to a failure (a Mode 2 hardening beyond the
   reference impl).
3. The callable's declared verifier hook, if any, passes.

Session end with missing or invalid evidence yields `rejected`, with
machine- and human-readable reasons in the summary — re-queue explicitly
with `requeue` once the cause is fixed.

---

## Relationship to the reference implementation

Mode 2 ships two implementations on purpose, per
[ADR 0008](../command-centre/decisions/0008-supported-mode-implementations.md):

- The reference implementation at
  `command-centre/03-mode-orchestration/reference-impls/file-queue-dispatcher/`
  is contract pedagogy. It stays frozen byte-unchanged (asserted by test)
  and exists to make `mode-2-contract-v1` readable in ~200 lines.
- The supported implementation — `src/mode2_dispatcher/` + `dispatch.py`,
  this page — adds what production needs: packaging, a CLI, durable
  journaled state, crash recovery, and return-tier hardening.

Both pass the identical `mode-2-contract-v1` conformance checklist through
the same parametrized tests (`tests/test_protocol_v1_conformance.py` and
`tests/test_mode2_dispatcher.py`), so the two can never drift apart
semantically. Runtimes remain interchangeable: if you bring your own
dispatcher, conformance is checked against the contract alone.
