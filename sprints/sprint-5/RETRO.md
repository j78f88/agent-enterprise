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
