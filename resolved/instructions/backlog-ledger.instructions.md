---
applyTo: "docs/planning/BACKLOG_LEDGER.md"
---

# Backlog Ledger — Schema & Governance

Single schema, governance, and escalation specification for `docs/planning/BACKLOG_LEDGER.md`.

> **Canonical status tracker.** The ledger is the single source of truth for item status. Detail stores (`docs/planning/BUG_BACKLOG.md`, `docs/planning/HANDOFF_REJECTIONS.md`) hold reproduction/rejection context only — no status fields.

## Schema

The ledger table uses 10 columns:

| Column  | Type     | Description                                                                          |
| ------- | -------- | ------------------------------------------------------------------------------------ |
| ID      | string   | `ITEM-NNN`, zero-padded to 3 digits, sequential                                     |
| Type    | enum     | `bug`, `debt`, `feature`, `carry-over`, `audit-finding`, `research`, `rejection`     |
| Source  | string   | Origin reference (e.g., `BUG-003`, `REJ-001`, `audit-H-1`, `RETRO-55`, `ROAD-nnn`) |
| Age     | integer  | Sprint number when item first appeared (not migration sprint)                        |
| Def     | integer  | Deferral count — incremented each sprint the item is not resolved                    |
| Sprint  | string   | Assigned sprint number, or `—` if unscheduled                                        |
| Status  | enum     | `open`, `assigned`, `done`, `killed`                                                 |
| Blocked | string   | Blocking reference (e.g., `ITEM-005`) or `—`                                         |
| Draft   | string   | Link to draft plan if exists, or `—`                                                 |
| Notes   | string   | Free-text context                                                                    |

### ID Assignment

Read the ledger to find the highest existing ITEM-NNN; assign NNN+1. IDs are never reused.

### Type Values

`bug` · `debt` · `feature` · `carry-over` · `audit-finding` · `research` · `rejection`

Features use the Draft column to indicate draft plan existence — there is no separate "draft" type.

### Status Values

`open` → `assigned` → `done` or `killed`

Status changes are edit-in-place on the existing row.

## Operation-Based Governance

Operations are governed by permitted actors, not file ownership. Multiple agents may write to the ledger for different operations.

| Operation                                | Permitted Actors                     | Notes                                                   |
| ---------------------------------------- | ------------------------------------ | ------------------------------------------------------- |
| Append new ITEM (type: bug)              | `@bug`                               | Same commit as docs/planning/BUG_BACKLOG.md entry                        |
| Append new ITEM (type: rejection)        | `@planner`                           | Same commit as docs/planning/HANDOFF_REJECTIONS.md entry                 |
| Append new ITEM (type: feature)          | `@planner`, `@delivery-lead`         | When accepting a validated feature for scheduling       |
| Append new ITEM (type: carry-over)       | `@sprint-lead`                       | Post-sprint Phase 6 ledger update                       |
| Append new ITEM (type: audit-finding)    | `@sprint-lead`, `@planner`           | From audit roadmaps or code review findings             |
| Append new ITEM (type: research)         | `@researcher`, `@planner`            | Research follow-ups with concrete next-steps            |
| Append new ITEM (type: debt)             | `@sprint-lead`, `@planner`           | Technical debt items from retros, audits, or reviews    |
| Update Status: open → assigned           | `@planner`, `@delivery-lead`         | When item is scheduled into a sprint                    |
| Update Status: assigned → done           | `@sprint-lead`                       | Post-sprint Phase 6 completion                          |
| Update Status: open/assigned → killed    | `@planner`, `@delivery-lead`         | With rationale in Notes                                 |
| Increment Def (deferral count)           | `@sprint-lead`                       | Post-sprint Phase 6 for unresolved items                |
| Update Sprint assignment                 | `@planner`, `@delivery-lead`         | During sprint composition                               |
| Update Blocked field                     | Any agent discovering a dependency   | Must cite the blocking ITEM-NNN or external reference   |
| Update Draft field                       | `@planner`                           | When a draft plan is created or removed                 |
| Update Notes field                       | Any permitted actor for the row type | Append-only; do not overwrite existing notes            |
| Update summary counts                    | `@sprint-lead`, `@planner`           | Must match actual table contents                        |

## Escalation Rules

| Condition                      | Effect                                                                 |
| ------------------------------ | ---------------------------------------------------------------------- |
| Def 3                        | Item escalates to P0 — mandatory inclusion in next composition         |
| Def 5                        | Item must be resolved or killed — no further deferral permitted        |
| Age 10 sprints (Status: open) | Item flagged as stale — review for kill or schedule at next composition |

## Detail-Store Relationship

The ledger is the **canonical status tracker**. Detail stores hold context only:

| File                         | Role                                      | Status Fields |
| ---------------------------- | ----------------------------------------- | ------------- |
| `docs/planning/BACKLOG_LEDGER.md` | Canonical tracker — status, scheduling, deferrals | ✅ Yes   |
| `docs/planning/BUG_BACKLOG.md`    | Reproduction context — severity, description, screenshots | ❌ None — removed |
| `docs/planning/HANDOFF_REJECTIONS.md` | Rejection context — reason, proposed resolution, response | ❌ None — removed |

Cross-references:
- Ledger entries use the **Source** column to reference detail-store entries (e.g., `BUG-003`, `REJ-001`).
- Detail-store entries use a **Ledger:** field to reference back (e.g., `ITEM-007`).

## Invariants

1. **ID uniqueness.** Every ITEM-NNN in the ledger is unique.
2. **Status validity.** Every Status value is one of: `open`, `assigned`, `done`, `killed`.
3. **Type validity.** Every Type value is one of the 7 defined types.
4. **Summary accuracy.** The summary section counts must match actual table contents.
5. **No orphaned assignments.** Every `assigned` item must have a Sprint value ≠ `—`.
6. **No status in detail stores.** docs/planning/BUG_BACKLOG.md and docs/planning/HANDOFF_REJECTIONS.md entries must not contain Status fields.
7. **Cross-reference consistency.** Every Source reference in the ledger must correspond to an entry in the referenced detail store.

## Follow-Up Binding Rule

When an agent discovers a follow-up action during execution (e.g., a retro carry-over, an audit finding, a research follow-up):

1. Append an ITEM to the ledger in the **same commit** as the source artifact update.
2. Do NOT leave follow-ups as prose in RETRO.md, audit reports, or research docs without a corresponding ledger entry.
3. Dedup check: before appending, scan the ledger for an existing ITEM with the same Source reference.
