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

<!-- ACTUALS — completed by @sprint-lead 2026-06-10 -->

## Section 0: Forecast vs. Actual

**Previous Action Items: Status** (from Sprint 3 §7)

| Action Item | Target | Status |
| ----------- | ------ | ------ |
| CI canonical-build-last ordering | ITEM-021 | ✅ Done — TG6 reordered the workflow; canonical build runs last |
| ADR 0008 wording disambiguation | ITEM-022 | ⏸ Open — not in this sprint's scope |

**Complexity Comparison**

| Task | Forecast | Actual | Accurate? |
| ---- | -------- | ------ | --------- |
| TG1 ungate | moderate | moderate | ✅ |
| TG2 Claude subagents | moderate | moderate | ✅ |
| TG3 Cursor commands | straightforward | straightforward | ✅ |
| TG4 Codex managed block | complex | complex (3 review findings: duplicate markers, CRLF, plus the B1 staleness interaction) | ✅ |
| TG5 emission tests | moderate | moderate | ✅ |
| TG6 CI dimension | straightforward | straightforward | ✅ |
| TG7 docs | straightforward | straightforward | ✅ |

**Assumptions Check**

| Assumption | Held? | Notes |
| ---------- | ----- | ----- |
| Sprint 3 foundations stable; 431 green at start | ✅ | 431 → 533 over the sprint. |
| transform path composes without contract changes | ✅ | codex is an explicit no-op branch; no frozen contract touched. |
| No frozen contract touched | ✅ | |

**Risk Area Accuracy**

- **TG4 AGENTS.md merge** (predicted highest-risk) — correct: review probing found duplicate-marker splicing and CRLF normalization; both fixed with guards + tests. The marker contract held for the cases tests covered.
- **TG1 behaviour change** (predicted) — materialized indirectly: ungating exposed the latent post-deploy scan failure on escaped literals (fix pass 1) and the stale-wrapper staleness became the review BLOCKER (B1) once the dogfood deploy ran.
- **Sprint-2-precedent fix-loop budget** (predicted) — confirmed: 3 fix passes (escaped-literal scan, guardrail punctuation, review fixes), all caught by the repo's own gates/review rather than by CI after merge.

**Forecast Calibration Score** — Assumptions 3/3, Complexity 7/7: **100%** (forecast seeded at promotion for the first time, per the Sprint 3 action item).

## Section 1: Sprint Summary

- Tasks planned / completed / blocked / partial: **7 / 7 / 0 / 0**
- New files: emit/seed code paths in `init.py`, `tests/test_platform_emission.py`, `docs/PLATFORMS.md`; new committed platform surfaces `.claude/agents/`, `.cursor/rules/`, `.cursor/commands/`, AGENTS.md managed block
- Sprint type: **feature** (claims-truth / build-system)

## Section 2: Execution Timeline

| Phase | Notes |
| ----- | ----- |
| 1 Kickoff | Promotion + forecast seeding + ITEM-021 folded into TG6. |
| 2 Implementation | TG1 solo → TG2/TG3/TG4 parallel → fix pass (post-deploy scan + dogfood config) → TG5/TG6/TG7 parallel → fix pass (guardrail punctuation, onboarding canonical command). 7 TG subagents + 2 fix passes. |
| 2.5/3 Gates | @qa ×1 — all gates pass, replicating CI step order exactly. |
| 4 Review | @reviewer ×1 — REQUEST-CHANGES: 1 BLOCKER + 9 SUGGESTIONs; blocker + 7 suggestions fixed in-sprint (fix pass 3), S8 → ITEM-023, S9 → CHANGELOG. |
| 5 Docs | CHANGELOG Unreleased § Sprint 4. |
| 6 Retro | This file; ledger/SPRINTS close-out; archive rule applied (Sprint 2 → docs/archive/sprint-history.md). |

## Section 3: Fix Loops

| Fix # | Trigger | Root Cause | Resolution |
| ----- | ------- | ---------- | ---------- |
| 1 | --deploy exit 1 on onboarding docs | Post-deploy scan ran on stripped files where escaped literals look like leaks | find_unresolved_real_tokens (dotted-only) at the 5 post-deploy sites; convention documented; CLAUDE_CODE_SETUP.md rewritten brace-free |
| 2 | check_build_command FAIL on perf SKILL + onboarding | Guardrail captured trailing quote punctuation; repo commands.build pointed at itself; non-canonical deploy example | Punctuation strip + canonical command token + canonical deploy example |
| 3 | Review B1 + S1-S7 | Stale resolved/agents wrappers survive setup-skip and get re-deployed (zombie onboarding artifacts); emission edge cases | Wrapper pruning + deploy-side stale cleanup + regression tests; YAML-safe descriptions, duplicate-marker guard, CRLF preservation, multi-dot scanners, ungated claude_agents scan, both/all in CI loop |

## Section 4: Quality Results

- Unit tests: **533 passed / 0 failed / 11 skipped** (+102 this sprint); green with `-W error::DeprecationWarning`.
- Determinism: build and deploy byte-identical across double runs; clean-clone reproducibility explicitly verified after the B1 fix (rm -rf resolved/ → rebuild+deploy → no drift).
- Guardrails: check_tokens.py, check_build_command.py exit 0; CI step order replicated locally end-to-end.
- A11y / Perf: N/A.

## Section 5: Code Review

| Severity | Count | Resolution |
| -------- | ----- | ---------- |
| BLOCKER | 1 | ✅ fixed in-sprint — zombie onboarding artifacts; clean-clone reproducibility restored, regression-tested |
| SUGGESTION | 9 | 7 fixed in-sprint (S1-S7); S8 → ITEM-023; S9 delivered via CHANGELOG |

## Section 6: Retrospective

**What went well**
- The dogfood requirement did its job: deploying the repo's own config surfaced two latent defects (escaped-literal scan, stale-wrapper zombies) that no adopter had hit yet.
- Forecast seeded at promotion and scored 100% — the Sprint 3 process fix landed.
- Commit hygiene held: explicit pathspecs throughout; one staging slip (untracked file with `git commit --`) caught immediately, no history damage.
- Review depth: the reviewer empirically probed the merge function (fences, CRLF, duplicates) rather than reading it — found real defects tests had missed.

**What didn't go well**
- A subagent ran `--deploy` with the example config against the real repo, overwriting tracked deployed trees with "My Project" artifacts (restored via git checkout). Subagent prompts now need explicit "which config" instructions for deploy-capable tasks.
- The platform-emission test module asserted artifact sets but missed the staleness dimension entirely (B1) — matrix tests pin what IS emitted, not what should no longer be.

**Start / Stop / Continue**
- **Start:** including a "stale state" dimension when testing emitters (build A → change config → build B → assert A's artifacts gone).
- **Stop:** letting deploy-capable subagents choose their own config file.
- **Continue:** empirical-probing review style; forecast-at-promotion; CI-order-replicating QA gates.

**Action Items**

| Action Item | Target |
| ----------- | ------ |
| Decouple onboarding skill walkthrough from the canonical-build-command guardrail | ITEM-023 |
| ADR 0008 wording disambiguation (carried) | ITEM-022 |

## Section 7: Carry-Over

No functional carry-over. Open suggestion-level items: ITEM-022 (carried from Sprint 3), ITEM-023 (new). Codex managed-block fence-awareness documented as a known limitation in docs/PLATFORMS.md rather than implemented.

## Section 8: Sprint Trends

| Metric | Sprint 2 | Sprint 3 | Sprint 4 | Signal |
| ------ | -------- | -------- | -------- | ------ |
| Tasks planned / completed | 7 / 7 | 6 / 6 | 7 / 7 | ● |
| Fix iterations | 9 | 2 | 3 passes (12 findings) | ● |
| Review BLOCKER/CRITICALs | 1 (fixed) | 1 (fixed) | 1 (fixed) | ● |
| Test count delta | +30 | 0 | +102 | ▲ |
| Forecast calibration | 100% | not seeded | 100% | ▲ |

**Drift Analysis** — implementation-heavy sprints reliably produce ~1 blocker-class defect caught by review, never by tests alone; the review gate remains the highest-value step. Test growth (+102) tracked new emission surface 1:1.

## Section 9: Owner Notes
_Reserved for project owner — no agent writes here._

<!-- /ACTUALS -->
