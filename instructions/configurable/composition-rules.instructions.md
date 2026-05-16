---
id: instruction.composition-rules
kind: instruction
version: 1.0.0
applies_to: '**'
description: composition-rules instruction
---

# Sprint Composition Rules

Priority stack, scoring formula, and constraints for `/compose-sprint`. Referenced by `@planner` and `@delivery-lead`.

> **Calibration notice:** All thresholds in this file are initial calibrations. Tune after 3 composition cycles based on observed outcomes.

## P0–P6 Priority Stack

Items are assigned a priority tier at composition time based on their ledger attributes and source artifact context. **No severity column is stored in the ledger** — tiers are computed fresh each time.

| Tier | Name               | Criteria                                                                                   |
| ---- | ------------------ | ------------------------------------------------------------------------------------------ |
| P0   | Mandatory          | Def {{escalation.def_p0_threshold}} (escalation rule), or item explicitly marked as blocker by user                    |
| P1   | Blocking Bug       | Type: `bug`, source severity 🔴 Blocks                                                    |
| P2   | Degrading Bug      | Type: `bug`, source severity 🟡 Degraded                                                  |
| P3   | Validated Feature   | Type: `feature` with a passing validation record in `{{paths.validation}}`            |
| P4   | Planned Feature    | Type: `feature` with a Draft ≠ `—` but no validation record                               |
| P5   | Backlog            | All other open items (carry-overs, audit findings, research, rejections, unplanned features) |
| P6   | Cosmetic / Edge    | Type: `bug`, source severity 🟢 Cosmetic or ⚪ Edge case                                  |

### P3 Source Artifact Lookup

When computing P1/P2/P6 tiers for bug-type items, read the {{paths.bug_backlog}} entry referenced in the Source column to determine the native severity classification (🔴/🟡/🟢/⚪).

### P4 Validation Record Lookup

When computing P3 tier for feature-type items, check `{{paths.validation}}` for a validation record matching the item's source reference. If a passing validation exists, promote from P4 to P3.

## Intra-Tier Scoring Formula

Within the same priority tier, items are ranked by score (higher = scheduled first):

```
score = (currentSprint - Age) + (Def × 2) + (hasDraft ? 1 : 0)
```

| Component               | Weight | Rationale                                      |
| ------------------------ | ------ | ---------------------------------------------- |
| `currentSprint - Age`   | 1×     | Older items rank higher (time in backlog)      |
| `Def × 2`               | 2×     | Repeatedly deferred items get urgency boost    |
| `hasDraft ? 1 : 0`      | 1      | Items with draft plans are ready to execute    |

Ties are broken by {{ids.item_prefix}}-NNN order (lower ID first).

## Composition Constraints

| Constraint          | Rule                                                                              |
| ------------------- | --------------------------------------------------------------------------------- |
| Feature cap         | Features (P3 + P4) ≤ {{escalation.feature_cap_percent}}% of sprint capacity                                      |
| Bug inclusion       | If any P1 or P2 bugs exist, at least one must be included                         |
| Debt pressure       | If debtPressure (sum of Def across all open items) > 10, at least one high-Def item must be included |
| Sprint size         | Target {{escalation.sprint_size_min}}–{{escalation.sprint_size_max}} task groups per sprint (velocity reference from {{paths.sprints_doc}})            |
| P0 mandatory        | All P0 items must be included — they cannot be deferred                           |

## P0 Overflow Relief Valve

If P0 items alone consume > {{escalation.p0_overflow_percent}}% of sprint capacity:

1. Flag an advisory: "Debt sprint recommended — P0 overflow detected."
2. Present the user with options:
   - **Debt sprint:** Schedule only P0 + P1 items, no new features.
   - **Split:** Break large P0 items into smaller increments across 2 sprints.
   - **Kill:** Review P0 items for kill candidates (items that are no longer relevant).
3. Do NOT proceed with composition until the user chooses.

## Debt Health Monitor

Constants for monitoring technical debt accumulation:

| Constant               | Value | Trigger                                                              |
| ---------------------- | ----- | -------------------------------------------------------------------- |
| `DEBT_WARNING_SPRINTS` | {{escalation.debt_warning_sprints}}     | Warn if any debt item has Def {{escalation.def_p0_threshold}} (also triggers P0 escalation)     |
| `DEBT_ESCALATE_SPRINTS`| {{escalation.debt_escalate_sprints}}     | Escalate: must resolve or kill (no further deferral)                 |
| `DEBT_WARNING_ITEMS`   | {{escalation.debt_warning_items}}    | Warn if debtPressure {{escalation.debt_warning_items}}                                            |
| `DEBT_ESCALATE_ITEMS`  | {{escalation.debt_escalate_items}}    | Escalate: debtPressure {{escalation.debt_escalate_items}} — mandatory debt sprint before any new features |
| `DEBT_MIN_ALLOCATION`  | {{escalation.debt_min_allocation_percent}}    | When debt pressure advisory active, {{escalation.debt_min_allocation_percent}}% capacity allocated to debt |

### Debt Pressure Score

```
debtPressure = sum(Def) across all open items
```

When `debtPressure` exceeds `DEBT_WARNING_ITEMS` ({{escalation.debt_warning_items}}), include a debt health warning in the composition output. When it exceeds `DEBT_ESCALATE_ITEMS` ({{escalation.debt_escalate_items}}), block feature-only sprints.

## Override Protocol

The user may override any composition constraint or priority assignment. When overriding:

1. The user states the override and rationale.
2. `/compose-sprint` records the override in the composition rationale file (`sprint-{N}-composition.md`).
3. The override applies to the current composition only — it does not change the rules in this file.
4. If the same override is applied 3+ times, flag a SUGGESTION to update this instruction file.
