---
id: instruction.non-goals-governance
kind: instruction
version: 1.0.0
applies_to: '**'
description: non-goals-governance instruction
applyTo: '**'
paths:
- '**'
---

# Non-Goals Governance

Single source of truth for `docs/NON_GOALS.md` ownership, modification protocol, and enforcement.

## Ownership

`docs/NON_GOALS.md` is owned exclusively by `@planner`. No other agent may modify it. Any ad-hoc session asked to edit it must defer to `@planner`.

## Modification Protocol

- **Adding or clarifying a non-goal:** requires explicit user approval, recorded in the commit body as `(approved by josh YYYY-MM-DD)`.
- **Removing a non-goal:** requires an ADR in `docs/decisions/DECISIONS.md` _plus_ the approval marker. Removal expands scope and must be justified.

## Enforcement (for @reviewer)

- **CRITICAL:** Commit modifying `docs/NON_GOALS.md` without the approval marker.
- **CRITICAL:** Commit modifying `docs/NON_GOALS.md` authored by any agent other than `@planner`.
- **WARNING:** PR whose scope appears to cross a listed non-goal without an ADR reference.

## Pre-Flight Reading

Every ideation pre-flight reads `docs/NON_GOALS.md`. If a proposal conflicts with a listed non-goal, flag the conflict — do not silently work around it.
