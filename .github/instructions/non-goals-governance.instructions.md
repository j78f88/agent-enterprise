---
id: instruction.non-goals-governance
kind: instruction
version: 1.0.0
applies_to: '**'
description: non-goals-governance instruction
applyTo: '**'
---

# Non-Goals Governance

Single source of truth for `{{paths.non_goals}}` ownership, modification protocol, and enforcement.

## Ownership

`{{paths.non_goals}}` is owned exclusively by `@planner`. No other agent may modify it. Any ad-hoc session asked to edit it must defer to `@planner`.

## Modification Protocol

- **Adding or clarifying a non-goal:** requires explicit user approval, recorded in the commit body as `(approved by {{team.cto_name}} YYYY-MM-DD)`.
- **Removing a non-goal:** requires an ADR in `{{paths.decisions}}` _plus_ the approval marker. Removal expands scope and must be justified.

## Enforcement (for @reviewer)

- **CRITICAL:** Commit modifying `{{paths.non_goals}}` without the approval marker.
- **CRITICAL:** Commit modifying `{{paths.non_goals}}` authored by any agent other than `@planner`.
- **WARNING:** PR whose scope appears to cross a listed non-goal without an ADR reference.

## Pre-Flight Reading

Every ideation pre-flight reads `{{paths.non_goals}}`. If a proposal conflicts with a listed non-goal, flag the conflict — do not silently work around it.
