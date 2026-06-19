# Work Loop: Chat Intake to Verified Completion

This guide bridges the project backlog ledger and the Mode 2 queue for a
project-embedded agent-enterprise installation. It explains how a request moves
from a user chat into durable planning records, optionally through
non-interactive dispatch, and back into the backlog as a completed or rejected
item.

The work loop is generic: use it for any adopter project that keeps
agent-enterprise under the project (for example `skills-library/`) and deploys
resolved assistant artifacts into the project root. It does not require a
specific chat product, repository host, or automation platform.

---

## Canonical records and status ownership

Use one owner for each kind of status. Do not duplicate lifecycle state across
backlog detail files and queues.

| Record | Canonical owner | Status it owns | Detail it stores |
|:--|:--|:--|:--|
| `docs/planning/BACKLOG_LEDGER.md` or the configured `paths.backlog_ledger` | Planning and delivery agents (`@planner`, `@sprint-lead`, and row-type permitted actors) | Product/planning lifecycle: `open`, `assigned`, `done`, `killed`; sprint assignment; deferrals; blockers | The durable portfolio view of all accepted bugs, features, debt, research follow-ups, rejections, and carry-over work |
| `docs/planning/BUG_BACKLOG.md` or the configured `paths.bug_backlog` | `@bug` for new bug detail; other permitted actors only for context updates | No status | Reproduction steps, severity, screenshots, affected versions, and a back-reference to the ledger item |
| `docs/planning/HANDOFF_REJECTIONS.md` or the configured `paths.rejections` | `@planner` for rejection detail; other permitted actors only for context updates | No status | Rejection rationale, proposed resolution, response notes, and a back-reference to the ledger item |
| Mode 2 `queue/state.yml` and `queue/journal.ndjson` | The dispatcher described in [ORCHESTRATION.md](ORCHESTRATION.md) | Execution lifecycle for queued work: `queued`, `in-progress`, `done`, `rejected`, `failed` | Machine execution state, crash recovery history, and terminal dispatch evidence |
| Mode 2 `queue/inbox/*.yml` | The planning actor that queues the item | No mutable status | Callable id and immutable inputs needed by the callable |

The backlog ledger remains the canonical planning status tracker. Detail stores
must not contain status fields. When Mode 2 is used, its state files own only
the execution state of queue items. After dispatch completes, the planning or
delivery actor reconciles the terminal queue result back into the ledger by
updating the existing row in place.

---

## End-to-end loop

1. **Intake in chat.** A user asks for a feature, bug fix, research follow-up,
   debt item, or other actionable change.
2. **Triage.** The appropriate role validates whether the request should enter
   the backlog. Examples: `@pm` validates feature value, `@bug` captures a
   reproducible defect, and `@planner` scopes accepted work.
3. **Ledger entry.** Accepted work receives the next ledger ID. The ledger row
   records type, source, age, deferral count, sprint assignment, status,
   blockers, draft plan link, and notes.
4. **Detail store entry, when needed.** Bugs and handoff rejections get context
   in their detail store. The detail entry references the ledger ID, and the
   ledger `Source` column references the detail ID.
5. **Plan or queue.** Interactive work can move from ledger to a sprint plan.
   Non-interactive work can also be materialized as a Mode 2 inbox item that
   names a callable and passes the ledger context as inputs.
6. **Execute.** A human-directed agent or the Mode 2 dispatcher performs the
   work. The dispatcher writes execution state to `state.yml` and
   `journal.ndjson`; it never marks an item `done` without verified evidence.
7. **Verify.** Run the relevant checks for the change. For Mode 2, verification
   includes declared output artifacts, return-tier validation when configured,
   and any verifier hook declared by the callable.
8. **Reconcile.** Update the backlog ledger row to `done` or `killed`, or leave
   it `open`/`assigned` with a blocker or follow-up note if the work did not
   land. Do not edit queue state by hand to make planning status look complete.
9. **Retro/update.** Capture carry-over, audit findings, or research follow-ups
   as new ledger rows in the same commit as the source artifact update.

---

## Mapping backlog fields to queue fields

A ledger row describes why work exists and where it sits in the planning
lifecycle. A queue item describes how a callable should execute one piece of
work. The fields do not have a one-to-one schema match, so use this mapping
when creating `queue/inbox/*.yml` from backlog work.

| Backlog ledger field | Queue field or location | Mapping guidance |
|:--|:--|:--|
| `ID` | `id` or `inputs.ledger_id` | Prefer a stable queue id that includes the ledger id, such as `ITEM-042-implement`. Also pass the original ledger id in inputs so generated artifacts can link back. |
| `Type` | `callable_id` and/or `inputs.work_type` | Select the callable based on the type of work. For example, a bug might route to a fix callable, while research follow-up might route to a documentation or investigation callable. |
| `Source` | `inputs.source_ref` | Preserve the origin reference, such as a bug detail id, rejection id, retro id, roadmap item, or external issue. |
| `Age` | No queue field | Keep age in the ledger. The queue should not own backlog aging policy. Pass only if the callable explicitly needs prioritization context. |
| `Def` | No queue field | Keep deferral count in the ledger. The queue should execute selected work, not enforce deferral escalation. |
| `Sprint` | Queue root, batch name, or `inputs.sprint` | If the queue represents one sprint or execution batch, the directory name may be enough. Otherwise pass the sprint assignment as immutable input. |
| `Status` | `queue/state.yml` after dispatch starts | Ledger `open`/`assigned` is planning status. Queue `queued`/`in-progress`/`done`/`rejected`/`failed` is execution status. Reconcile terminal queue state back to the ledger instead of treating the queue as the ledger. |
| `Blocked` | `inputs.blocked_on` or omit | Do not queue blocked work unless the callable's purpose is to unblock it. If queued, pass the blocker reference for context. |
| `Draft` | `inputs.draft_path` or `inputs.plan_path` | Pass the draft plan path when the callable needs scoped requirements, acceptance criteria, or design notes. |
| `Notes` | `inputs.notes` or linked context file | Keep long-lived notes in the ledger. Pass only concise execution-relevant context or a path to a richer source document. |

A minimal queue item derived from a ledger row can look like this:

```yaml
id: ITEM-042-docs-bridge
callable_id: project.docs-update
inputs:
  ledger_id: ITEM-042
  work_type: debt
  source_ref: RETRO-12
  sprint: Sprint 13
  plan_path: docs/planning/drafts/work-loop-bridge.md
  notes: Add docs that connect chat intake, backlog ledger, queue execution, and completion reconciliation.
```

---

## Complete example

This example shows one request from user chat through completion. Names are
illustrative; use your project's configured prefixes and paths.

### 1. User chat intake

```text
User: The release process is still confusing. Please add documentation that
connects chat intake, the backlog ledger, the execution queue, and the final
retro update.
```

### 2. Triage and ledger entry

`@planner` accepts the request as documentation debt and appends a ledger row:

```markdown
| ID | Type | Source | Age | Def | Sprint | Status | Blocked | Draft | Notes |
| --- | --- | --- | ---: | ---: | --- | --- | --- | --- | --- |
| ITEM-042 | debt | CHAT-2026-06-19 | 13 | 0 | Sprint 13 | assigned | — | docs/planning/drafts/work-loop-bridge.md | Clarify chat intake -> backlog ledger -> queue -> execution -> retro/update. |
```

No bug or rejection detail-store entry is needed because this is not a bug or a
handoff rejection. The ledger owns the row status.

### 3. Queue item for non-interactive execution

The delivery actor creates `queue/inbox/ITEM-042-docs-bridge.yml`:

```yaml
id: ITEM-042-docs-bridge
callable_id: project.docs-update
inputs:
  ledger_id: ITEM-042
  work_type: debt
  source_ref: CHAT-2026-06-19
  sprint: Sprint 13
  plan_path: docs/planning/drafts/work-loop-bridge.md
  deliverable_path: docs/WORK_LOOP.md
  acceptance_criteria:
    - Define canonical status owner and detail stores.
    - Map backlog fields to queue fields.
    - Include one complete chat-to-completion example.
```

At this point, the inbox file has no mutable status. The dispatcher will create
or update queue state when it runs.

### 4. Dispatch and verification

The dispatcher runs:

```powershell
python dispatch.py run --queue-root queue --summary-out queue/last-run-summary.json
```

It transitions the queue item through `queued -> in-progress -> done` only if
its output and verifier requirements pass. If an output is missing or invalid,
the terminal queue state is `rejected` or `failed`, and the ledger remains
`assigned` until a planning actor decides how to proceed.

### 5. Ledger reconciliation and retro/update

After the verified docs change lands, `@sprint-lead` updates the existing
ledger row in place:

```markdown
| ITEM-042 | debt | CHAT-2026-06-19 | 13 | 0 | Sprint 13 | done | — | docs/planning/drafts/work-loop-bridge.md | Completed in commit abc1234; verified docs build and Mode 2 dispatcher tests. |
```

The sprint retro lists the completed item and records any follow-up as a new
ledger row. The queue remains an execution audit trail; it does not replace the
ledger's planning status.

---

## Non-goals

- This guide does not change the Mode 2 runtime contract, dispatcher schemas,
  state transitions, verifier behavior, or queue file format.
- This guide does not require every ledger item to become a queue item.
  Interactive sprint execution remains supported.
- This guide does not make bug or rejection detail stores status trackers.
  They remain context stores only.
- This guide does not define a cross-project choreography registry. Use Mode 3
  documentation for program-level coordination across repositories.
- This guide does not prescribe a particular chat tool, CI provider, or issue
  tracker integration.

---

## Related docs

- [ORCHESTRATION.md](ORCHESTRATION.md) — Mode 2 queue layout, dispatcher
  commands, crash recovery, and verified-result guarantees.
- [README.md](../README.md#-three-delivery-modes) — summary of the three
  delivery modes and adoption paths.
- [backlog-ledger.instructions.md](../instructions/configurable/backlog-ledger.instructions.md)
  — source instruction that defines ledger schema, governance, detail stores,
  and invariants before token resolution.
- `docs/planning/BACKLOG_LEDGER.md` in an adopter project — the resolved,
  project-specific backlog ledger.
- `docs/planning/BUG_BACKLOG.md` and `docs/planning/HANDOFF_REJECTIONS.md` in
  an adopter project — resolved detail stores that reference ledger rows but do
  not own status.
