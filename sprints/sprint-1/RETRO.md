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
_To be completed by @sprint-lead_

## Section 1: Sprint Summary
_To be completed by @sprint-lead_

## Section 2: Execution Timeline
_To be completed by @sprint-lead_

## Section 3: Complexity Profile
_To be completed by @sprint-lead_

## Section 4: Process Health
_To be completed by @sprint-lead_

## Section 5: Quality Results
_To be completed by @sprint-lead_

## Section 6: Code Review
_To be completed by @sprint-lead_

## Section 7: Retrospective
_To be completed by @sprint-lead_

## Section 8: Commits
_To be completed by @sprint-lead_

## Section 9: Carry-Over
_To be completed by @sprint-lead_

## Section 10: Sprint Trends
_To be completed by @sprint-lead_

## Section 11: Owner Notes
_Reserved for project owner — no agent writes here._

<!-- /ACTUALS -->
