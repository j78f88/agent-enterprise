# Backlog Ledger

Single source of truth for all backlog item status. Detail and context live in BUG_BACKLOG.md and HANDOFF_REJECTIONS.md — this file tracks status only.

| ID | Type | Source | Age | Def | Sprint | Status | Blocked | Draft | Notes |
|----|------|--------|-----|-----|--------|--------|---------|-------|-------|
| ITEM-006 | bug | BUG-003 | 0 | 0 | 2 | done | | | Onboarding missing Claude Code /command setup |
| ITEM-007 | bug | BUG-004 | 0 | 0 | 2 | done | | | Planner-mode workflow bypassed before approved sprint draft |
| ITEM-008 | bug | BUG-005 | 0 | 0 | 1 | done | | ../archive/onboarding-path-resolution-remediation-draft-plan.md | RESOLVED Sprint 1 — companion-file resolution, skills_deploy_dir cross-refs, inline code-span resolution + escape; all 3 BUG-005 mechanisms closed |
| ITEM-009 | audit-finding | Sprint 1 review SUGGESTION #2 | 1 | 0 | 2 | done | | | `SOURCE_STYLE_REFS` in tests/test_init.py is a hardcoded 7-item allowlist; consider deriving it from config/resolved tree instead of maintaining by hand |
| ITEM-010 | debt | Sprint 1 retro | 1 | 0 | 2 | done | | | Decide whether SPRINTS.md and BACKLOG_LEDGER.md hold real repo history or stay as template demo content |
| ITEM-011 | debt | Sprint 1 retro | 1 | 0 | 2 | done | | | Consider a CI check asserting all docs use config/project.config.example.yml for the canonical build command |
| ITEM-012 | bug | BUG-006 | 0 | 0 | 2 | done | | | init.py has no automated deploy-copy or token-free guardrail for the .github tree (distinct from BUG-005) |
| ITEM-013 | debt | Sprint 2 retro (@security/@reviewer SUGGESTION) | 2 | 0 | 3 | done | | | jsonschema.RefResolver deprecated in jsonschema ≥4.18; pre-existing warning, no immediate failure, migrate to jsonschema.validators API before upgrading jsonschema |
| ITEM-014 | feature | session review 2026-06-10 | 0 | 0 | 3 | done | | ../archive/claims-foundation-draft-plan.md | ADR 0008: define supported-mode-implementation promotion contract; revise command-centre/PLAN.md non-goal |
| ITEM-015 | debt | session review 2026-06-10 | 0 | 0 | 3 | done | | ../archive/claims-foundation-draft-plan.md | Stale drafts cleanup: archive completed draft plans, relocate handoff, triage remaining |
| ITEM-016 | debt | session review 2026-06-10 | 0 | 0 | 3 | done | | ../archive/claims-foundation-draft-plan.md | CI builds all profiles/*.config.yml, not just the example config |
| ITEM-017 | feature | session review 2026-06-10 | 0 | 0 | 3 | open | | drafts/platform-parity-draft-plan.md | Platform parity: ungate agent generation; native Claude Code subagents, Cursor commands, Codex AGENTS.md target |
| ITEM-018 | feature | session review 2026-06-10 | 0 | 0 | 3 | open | | drafts/mode2-dispatcher-promotion-draft-plan.md | Promote Mode 2 file-queue dispatcher to supported implementation in src/ per ADR 0008 |
| ITEM-019 | feature | session review 2026-06-10 | 0 | 0 | 3 | open | | drafts/mode3-coordinator-promotion-draft-plan.md | Promote Mode 3 registry coordinator to supported implementation in src/ per ADR 0008 |
| ITEM-020 | feature | session review 2026-06-10 | 0 | 0 | 3 | open | | drafts/adopter-bootstrap-draft-plan.md | Adopter bootstrap: init.py --target/--bootstrap one-line setup into external projects |
| ITEM-021 | debt | Sprint 3 review SUGGESTION | 0 | 0 | 3 | open | | | CI: run canonical example-config build last so post-build guardrail steps validate the canonical tree, not the last profile build |
| ITEM-022 | debt | Sprint 3 review SUGGESTION | 0 | 0 | 3 | open | | | ADR 0008 wording: disambiguate "promotion contract" vs 05-promotion-contract.md; add explicit ADR 0004 cross-reference |

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
