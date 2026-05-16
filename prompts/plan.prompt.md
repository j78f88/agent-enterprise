---
description: "Lifecycle command — turn a vetted spec/ADR into a sprint plan with tasks, files, and gates."
mode: chat
---

# /plan

Use this after `/spec` to produce a sprint-ready plan from a spec and its
associated ADR(s).

## Flow

1. Invoke `@planner` with links to the spec doc and the ADR(s).
2. `@planner` produces a sprint folder under `sprints/sprint-NNN/` containing
   `PLAN.md` with: scope, dependency graph, tasks (with `Files:` annotations),
   risks, and quality gates.
3. Any handoff that cannot be cleanly scoped is recorded via the
   `handoff-rejection-format` instruction, not silently dropped.

## Artifacts

- `sprints/sprint-NNN/PLAN.md` with explicit tasks and quality gates.
- Optional `REJ-NNN` entries documenting rejected scope.

## Exit

PLAN.md is reviewed and ready to be handed to `@sprint-lead` via `/build`.
