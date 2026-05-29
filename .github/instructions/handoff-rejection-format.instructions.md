---
id: instruction.handoff-rejection-format
kind: instruction
version: 1.0.0
applies_to: '**'
description: handoff-rejection-format instruction
applyTo: '**'
---

# Handoff Rejection Format

Single schema and lifecycle specification for `{{paths.rejections}}`. Mirrors the `bug-backlog-format` pattern.

> **Why this exists:** handoffs between agents (e.g., `@pm → @planner`, `@architect → @planner`) are currently one-directional. When a receiving agent discovers the handoff cannot be cleanly scoped — scope too large, conflicts with an ADR, missing dependency — there needs to be a structured place to record the rejection and loop back to the upstream agent with context. Without this, rejections happen informally and the upstream agent loses signal.

> **Status tracked in docs/planning/BACKLOG_LEDGER.md — this file holds rejection context only.**

## Entry Format

```markdown
### REJ-NNN — <one-line summary>

- **Severity:** 🔴 Blocker / 🟡 Scope mismatch / 🟢 Needs refinement
- **From:** <receiving agent that is rejecting, e.g., @planner>
- **To:** <upstream agent that needs to reconsider, e.g., @pm / @architect / @researcher>
- **Raised:** YYYY-MM-DD
- **Ledger:** ITEM-NNN
- **Context:** What was handed over (feature slug, ADR number, research doc name)
- **Reason:** Why it can't be scoped as handed over — cite the specific conflict (ADR-NNN broken, N stores touched, missing dependency X)
- **Fix:** One-sentence actionable step the upstream agent can take next ("Split feature into A and B", "Resolve ADR-014 ambiguity on caching", "Wait for X dependency to land")
- **Link:** Path to the constraining doc, ADR, instruction, or ticket (e.g. `docs/adr/ADR-014.md`, `docs/sprints/sprint-007/PLAN.md#dependencies`). At least one link is required.
- **Proposed resolution:** What the rejecting agent thinks should happen — split into N features, defer until Y, re-approach via Z
- **Response:** (upstream agent fills in when revising — what they changed and why)
```

## ID Assignment

`{{ids.rejection_prefix}}-NNN`, zero-padded to 3 digits, sequential. Read `{{paths.rejections}}` to find the highest existing N; assign N+1.

## Severity

- 🔴 **Blocker** — cannot proceed at all; upstream must revise or user must override.
- 🟡 **Scope mismatch** — could proceed but at a cost not justified by the handoff (scope creep, partial solution).
- 🟢 **Needs refinement** — minor gap that upstream can patch quickly; rejection is advisory rather than halting.

## Writer Discipline

| Agent | Permission |
| --- | --- |
| `@planner` | Appends new REJ-NNN entries below `<!-- @planner appends new entries below this line -->` marker. Never edits existing entries except to add its own **Response:** block if @planner is the "To" agent (rare — would be @planner → @planner, only via supersede). |
| `@pm` | Adds **Response:** block to entries where `To: @pm`. |
| `@architect` | Adds **Response:** block to entries where `To: @architect`. |
| `@researcher` | Adds **Response:** block to entries where `To: @researcher`. |
| User | May edit entries directly. |
| All other agents | No write access. |

## Loopback Recipe

When `@planner` encounters a blocking condition while executing `/plan-feature`, `/plan-fix`, or `/promote-draft`:

1. Write a REJ-NNN entry with Severity, From/To, Reason, Proposed resolution.
2. Surface via `askQuestions` with options:
   - "Reject back to `<upstream agent>` — I'll re-invoke with REJ-NNN as context"
   - "Override and proceed — update ledger Status to `killed` with override rationale in Notes"
   - "Save REJ and pause — come back to it later"
3. **Do not** proceed with the original handoff until the user chooses.

## Enforcement (for @reviewer)

- **CRITICAL:** Commit where `@planner` silently scaled down or dropped a feature scope that differs from the source `-draft-plan.md` without a corresponding REJ-NNN entry.
- **WARNING:** REJ entry with no **Proposed resolution** field populated.
- **WARNING:** new REJ entry with no **Fix** field (or `Fix: TBD` left in place at commit time).
- **WARNING:** new REJ entry with no **Link** field, or with a `Link:` value that does not resolve to an existing file or anchor.
- **SUGGESTION:** REJ entry OPEN for >14 days with no **Response:** — flag for supersession or closure.

## Handoff Manifest Cleanup

Handoff manifests in `{{paths.handoffs}}` track agent-to-agent hand-offs (separate from rejections above).

- When the promoted sprint completes, move the handoff manifest to `{{paths.handoffs}}archive/`.
- Handoffs that did not result in a sprint (abandoned or superseded) should also be archived with a note.
