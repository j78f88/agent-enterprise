# Sprint 5 Retrospective — Mode 2 Dispatcher Promotion

<!-- FORECAST — seeded by @sprint-lead at promotion 2026-06-10 -->

## Sprint Forecast

### Sprint Type

`feature` (mode promotion per ADR 0008)

### Per-Task Complexity Forecast

| Task | Expected Complexity | Reasoning |
| ---- | ------------------- | --------- |
| TG1 – core port | moderate | Copy + adaptation of a 253-line reference impl; semantics must not drift (shared conformance pins it). |
| TG2 – callable discovery | moderate | Two discovery paths (sidecar + frontmatter) with schema validation; frontmatter parsing reused from init.py. |
| TG3 – durable queue + returns | complex | Crash-resume is the sprint's highest-complexity new code: journal reconciliation, atomic replace, in-flight requeue semantics. |
| TG4 – root CLI | straightforward | argparse mirror of init.py conventions; containment posture borrowed from the deploy guard. |
| TG5 – dispatcher tests | moderate | Crash-simulation fixtures (partial state/journal) need care; rest is direct. |
| TG6 – shared conformance + byte-freeze | straightforward | Parametrize an existing hook over two impls; hash assertion. |
| TG7 – docs + install contract | straightforward | Documentation of what TG1-6 prove; contract text stays frozen. |

### Risk Areas

1. **TG3 crash-resume** — journal/state reconciliation bugs are subtle; partial-failure tests must simulate torn writes and orphaned in-flight items.
2. **Port drift from contract semantics** — mitigated by running the identical `mode-2-contract-v1` checklist against both impls in one parametrized test.
3. **Windows atomicity/paths** — `os.replace` + explicit UTF-8 everywhere; both CI OSes gate per ADR 0008 criterion 2.
4. **Scope temptation** to improve the frozen contract — zero schema/contract diffs is a checklist item; breaking needs escalate per ADR 0003.

### Assumptions

- Suite green at 533 at sprint start; main fully merged (Sprints 3+4 + PRs #2/#4).
- `SubagentReturnValidator` is stable and reusable without Mode 1 build artifacts at runtime.
- The reference impl correctly encodes contract semantics (it is the porting source AND the conformance co-subject).

### Expected Gate Outcomes

| Gate | Outcome | Reasoning |
| ---- | ------- | --------- |
| standard (pytest) | PASS after fix loops | New runtime package; expect first-pass failures in TG3/TG5 crash paths. |
| Determinism | PASS | Sprint doesn't touch the build path; discovery is sorted. |
| guardrail | PASS | No new tokens or deployed-tree changes. |
| conformance (both impls) | PASS | The port is adaptation, not redesign. |
| CI (PR branch) | PASS | Windows risk budgeted; fix-before-close contract. |

### Scope Estimate

- Files: `src/mode2_dispatcher/` (5 new), `dispatch.py` (new), `tests/test_mode2_dispatcher.py` (new), `tests/test_protocol_v1_conformance.py`, `docs/ORCHESTRATION.md` (new), install-contract, README, CHANGELOG
- Estimated lines: ~700–1000 (runtime + tests)
- Subagents: 3 batches — TG1-4 (package+CLI) → TG5+TG6 (tests) ∥ TG7 (docs)

### Watch Items

- Subagents edit only; sprint lead commits per batch with explicit pathspecs (Sprint 3/4 lesson).
- Cross-check subagent self-reports against `git status` (Sprint 3 lesson).
- Crash-resume tests are the "stale state" dimension for this sprint (Sprint 4 lesson).
- Reference impl byte-freeze asserted by test, not by promise.

<!-- /FORECAST -->

<!-- ACTUALS — completed by @sprint-lead 2026-06-10 -->

## Section 0: Forecast vs. Actual

**Previous Action Items: Status** (from Sprint 4 §6)

| Action Item | Target | Status |
| ----------- | ------ | ------ |
| Onboarding/guardrail decoupling | ITEM-023 | ⏸ Open — not in scope |
| ADR 0008 wording disambiguation | ITEM-022 | ⏸ Open — carried again; schedule or kill next planning pass |

**Complexity Comparison**

| Task | Forecast | Actual | Accurate? |
| ---- | -------- | ------ | --------- |
| TG1 core port | moderate | moderate | ✅ |
| TG2 discovery | moderate | moderate | ✅ |
| TG3 queue + returns | complex | complex (torn-tail bug caught during the implementer's own crash simulation) | ✅ |
| TG4 CLI | straightforward | straightforward | ✅ |
| TG5 tests | moderate | moderate (60 tests; 5 implementation findings reported, not fixed) | ✅ |
| TG6 conformance | straightforward | straightforward | ✅ |
| TG7 docs | straightforward | straightforward — but both review BLOCKERs were doc defects | ⚠️ |

**Assumptions Check** — all three held (suite 533 green at start, validator reuse clean, reference impl semantics sound). One refinement: the tier-3 summary schema turned out to be the planner-composition shape — the reference impl's summary fails it identically, so the contract checklist (not the schema) is the binding assertion; recorded in a test comment.

**Forecast Calibration Score** — Assumptions 3/3, Complexity 7/7 (one ⚠️ on where TG7's risk landed): **100%**.

## Section 1: Sprint Summary

- Tasks planned / completed / blocked / partial: **7 / 7 / 0 / 0**
- New: `src/mode2_dispatcher/` (5 modules), `dispatch.py`, `tests/test_mode2_dispatcher.py` (60 tests), `docs/ORCHESTRATION.md`; conformance now parametrized over both impls with a byte-freeze pin.
- Sprint type: **feature** (mode promotion per ADR 0008)

## Section 2: Execution Timeline

| Phase | Notes |
| ----- | ----- |
| 1 Kickoff | Promotion + forecast seeding; retro lessons in execution guidelines. |
| 2 Implementation | Batch 1: TG1-4 (one subagent, package+CLI). Batch 2: TG5+TG6 ∥ TG7. 3 subagents total. |
| 2.5/3 Gates | @qa ×1 — all gates first-run PASS incl. Mode 2 independence spot-check (no skills/, no init.py). |
| 4 Review | @reviewer ×1 — REQUEST-CHANGES: 2 doc BLOCKERs + 7 SUGGESTIONs; blockers + S1 fixed in-sprint, rest triaged to ledger/accept. |
| 5 Docs | CHANGELOG landed with TG7. |
| 6 Retro | This file; ledger ITEM-024/025/026 seeded; archive rule applied (Sprint 3 → docs/archive/sprint-history.md). |

## Section 3: Fix Loops

| Fix # | Trigger | Root Cause | Resolution |
| ----- | ------- | ---------- | ---------- |
| 1 | Review B1/B2 + S1 | Doc example missing schema-required fields; doc overclaimed recovery surface; read-only load mkdir'd the queue root | Example completed (verified against the validator); recovery claim corrected; mkdir gated on recover; requeue hint for crash-interrupted items; 1 test assertion updated |

## Section 4: Quality Results

- Unit tests: **600 passed / 0 failed / 11 skipped** (+67 this sprint); green with `-W error::DeprecationWarning`.
- Conformance: mode-2-contract-v1 checklist passes parametrized over reference + supported impls; reference impl byte-frozen (sha256 pinned by test).
- Independence: dispatcher runs in a bare temp project (no Mode 1 artifacts) — proven by e2e test and manual QA probe.
- Determinism: init.py double-build identical; discovery output byte-identical across runs.

## Section 5: Code Review

| Severity | Count | Resolution |
| -------- | ----- | ---------- |
| BLOCKER | 2 | ✅ both fixed in-sprint (doc example invalid against own validator; recovery claim false) |
| SUGGESTION | 7 + 5 test-author findings | S1 fixed in-sprint; a→ITEM-024, S3/S4/d/e→ITEM-025, S5/S6→ITEM-026; b/c/S2/S7 accepted with rationale |

## Section 6: Retrospective

**What went well**
- The implementer's own crash simulation caught a real torn-tail bug before tests existed — building the smoke check into the implementation task pays.
- Review probing again found what tests missed — but this sprint both blockers were docs, not code: the code survived every empirical attack (ghost-done, containment, journal divergence).
- Test author reported implementation findings instead of silently fixing them — the report/triage split kept ownership clean and produced three well-scoped ledger items.
- First-run QA gates for the second consecutive sprint.

**What didn't go well**
- Both blockers were documentation that contradicted the implementation — docs were written from the implementer's report rather than re-verified against behaviour. The docs subagent did cross-check --help output but not the example against the validator.
- ITEM-022 has now been carried twice without being scheduled.

**Start / Stop / Continue**
- **Start:** docs subagents must execute every copy-pasteable example through the relevant validator/CLI before returning.
- **Stop:** carrying ITEM-022 silently — schedule it into the next sprint or kill it explicitly.
- **Continue:** implementer-run smoke checks; report-not-fix for test-author findings; empirical review probing.

**Action Items**

| Action Item | Target |
| ----------- | ------ |
| Doc examples executed against validators before return (process rule, encode in docs-subagent prompts) | sprint-lead practice |
| Schedule or kill ITEM-022 | next planning pass |

## Section 7: Carry-Over

No functional carry-over. Ledger: ITEM-024 (frozen-contract example erratum), ITEM-025 (CLI hardening bundle), ITEM-026 (journal robustness bundle); ITEM-022/023 still open from prior sprints.

## Section 8: Sprint Trends

| Metric | Sprint 3 | Sprint 4 | Sprint 5 | Signal |
| ------ | -------- | -------- | -------- | ------ |
| Tasks planned / completed | 6 / 6 | 7 / 7 | 7 / 7 | ● |
| Fix passes (findings) | 1 (review) | 3 (12) | 1 (3 fixed, 8 triaged) | ▲ |
| Review BLOCKERs | 1 | 1 | 2 (both docs) | ● |
| Test count delta | 0 | +102 | +67 | ● |
| Forecast calibration | not seeded | 100% | 100% | ● |

**Drift Analysis** — blocker class shifted from code (Sprints 3-4) to docs: the implementation pipeline (smoke-check + report/triage + shared conformance) is maturing faster than the docs pipeline. The new process rule (execute examples) targets exactly that. Open-ledger debt is growing (022-026, five open items) — the next planning pass should compose a small hardening sprint or fold items into Mode 3.

## Section 9: Owner Notes
_Reserved for project owner — no agent writes here._

<!-- /ACTUALS -->
