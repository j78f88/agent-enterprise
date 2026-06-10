# Sprint 4 Retrospective — Platform Parity: Native Emission for Claude Code, Cursor, and Codex

<!-- FORECAST — seeded by @sprint-lead at promotion 2026-06-10 -->

## Sprint Forecast

### Sprint Type

`feature` (claims-truth / build-system)

### Per-Task Complexity Forecast

| Task | Expected Complexity | Reasoning |
| ---- | ------------------- | --------- |
| TG1 – ungate agent generation per target | moderate | Behaviour change in the build's central gate (`init.py:1102-1124`); must compose with the existing cursor transform path without duplicating emission. |
| TG2 – Claude Code native subagents | moderate | New output directory + token, but mirrors the proven `.claude/commands/` seeding pattern. |
| TG3 – Cursor commands seeding | straightforward | Direct mirror of existing seeding logic with an existing frontmatter transform. |
| TG4 – Codex AGENTS.md managed block | complex | Writes into an adopter-owned file; merge semantics (markers, idempotency, no-clobber) carry the sprint's highest defect risk. |
| TG5 – parametrized platform emission tests | moderate | New test module across 6 target values; needs temp-dir builds and byte-level determinism assertions. |
| TG6 – CI target dimension + ITEM-021 ordering | straightforward | Extends the Sprint 3 loop; reorder so canonical build runs last. |
| TG7 – docs/PLATFORMS.md + README truth pass | straightforward | Documentation of what TG1–5 prove; removes the Sprint 3 footnote. |

### Risk Areas

1. **TG4 merge into `AGENTS.md`** — adopter-owned file; a marker bug loses user content. Tests must cover pre-existing content, missing markers, duplicate markers.
2. **TG1 behaviour change** for existing `claude-code`/`cursor` configs that silently skipped agent generation — pinned by TG5's per-target artifact-set assertions and a CHANGELOG entry.
3. **Sprint-2 precedent**: implementation-heavy sprints produced 9 fix iterations; budget for fix loops, especially in scripts/regex-adjacent code (the marker merge).

### Assumptions

- Sprint 3 foundations (ADR 0008, CI profile matrix) are stable; suite green at 431 at sprint start.
- The existing `transform_frontmatter_for_target` path composes with new targets without contract changes.
- No frozen contract (`protocol-v1`, mode contracts) is touched by any TG.

### Expected Gate Outcomes

| Gate | Outcome | Reasoning |
| ---- | ------- | --------- |
| standard (pytest) | PASS after fix loops | New emission code + new test module; first-pass failures likely in TG4/TG5. |
| Determinism | PASS | Sorted iteration + no timestamps is an explicit acceptance criterion per TG. |
| guardrail | PASS | New target dirs added to the post-deploy token scan in TG3/TG5. |
| CI (PR branch) | PASS | Sprint contract: any failing check on the PR branch is fixed before close. |

### Scope Estimate

- Files: `init.py`, example config + 3 profiles, `AGENTS.md`, `tests/test_platform_emission.py` (new), `tests/test_init.py`, `.github/workflows/ci.yml`, `docs/PLATFORMS.md` (new), `README.md`, `docs/ONBOARDING.md`, `skills/onboarding/*`
- Estimated lines changed: ~400–600
- Subagents: 7 implementation (TG1 → TG2/TG3/TG4 parallel → TG5 → TG6 → TG7)

### Watch Items

- TG1 → TG2/3/4 sequencing is load-bearing: emission targets depend on the ungated dispatch.
- Commit with explicit pathspecs while parallel subagents are active (Sprint 3 retro lesson).
- Cross-check subagent self-reports against `git status` (Sprint 3 retro lesson).

<!-- /FORECAST -->
