# Sprint Tracking

**Last Completed: Sprint 5**

---

## Sprint 5 — Mode 2 Dispatcher Promotion: Supported Implementation in src/

**Status:** Complete  
**Type:** Feature (mode promotion per ADR 0008)  
**Started:** 2026-06-10  
**Completed:** 2026-06-10

### Goals

- [x] src/mode2_dispatcher/ package: core port, discovery, durable queue, return validation (ITEM-018)
- [x] Root CLI dispatch.py (run/status/requeue/validate-callables) (ITEM-018)
- [x] Crash-resume + atomic state proven by tests (ITEM-018)
- [x] Shared mode-2-contract-v1 conformance over both impls; reference impl byte-frozen (ITEM-018)
- [x] docs/ORCHESTRATION.md + install-contract names the supported impl (ITEM-018)

### Tasks

- [x] TG1: src/mode2_dispatcher/ core port
- [x] TG2: callable discovery (discovery.py)
- [x] TG3: durable queue (queue_file.py) + returns.py
- [x] TG4: root CLI dispatch.py
- [x] TG5: tests/test_mode2_dispatcher.py
- [x] TG6: shared conformance parametrization + byte-freeze test
- [x] TG7: adopter docs + install contract + README/CHANGELOG

### Notes

- Sprint started 2026-06-10 (promoted from mode2-dispatcher-promotion draft; user approved)
- Sprint completed 2026-06-10; retro at sprints/sprint-5/RETRO.md

---

## Sprint 4 — Platform Parity: Native Emission for Claude Code, Cursor, and Codex

**Status:** Complete  
**Type:** Feature (claims-truth / build-system)  
**Started:** 2026-06-10  
**Completed:** 2026-06-10

### Goals

- [x] Ungate agent generation per editor.target; add codex target (ITEM-017)
- [x] Native Claude Code subagents in .claude/agents/ (ITEM-017)
- [x] Cursor .cursor/commands/ seeding (ITEM-017)
- [x] Codex AGENTS.md managed-block emission, dogfooded (ITEM-017)
- [x] tests/test_platform_emission.py + CI editor.target dimension (ITEM-017)
- [x] CI canonical-build-last ordering fix (ITEM-021)
- [x] docs/PLATFORMS.md + README truth pass (ITEM-017)

### Tasks

- [x] TG1: ungate agent generation per target
- [x] TG2: Claude Code native subagents
- [x] TG3: Cursor commands seeding
- [x] TG4: Codex AGENTS.md managed block
- [x] TG5: parametrized platform emission tests
- [x] TG6: CI editor.target dimension + ITEM-021 ordering
- [x] TG7: docs/PLATFORMS.md + README truth pass

### Notes

- Sprint started 2026-06-10 (promoted from platform-parity draft; user approved)
- Sprint contract includes fixing any CI failures observed on the PR branch
- Sprint completed 2026-06-10; retro at sprints/sprint-4/RETRO.md

---


<!-- 
Archive rule: when Sprint N completes, move Sprint N-2 entry to docs/archive/
Format: one H2 per sprint, most recent at top.
-->
