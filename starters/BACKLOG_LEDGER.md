# Backlog Ledger

Single source of truth for all backlog item status. Detail and context live in BUG_BACKLOG.md and HANDOFF_REJECTIONS.md — this file tracks status only.

| ID | Type | Source | Age | Def | Sprint | Status | Blocked | Draft | Notes |
|----|------|--------|-----|-----|--------|--------|---------|-------|-------|

<!-- 
Column guide:
  ID       — ITEM-NNN (sequential, zero-padded)
  Type     — bug | debt | feature | carry-over | audit-finding | research | rejection
  Source   — BUG-NNN, REJ-NNN, or free text
  Age      — sprints since first logged
  Def      — times deferred (≥3 → P0 mandatory, ≥5 → must resolve or kill)
  Sprint   — sprint number first logged
  Status   — open | assigned | done | killed
  Blocked  — blocker description or blank
  Draft    — draft filename or blank
  Notes    — free text

Governance:
  @bug     — appends bug items
  @planner — appends feature, debt, rejection items; marks done/killed
  @sprint-lead — updates status to assigned during sprint, done at completion
-->
