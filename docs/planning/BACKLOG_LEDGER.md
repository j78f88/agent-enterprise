# Backlog Ledger

Single source of truth for all backlog item status. Detail and context live in BUG_BACKLOG.md and HANDOFF_REJECTIONS.md — this file tracks status only.

| ID | Type | Source | Age | Def | Sprint | Status | Blocked | Draft | Notes |
|----|------|--------|-----|-----|--------|--------|---------|-------|-------|
| ITEM-001 | feature | User feedback | 0 | 0 | 1 | open | | drafts/auth-flow.md | OAuth integration |
| ITEM-002 | bug | BUG-001 | 1 | 0 | 1 | assigned | | | Login redirect broken |
| ITEM-003 | debt | Code review | 2 | 1 | 2 | open | Waiting on ITEM-001 | | Refactor auth module |
| ITEM-004 | feature | Roadmap | 0 | 0 | — | open | | | Dashboard widgets |
| ITEM-005 | carry-over | Sprint 1 | 1 | 1 | 2 | assigned | | | API rate limiting |
| ITEM-006 | bug | BUG-003 | 0 | 0 | — | open | | | Onboarding missing Claude Code /command setup |
| ITEM-007 | bug | BUG-004 | 0 | 0 | — | open | | | Planner-mode workflow bypassed before approved sprint draft |
| ITEM-008 | bug | BUG-005 | 0 | 0 | 1 | assigned | | drafts/onboarding-path-resolution-remediation-draft-plan.md | init.py leaves unresolved path tokens in deployed skills/docs |

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
