# Sprint 1 Retrospective — Onboarding Path Resolution Remediation

<!-- FORECAST — seeded by @planner at promotion -->

## Sprint Forecast

### Sprint Type

`fix` (build-system debt / bug-fix)

### Per-Task Complexity Forecast

| Task | Expected Complexity | Reasoning |
| ---- | ------------------- | --------- |
| TG1 (A) companion-file resolution | moderate | Additive loop in `init.py` + setup-only skip interaction + new test. Isolated, low risk. |
| TG2 (C) cross-reference path token | moderate | New config token threaded through profiles + mechanical reference rewrites across several skill sources. Breadth, not depth. |
| TG3 (B) inline code-span policy + escape | complex | Changes long-standing `substitute()` behaviour with repo-wide blast radius; the literal audit across `skills/` + `instructions/` is the load-bearing, error-prone step. |

### Risk Areas

1. **TG3 literal audit** — every inline `{{token}}` must be classified real-reference vs. template-literal. A misclassification either resolves a literal that should survive, or leaves a real reference raw. Highest-surprise task.
2. **TG1 / setup-only interaction** — companions of skipped setup-only skills must also be skipped; easy to miss.

### Assumptions

- Fenced code blocks already resolve correctly (confirmed: deployed `a11y/SKILL.md` resolves `{{commands.e2e}}` in a bash block) — so only **inline** spans need the policy flip.
- The existing 393+ test suite is green at sprint start.
- No adopter relies on the current raw-token output as intended behaviour.

### Expected Gate Outcomes

| Gate | Outcome | Reasoning |
| ---- | ------- | --------- |
| standard (pytest) | PASS | New tests added per task group; existing suite unaffected by additive A/C. |
| Determinism | RISK | B's escape handling must be order-independent; double-run equality is the explicit check. |

### Scope Estimate

- Files: `init.py`, `config/project.config.yml` + profiles, multiple `skills/**` and `instructions/**` sources, new `tests/`.
- Estimated lines changed: ~150–300 (most in mechanical reference/escape edits).
- Subagents expected: 1–2 implementation subagents (A+C together, B separately behind the audit).

### Watch Items

- Sequencing A → C → B is load-bearing: B must run last, after C settles where companions/references land.
- The escape syntax (`\{{...}}` vs. alternative) is an implementation detail to lock early in TG3.

<!-- /FORECAST -->

<!-- ACTUALS — to be completed by @sprint-lead at sprint completion -->

## Section 0: Forecast vs. Actual

**Previous Action Items: Status** — No prior retrospective (Sprint 1 is the first real sprint) — skipping action item review.

**Complexity Comparison**

| Task | Forecast | Actual | Δ | Accurate? |
| ---- | -------- | ------ | - | --------- |
| TG1 (A) companion-file resolution | moderate | moderate | 0 | ✅ |
| TG2 (C) cross-reference path token | moderate | moderate | 0 | ✅ |
| TG3 (B) inline code-span policy + escape | complex | complex | 0 | ✅ |

**Assumptions Check**

| Assumption | Held? | Notes |
| ---------- | ----- | ----- |
| Fenced code blocks already resolve; only inline spans need the flip | ✅ | Confirmed — only inline `substitute()` behaviour changed in TG3. |
| Existing 393+ test suite green at start | ✅ | Ended at 401 passed / 7 skipped. |
| No adopter relies on raw-token output | ✅ | No change requests; treated as a defect. |

**Risk Area Accuracy**

- **TG3 literal audit** (predicted highest-surprise) — materialized differently: the audit itself was clean, but the *escape implementation* surprised us. The v1 escape stripped the backslash inline in `substitute()`, making escaped literals byte-identical to unresolved tokens, so post-substitution scans false-flagged them (2 test failures). Resolved by redesigning as a **two-phase** escape: `substitute()` preserves the `\{{...}}` marker, and a final `strip_escapes()` pass (after all scans) removes the backslash. Correct prediction of *where* risk lived (TG3), wrong about *which* sub-step.
- **TG1 / setup-only interaction** (predicted) — handled cleanly, no surprise; companions of skipped skills are skipped.
- **Missed risk:** the cross-reference rewrite (TG2) initially covered only skill-source companion refs and **missed the 13 agent-body wrappers**, which @reviewer caught (WARNING #1). The sprint Goal ("cross-references resolve to a path that exists in the adopter") was only partially met until the review-fix commit closed it.

**Forecast Calibration Score**

- Assumptions accuracy: 3/3 (100%)
- Complexity accuracy: 3/3 (100%)
- Combined: **100%**

## Section 1: Sprint Summary

- Tasks planned / completed / blocked / partial: **3 / 3 / 0 / 0** (+ 1 review-driven follow-up completed in-sprint)
- Files created/modified: `init.py`, `tests/test_init.py`, `config/project.config.yml` + `project.config.example.yml` (+ profiles), 13 `agents/*.body.md`, multiple `skills/**` cross-refs, `skills/onboarding/onboarding.skill.md` escape; docs sync touched `.github/copilot-instructions.md`, `docs/EXTENSION_GUIDE.md`, `docs/CUSTOMIZATION.md`, `CHANGELOG.md`, `src/__init__.py`, `config/plugin.json`.
- Sprint type: **fix** (build-system debt / bug-fix)

## Section 2: Execution Timeline

| Phase | Duration | Notes |
| ----- | -------- | ----- |
| Phase 1: Kickoff | — | Read PLAN + seeded RETRO forecast. |
| Phase 2: Implementation | — | TG1 → TG2 → TG3 in mandated order, one subagent per group. |
| Phase 2.5: Safety-Net | N/A | `typecheck`/`lint` commands are empty no-ops; pytest is the QA gate. |
| Phase 3: Quality Gates | — | pytest (401 pass) + determinism double-run. |
| Phase 4: Code Review | — | @reviewer APPROVE (0 critical, 2 warning, 3 suggestion); both warnings fixed in-sprint. |
| Phase 5: Documentation | — | @docs sync; reconciled build-command inconsistency, stale policy docs, changelog 3.0.2. |
| Phase 6: Retrospective | — | Ledger + RETRO. |

(Wall-clock durations not instrumented in this environment — no terminal timing available.)

## Section 3: Complexity Profile

| Task | Complexity | Lines +/- | Files | Fix Iterations | Commit |
| ---- | ---------- | --------- | ----- | -------------- | ------ |
| TG1 (A) companion resolution | moderate | — | `init.py`, `tests/` | 0 | `e4d0272` |
| TG2 (C) cross-ref path token | moderate | — | config + profiles + `skills/**` | 0 | folded into `e4d0272`/`8a33211` |
| TG3 (B) code-span + escape | complex | +102 / -44 | `init.py`, `tests/`, skill sources | 1 (two-phase redesign) | `8a33211` |
| Review fix (TG2 gap) | straightforward | — | 13 `agents/*.body.md`, `tests/` | 0 | `b0f0057` |

Complexity distribution: 2 moderate, 1 complex, 1 straightforward.

## Section 4: Process Health

- Subagent counts: 3 implementation (one per task group) + 1 review-fix (orchestrator-applied) + @reviewer + @docs.
- Gate reruns: pytest re-run after the TG3 two-phase redesign and again after the review fix.
- Blocked/partial tasks: none.
- Fix loop detail:

  | Fix # | Trigger | Root Cause | Files |
  | ----- | ------- | ---------- | ----- |
  | 1 | 2 pytest failures in TG3 | v1 escape stripped backslash inline in `substitute()`, so escaped literals were indistinguishable from unresolved tokens during scans | `init.py`, `tests/test_init.py` |

- Gate pass rate: PASS after fixes (401/408 run, 7 skipped).

## Section 5: Quality Results

- TypeScript: N/A (Python project)
- Lint: N/A (`commands.lint` empty no-op)
- Unit Tests: **401 passed / 0 failed / 7 skipped** (1 deprecation warning — `jsonschema.RefResolver`, pre-existing, unrelated)
- Coverage: not measured in this environment
- Determinism: PASS — `init.py` double-run byte-identical, 0 unresolved-token warnings
- A11y / Perf: N/A (no UI surface)

## Section 6: Code Review

| Severity | Count | All Resolved? |
| -------- | ----- | ------------- |
| CRITICAL | 0 | — |
| WARNING | 2 | ✅ (both fixed in-sprint: agent-wrapper refs + contradicting test) |
| SUGGESTION | 3 | Deferred (see §9) |

## Section 7: Retrospective

**What went well**
- Forecast calibration was excellent (100% on assumptions + complexity).
- The mandated A → C → B ordering held; B's blast radius was contained behind the literal audit.
- @reviewer caught a genuine Goal gap (agent-wrapper refs) that the task list under-specified — review added real value.

**What didn't go well**
- TG2's task list said "update sprint-lead, planner, security, docs cross-references" but the broader Goal required all 13 agent wrappers too — the narrow task wording let the gap slip until review.
- The escape mechanism needed a redesign mid-TG3 because the v1 approach collided with the unresolved-token scans.

**Surprises & Lessons**
- An escape that is byte-identical to the thing being detected cannot be stripped before detection runs — separate "preserve marker" from "render literal" into two phases ordered around the scans.

**Start / Stop / Continue**
- **Start:** When a task rewrites references "across skills," explicitly enumerate *all* artifact families (skill sources AND agent wrappers) in the task list.
- **Stop:** Treating an inline-escape as a single-pass transform when scans run between substitution and final render.
- **Continue:** Seeding the RETRO forecast at promotion — it made calibration measurement trivial.

**Action Items**

| Action Item | Target |
| ----------- | ------ |
| Decide whether `SPRINTS.md` and `BACKLOG_LEDGER.md` should hold real repo history or stay as template demo content | ITEM-010 (open, unscheduled) |
| Consider a CI check asserting all docs use `config/project.config.example.yml` for the canonical build command | ITEM-011 (open, unscheduled) |

Scheduling is `@planner`'s call at composition — these are logged to the backlog ledger as `open` with no sprint assignment, not pre-allocated to a sprint.

## Section 8: Commits

| Hash | Message |
| ---- | ------- |
| `e4d0272` | feat: Sprint 1 — resolve and deploy skill companion files (TG1) |
| `8a33211` | feat: Sprint 1 — resolve inline code-span tokens with escape for literals (TG3) |
| `b0f0057` | fix: Sprint 1 — agent wrappers reference skills at deploy path (BUG-005 #3) |
| `2194596` | test: Sprint 1 — lock strip-after-scan ordering (review SUGGESTION #1) |

TG2 (the `paths.skills_deploy_dir` token + skill-source cross-reference rewrites) was not committed as a standalone commit — it landed folded into the TG1/TG3 commits; the agent-wrapper portion of the cross-reference work was completed and committed separately as `b0f0057` after code review. The `docs: Sprint 1 — complete` close-out commit (this RETRO, ledger, @docs sync, version bumps) follows.

## Section 9: Carry-Over

No functional work carried over — all three task groups and both review warnings completed in-sprint.

Deferred review SUGGESTIONs (non-blocking, first logged Sprint 1):
- SUGGESTION #1 — ✅ DONE in-sprint. Added `test_strip_must_run_after_scan` (ordering-contract unit test proving strip-before-scan would false-flag) and `test_resolved_onboarding_escape_is_clean_literal` (full-build evidence that the deployed onboarding SKILL.md ships a clean `{{tokens}}` literal with no leaked backslash).
- SUGGESTION #2 — `SOURCE_STYLE_REFS` in `tests/test_init.py` is a hardcoded 7-item allowlist; consider deriving it. Logged to backlog ledger as **ITEM-009** (open, unscheduled).
- SUGGESTION #3 — confirm commit messages follow Conventional Commits (verified: `e4d0272`, `8a33211`, `b0f0057` all use `feat:`/`fix:` prefixes). No follow-up needed.

## Section 10: Sprint Trends

No prior sprint with a RETRO.md — trend table begins next sprint. Baseline metrics for Sprint 1:

| Metric | Sprint 1 |
| ------ | -------- |
| Sprint type | fix |
| Tasks planned / completed | 3 / 3 |
| Completion rate | 100% |
| Fix iterations | 1 |
| Gate first-pass rate | TG1/TG2 first-pass; TG3 second-pass |
| Review CRITICALs | 0 |
| Review WARNINGs (resolved) | 2 / 2 |
| Carry-over items | 0 |
| Forecast calibration | 100% |
| Test count | 401 passed / 7 skipped |

## Section 11: Owner Notes
_Reserved for project owner — no agent writes here._

<!-- /ACTUALS -->
