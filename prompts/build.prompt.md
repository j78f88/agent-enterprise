---
description: "Lifecycle command — execute a sprint plan: implementation + per-task gates."
mode: chat
---

# /build

Use this after `/plan` to drive a sprint to completion.

## Flow

1. Invoke `@sprint-lead` with the sprint folder path.
2. `@sprint-lead` reads `PLAN.md`, sequences tasks per the dependency graph,
   and dispatches each task to the appropriate executor (engineer agent, or
   the user) with the structured handoff format.
3. Quality gates declared in `PLAN.md` are run as each task completes.
   Failing gates block downstream tasks.

## Artifacts

- Implementation commits attributed to the sprint.
- Updated `PLAN.md` showing task completion + gate results + timestamps.
- Bug backlog updated for any defects found mid-sprint.

## Exit

All tasks in `PLAN.md` are checked off or explicitly deferred with a reason.
Ready for `/review`.
