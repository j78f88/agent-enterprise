# Sprint Tracking

**Last Completed: Sprint 3**

---

## Sprint 4 — Platform Parity: Native Emission for Claude Code, Cursor, and Codex

**Status:** Active  
**Type:** Feature (claims-truth / build-system)  
**Started:** 2026-06-10

### Goals

- [ ] Ungate agent generation per editor.target; add codex target (ITEM-017)
- [ ] Native Claude Code subagents in .claude/agents/ (ITEM-017)
- [ ] Cursor .cursor/commands/ seeding (ITEM-017)
- [ ] Codex AGENTS.md managed-block emission, dogfooded (ITEM-017)
- [ ] tests/test_platform_emission.py + CI editor.target dimension (ITEM-017)
- [ ] CI canonical-build-last ordering fix (ITEM-021)
- [ ] docs/PLATFORMS.md + README truth pass (ITEM-017)

### Tasks

- [ ] TG1: ungate agent generation per target
- [ ] TG2: Claude Code native subagents
- [ ] TG3: Cursor commands seeding
- [ ] TG4: Codex AGENTS.md managed block
- [ ] TG5: parametrized platform emission tests
- [ ] TG6: CI editor.target dimension + ITEM-021 ordering
- [ ] TG7: docs/PLATFORMS.md + README truth pass

### Notes

- Sprint started 2026-06-10 (promoted from platform-parity draft; user approved)
- Sprint contract includes fixing any CI failures observed on the PR branch

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


<!-- 
Archive rule: when Sprint N completes, move Sprint N-2 entry to docs/archive/
Format: one H2 per sprint, most recent at top.
-->
