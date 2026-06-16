# Sprint History (archived)

Entries moved out of SPRINTS.md per the archive rule
(when Sprint N completes, Sprint N-2 moves here). Most recent at top.

---

## Sprint 3 — Claims Foundation: ADR, Debt, and Roadmap Seeding

**Status:** Complete  
**Type:** Mixed (feature-enabling / debt / hygiene)  
**Started:** 2026-06-10  
**Completed:** 2026-06-10

### Goals

- [x] ADR 0008 supported-mode-implementations; revise PLAN.md non-goal (ITEM-014)
- [x] Migrate `jsonschema.RefResolver` → `referencing` (ITEM-013)
- [x] Stale drafts cleanup + archive (ITEM-015)
- [x] CI builds all profiles (ITEM-016)
- [x] Interim README Codex honesty footnote
- [x] Seed four roadmap draft plans + ledger ITEMs (ITEM-017..020)

### Tasks

- [x] TG1: ADR 0008 + PLAN.md non-goal revision (ITEM-014)
- [x] TG2: RefResolver → referencing migration (ITEM-013)
- [x] TG3: stale drafts cleanup/archive (ITEM-015)
- [x] TG4: CI profile build matrix (ITEM-016)
- [x] TG5: README Codex footnote
- [x] TG6: seed four roadmap drafts + ledger (ITEM-017..020)

### Notes

- Sprint started 2026-06-10 (roadmap approved in-session)
- Sprint completed 2026-06-10; retro at sprints/sprint-3/RETRO.md

---

---

## Sprint 2 — Build-System Hardening & Process Hygiene

**Status:** Complete  
**Type:** Mixed (bug-fix / debt)  
**Started:** 2026-05-31  
**Completed:** 2026-05-31

### Goals

- [x] Automated deploy-copy + fail-on-unresolved (BUG-006 / ITEM-012)
- [x] Token-free guardrail for the deployed `.github/` tree (ITEM-012)
- [x] CI canonical-build-command check (ITEM-011)
- [x] Derive `SOURCE_STYLE_REFS` from config/resolved tree (ITEM-009)
- [x] Claude Code `/command` seeding + onboarding docs (BUG-003 / ITEM-006)
- [x] Planner-mode draft-approval checkpoint (BUG-004 / ITEM-007)
- [x] Purge demo/template content from ledger and SPRINTS (ITEM-010)

### Tasks

- [x] TG1: deploy-copy step + fail-on-missing-key (ITEM-012)
- [x] TG2: token-free guardrail script + CI step (ITEM-012)
- [x] TG3: CI canonical-build-command check (ITEM-011)
- [x] TG4: derive `SOURCE_STYLE_REFS` from config/resolved tree (ITEM-009)
- [x] TG5: Claude Code `/command` seeding + onboarding docs (ITEM-006)
- [x] TG6: planner-mode checkpoint enforcement (ITEM-007)
- [x] TG7: purge demo/template content — ledger, bug backlog, SPRINTS (ITEM-010)

### Notes

- Sprint started 2026-05-31
- Sprint completed 2026-05-31

---

---

## Sprint 1 — Onboarding Path Resolution Remediation

**Status:** Complete  
**Type:** fix (build-system debt / bug-fix)  
**Started:** 2026-04-27  
**Completed:** 2026-05-30

### Goals

- [x] Resolve and deploy skill companion files
- [x] Resolve inline code-span tokens with two-phase escape
- [x] Cross-references use deploy path (`paths.skills_deploy_dir` token)

### Tasks

- [x] TG1 (A): companion-file resolution loop + setup-skip interaction
- [x] TG2 (C): `paths.skills_deploy_dir` token + cross-reference rewrites
- [x] TG3 (B): inline code-span policy + two-phase escape (preserve → strip after scans)
- [x] Review fix: agent-wrapper refs corrected to deploy path

### Retro Summary

- **Velocity:** 3 task groups + 1 review-fix; 100% completion rate
- **Carry-over:** none
- **Forecast calibration:** 100% (3/3 assumptions, 3/3 complexity)
- **Process notes:** Escape must preserve marker through scans; strip-after-scan ordering is now test-locked.

---
