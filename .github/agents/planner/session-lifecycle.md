# Planner Session Lifecycle

## Context Continuity (Session Start)

At the **start** of any planning session:

1. **Check `docs/planning/_handoffs/`** for manifests addressed to `@planner`. If found, present the most recent: "I see a handoff from @X about `<slug>` — proceed with that?" On acceptance, archive it to `docs/planning/_handoffs/archive/`.
2. **Read ledger summary** from `docs/planning/BACKLOG_LEDGER.md` — note open item counts by type, escalated items (Def ≥ 3), and debt pressure score. Present a one-line status: "Ledger: X open items (Y bugs, Z debt), N escalated (Def ≥ 3), debt pressure: P."
3. **List files in `docs/planning/drafts/`** — ignore `_`-prefixed files.
4. **Triage by type** — brainstorms (`-brainstorm.md`) vs draft plans (`-draft-plan.md`). If brainstorms exist, offer: "I see existing brainstorms — would you like to harvest features from them?"
5. **Surface unfinished work** — for each brainstorm, scan for `[SELECTED]` markers and check whether a corresponding `-draft-plan.md` exists. Report status.
6. Present drafts: "Are any of these related to what you're working on?"
7. Do not rely on fuzzy matching — let the user confirm.
8. If identified, read and incorporate as prior context.

---

## Health Check (Auto — Every Session Start)

Before any workflow, silently run a contamination scan:

1. List files in `sprints/` — flag any with `DRAFT` status header (leaked draft).
2. Check `SPRINTS.md` — flag entries pointing to non-existent PLAN.md files (phantom entries).
3. If issues found: STOP, report, offer to fix before proceeding.
4. If clean: proceed silently (no output).

---

## Carry-Over Escalation Gate

Before finalizing any sprint plan:

1. Read the ledger for items with Def ≥ 3 (P0 mandatory).
2. If any exist, surface them via `#tool:askQuestions`: "N carry-over items have Def ≥ 3 (mandatory P0). Include in this plan, schedule separately, or kill?"
3. Items with Def ≥ 5: escalate more forcefully — must be resolved or killed, no further deferral permitted.
4. You **never** silently omit P0 items from a plan — the user must explicitly choose.

---

## RETRO.md Forecast Seeding

When promoting a draft plan to `sprints/sprint-N/PLAN.md` (and the sprint is NOT part of an engagement):

1. Write `sprints/sprint-N/RETRO.md` per `.github/instructions/retro-report.instructions.md` § Seeded RETRO.md Structure.
2. Copy `## Sprint Forecast` from the plan if present.
3. Pre-populate §9 (Carry-Forward) with deferred items from the ledger.
4. Commit the seeded RETRO.md in the same commit as the promoted PLAN.md.

---

## Handoff Rejections (Loopback Protocol)

When scoping a handoff that **cannot be cleanly scoped** (scope too large, ADR conflict, missing dependencies, contradictions):

1. You **never** silently scale down or drop conflicting parts.
2. Append a REJ-NNN entry to `docs/planning/HANDOFF_REJECTIONS.md`. Required fields: Severity, From, To, Raised, Status (OPEN), Context, Reason, Proposed resolution.
3. Surface the REJ to the user via `#tool:askQuestions`: reject back, override, or save and pause.
4. You **do not** proceed with the original handoff until the user chooses.

**Triggers:** >3 stores touched without ADR support; NON_GOAL conflict; ADR contradiction; missing source context.

---

## Handoff Manifest

Before showing any handoff button, write a manifest to `docs/planning/_handoffs/<date>-planner-to-<to>-<slug>.md`:

```markdown
---
from: "@planner"
to: "@sprint-lead"
date: YYYY-MM-DD
feature: <slug>
artifact: sprints/sprint-N/PLAN.md
status: promoted
notes: <one-line context summary>
---
```

Also present a copy-pasteable context block as fallback.
