# Sprint 2 Retrospective — Build-System Hardening & Process Hygiene

<!-- FORECAST — seeded by @sprint-lead at promotion -->

## Sprint Forecast

### Sprint Type

`mixed` (bug-fix / debt)

### Per-Task Complexity Forecast

| Task | Expected Complexity | Reasoning |
| ---- | ------------------- | --------- |
| TG1 – deploy-copy + fail-on-unresolved | moderate | Additive loop in `init.py` + config expansion + new test. Behaviour change (exit-code) keeps blast radius contained to build invocations. |
| TG2 – token-free guardrail | straightforward | Script + CI step building directly on TG1's deploy-copy output. Low risk once TG1 is stable. |
| TG3 – CI canonical-build-command check | straightforward | Script reads docs, checks a path string. No logic change in `init.py`. |
| TG4 – derive `SOURCE_STYLE_REFS` | straightforward | Mechanical replacement of hardcoded list with a derivation in one test file. |
| TG5 – Claude Code `/command` seeding + onboarding docs | moderate | Touches `init.py` output path, onboarding skill, and config token. New output directory to manage. |
| TG6 – planner-mode checkpoint enforcement | moderate | Behaviour change in planner agent body + skill — needs precise language so the gate is load-bearing, not advisory. |
| TG7 – purge demo/template content | straightforward | Surgical deletion + count recomputation across 3 files. One-way purge confirmed safe by pre-flight grep. |

### Risk Areas

1. **TG1 fail-on-unresolved exit-code change** — adopters with incomplete configs will now get a hard failure. Error message must be clear and actionable; a confusing message would surface as a regression for new adopters.
2. **TG5 `.claude/commands/` seeding** — new output directory; must be deterministic and must not overwrite files on re-run if they are already correct.
3. **TG7 purge** — one-way data change. Pre-flight confirmed no draft cross-references; execute atomically.

### Assumptions

- Sprint 1 BUG-005 resolution (companion files, inline code-span, cross-refs) is the stable foundation.
- Existing 401+ test suite is green at sprint start.
- No adopter currently depends on the exit-0 behaviour when config keys are missing (treating as a bug).
- TG7 purge is safe (no in-flight drafts reference demo items — confirmed by pre-flight grep 2026-05-30).

### Expected Gate Outcomes

| Gate | Outcome | Reasoning |
| ---- | ------- | --------- |
| standard (pytest) | PASS | New tests added per task group; existing suite unaffected by changes. |
| Determinism | PASS | Changes are additive; double-run equality is the explicit check. |
| guardrail | PASS | TG2 guardrail passes when TG1 deploy-copy is correct. |

### Scope Estimate

- Files: `init.py`, `config/project.config.yml` + profiles, `scripts/`, `tests/test_init.py`, `skills/onboarding/onboarding.skill.md`, `agents/planner.body.md`, `skills/planner/*`, `SPRINTS.md`, `docs/planning/BACKLOG_LEDGER.md`, `docs/planning/BUG_BACKLOG.md`
- Estimated lines changed: ~200–350
- Subagents: 6 implementation subagents (TG1 → TG2 → TG3; TG4/TG5/TG6/TG7 parallel)

### Watch Items

- TG1 → TG2 sequencing is load-bearing: the guardrail (TG2) checks the deploy output that TG1 creates.
- TG7 purge should be atomic — delete all demo rows and recompute counts in one commit.
- TG6 checkpoint language must be specific enough that the planner agent cannot accidentally skip it.

<!-- /FORECAST -->

<!-- ACTUALS — completed by @docs 2026-05-31 -->

## Section 0: Forecast vs. Actual

**Previous Action Items: Status** (from Sprint 1 §7)

| Action Item | Target | Status |
| ----------- | ------ | ------ |
| Decide whether `SPRINTS.md` and `BACKLOG_LEDGER.md` should hold real repo history or stay as template demo content | ITEM-010 | ✅ Done — TG7 purged all demo/template rows from both files |
| Consider a CI check asserting all docs use `config/project.config.example.yml` for the canonical build command | ITEM-011 | ✅ Done — TG3 delivered `scripts/check_build_command.py` + CI step |

**Complexity Comparison**

| Task | Forecast | Actual | Δ | Accurate? |
| ---- | -------- | ------ | - | --------- |
| TG1 – deploy-copy + fail-on-unresolved | moderate | moderate | 0 | ✅ |
| TG2 – token-free guardrail | straightforward | straightforward | 0 | ✅ |
| TG3 – CI canonical-build-command check | straightforward | straightforward | 0 | ✅ |
| TG4 – derive `SOURCE_STYLE_REFS` | straightforward | straightforward | 0 | ✅ |
| TG5 – Claude Code /command seeding + onboarding docs | moderate | moderate | 0 | ✅ |
| TG6 – planner-mode checkpoint enforcement | moderate | moderate | 0 | ✅ |
| TG7 – purge demo/template content | straightforward | straightforward | 0 | ✅ |

**Assumptions Check**

| Assumption | Held? | Notes |
| ---------- | ----- | ----- |
| Sprint 1 BUG-005 resolution is stable foundation | ✅ | No regressions observed; companion-file and escape logic undisturbed. |
| Existing 401+ test suite green at sprint start | ✅ | 401 passed at start; 431 at completion (+30). |
| No adopter depends on exit-0 when config keys are missing | ✅ | No reports; change treated as bug fix per intent. |
| TG7 purge safe (no in-flight drafts reference demo items) | ✅ | Pre-flight grep confirmed clean before execution. |

**Risk Area Accuracy**

- **TG1 exit-code change** (predicted) — materialized as a *test* issue, not a user-facing one: `SecurityValidator.validate_path()` used `sys.exit(1)` on absolute paths, breaking `TestDeployCopy` tests that passed absolute paths directly. Fixed by switching to `Path.is_absolute()` and refactoring tests to use `monkeypatch.chdir` + relative paths. Correct prediction of risk area; wrong about which layer would surface it.
- **TG5 `.claude/commands/` seeding** (predicted) — required two fix passes (200-line cap exceeded, canonical config path wrong) but both were self-contained and resolved cleanly.
- **TG7 purge** (predicted) — executed atomically without issues; pre-flight validation paid off.
- **Missed risk:** `check_build_command.py` required three separate fix passes (backtick extraction, scan-scope too broad, `PULL_REQUEST_TEMPLATE` directory exclusion). Script edge cases are harder to anticipate than logic changes.

**Forecast Calibration Score**

- Assumptions accuracy: 4/4 (100%)
- Complexity accuracy: 7/7 (100%)
- Combined: **100%**

## Section 1: Sprint Summary

- Tasks planned / completed / blocked / partial: **7 / 7 / 0 / 0**
- Files created / modified: ~24 (see §3); new files: `scripts/check_tokens.py`, `scripts/check_build_command.py`, `tests/test_scripts.py`, `skills/onboarding/CLAUDE_CODE_SETUP.md`
- Sprint type: **mixed** (bug-fix / debt)

## Section 2: Execution Timeline

| Phase | Duration | Notes |
| ----- | -------- | ----- |
| Phase 1: Kickoff | — | Read PLAN.md + seeded RETRO forecast. |
| Phase 2: Implementation | — | TG1 → TG2 → TG3 sequential (load-bearing order); TG4/TG5/TG6/TG7 as parallel batch. 7 implementation subagents. |
| Phase 2.5: Safety-Net | N/A | `typecheck`/`lint` commands are empty no-ops; pytest is the QA gate. |
| Phase 3: Quality Gates | — | 5 QA iterations: `init.py` exit-0, pytest (431 pass), `check_tokens.py` exit-0, `check_build_command.py` exit-0, determinism double-run. |
| Phase 4: Code Review | — | @security (1 run, 0 CRITICAL, 2 WARNINGs fixed); @reviewer (1 run + 1 fix pass: 0 CRITICAL remaining, 0 WARNING remaining, 3 SUGGESTIONs resolved). |
| Phase 5: Documentation | — | @docs sync: `docs/CONTRIBUTING.md`, `docs/ONBOARDING.md`, `README.md` build-command updates. |
| Phase 6: Retrospective | — | Ledger update + RETRO. |

(Wall-clock durations not instrumented in this environment.)

## Section 3: Complexity Profile

| Task | Complexity | Lines +/- | Files | Fix Iterations | Duration |
| ---- | ---------- | --------- | ----- | -------------- | -------- |
| TG1 deploy-copy + fail-on-unresolved | moderate | — | `init.py`, `config/project.config.yml`, `config/project.config.example.yml`, `tests/test_init.py` | 3 (ALLOWED_COMMANDS gap, absolute-path guard test clash, UNC blind spot) | — |
| TG2 token-free guardrail | straightforward | — | `scripts/check_tokens.py`, `.github/workflows/ci.yml` | 1 (regex tightened to require namespace.key dot pattern) | — |
| TG3 CI canonical-build-command check | straightforward | — | `scripts/check_build_command.py`, `ci.yml` | 3 (backtick strip, scan-scope narrowed, PULL_REQUEST_TEMPLATE exclusion) | — |
| TG4 derive `SOURCE_STYLE_REFS` | straightforward | — | `tests/test_init.py` | 0 | — |
| TG5 Claude Code /command seeding + onboarding | moderate | — | `init.py`, `skills/onboarding/onboarding.skill.md`, `skills/onboarding/CLAUDE_CODE_SETUP.md`, `config/project.config.yml`, `profiles/*.yml` | 2 (200-line cap, canonical config path) | — |
| TG6 planner-mode checkpoint | moderate | — | `agents/planner.body.md`, `skills/planner/planner.skill.md` | 0 | — |
| TG7 purge demo/template content | straightforward | — | `SPRINTS.md`, `docs/planning/BACKLOG_LEDGER.md`, `docs/planning/BUG_BACKLOG.md` | 0 | — |

Totals: ~24 files modified or created; lines changed not instrumented.  
Complexity distribution: 2 moderate, 4 straightforward (+ 1 moderate-equivalent fix batch).

## Section 4: Process Health

- Subagent counts: 7 implementation (TG1–TG7) + 5 fix-pass subagents + @qa (×5 runs) + @security (×1) + @reviewer (×1 + 1 fix pass) + @docs (×1).
- Gate reruns: @qa ran 5 times; each fix pass required a full re-run.
- Blocked/partial tasks: none.
- Fix loop detail:

  | Fix # | Trigger | Root Cause | Files |
  | ----- | ------- | ---------- | ----- |
  | 1 | TG5: onboarding.skill.md exceeded 200-line cap (234 lines) | Claude Code setup section included inline; file-size cap violated | `skills/onboarding/onboarding.skill.md` → split to `CLAUDE_CODE_SETUP.md` companion |
  | 2 | `check_tokens.py` false-positive on `{{tokens}}` docs literal | Regex matched bare `{{word}}` without namespace.key dot pattern | `scripts/check_tokens.py` |
  | 3 | `check_build_command.py` extraction included trailing backtick | Regex pattern not stripping backtick from extracted string | `scripts/check_build_command.py` |
  | 4 | `check_build_command.py` scan scope too broad | Scanned `docs/` and `README` in addition to authoritative sources | `scripts/check_build_command.py` |
  | 5 | TG5: canonical config path wrong in onboarding source | Referenced wrong config file path | `skills/onboarding/onboarding.skill.md` |
  | 6 | Security tool commands not in `ALLOWED_COMMANDS` | `syft`, `trivy`, `checkov`, `gitleaks`, `bandit`, `semgrep`, `grype` absent from allowlist | `init.py` |
  | 7 | `TestDeployCopy` tests broke with absolute-path guard | Tests passed absolute paths directly; `sys.exit(1)` path guard fired | `tests/test_init.py` (monkeypatch.chdir + relative paths) |
  | 8 | `SecurityValidator.validate_path()` UNC blind spot | `startswith('..')` + Windows-absolute check missed `\\server\share` UNC paths | `init.py` (replaced with `Path.is_absolute()`) |
  | 9 | `check_build_command.py` flagged `PULL_REQUEST_TEMPLATE` directory | Directory-form PR template path not excluded from scan | `scripts/check_build_command.py` |

- Gate first-pass rate: 0/7 TGs passed @qa without a fix iteration across the batch; all passed after the 5-pass fix sequence.

## Section 5: Quality Results

- TypeScript: N/A (Python project)
- Lint: N/A (`commands.lint` empty no-op)
- Unit Tests: **431 passed / 0 failed / 7 skipped** (+30 tests added this sprint; 1 pre-existing `jsonschema.RefResolver` deprecation warning, unresolved — see §9)
- Coverage: not measured in this environment
- `check_tokens.py`: exit 0 — no unresolved tokens in deployed `.github/` tree
- `check_build_command.py`: exit 0 — all authoritative sources reference correct canonical build command
- Determinism: PASS — `init.py` double-run byte-identical, 0 token warnings, 0 security warnings
- @security: 0 CRITICAL; 2 WARNINGs identified and fixed in-sprint (ALLOWED_COMMANDS gap, UNC path blind spot)
- A11y / Perf: N/A (no UI surface)

## Section 6: Code Review

From @reviewer final pass (after 1 in-sprint fix iteration):

| Severity | Count (initial) | All Resolved? |
| -------- | --------------- | ------------- |
| CRITICAL | 1 | ✅ fixed in-sprint |
| WARNING | present (all fixed) | ✅ 0 remaining after fix pass |
| SUGGESTION | 3 | ✅ all resolved in-sprint (planner body duplicate clause, PowerShell allowlist, onboarding companion test) |

## Section 7: Retrospective

**What went well**
- Both Sprint 1 action items (demo purge, CI build-command check) were delivered as first-class tasks — closing the loop on retrospective follow-ups.
- 100% forecast calibration for the second consecutive sprint; complexity estimates were accurate across all 7 TGs.
- TG1 → TG2 → TG3 sequencing held; the guardrail (TG2) validating TG1's deploy output worked exactly as planned.
- @reviewer SUGGESTIONs were all resolved in-sprint (planner body, PowerShell allowlist, onboarding companion test) — no deferred SUGGESTION carry-over.

**What didn't go well**
- Fix-pass count (9 issues, 5 passes) was much higher than Sprint 1's single fix. New scripts (`check_tokens.py`, `check_build_command.py`) introduced more edge-case surface area than implementation changes to `init.py`.
- `check_build_command.py` required 3 separate fix passes — regex scope, backtick extraction, and template exclusion — suggesting the script needed more careful upfront specification before implementation.
- Security ALLOWED_COMMANDS was incomplete at initial implementation; security tooling is a recurring blind spot when expanding `init.py` command validation.

**Surprises & Lessons**
- A path validation guard using `sys.exit(1)` will break any existing test that constructs absolute paths directly; test fixtures must be updated atomically with the guard.
- `str.startswith('..')` is not a reliable absolute-path detector on Windows — `Path.is_absolute()` is the correct check and should be the default.
- Documentation literals (e.g., `{{tokens}}`) in deployed skill files require token-detection regex to be scoped to `namespace.key` dot patterns, not bare `{{word}}`.

**Start / Stop / Continue**
- **Start:** When writing a new validation script, enumerate known edge cases (extraction backticks, template dirs, documentation literals) in the task spec before implementation.
- **Stop:** Using `sys.exit(1)` in validators without immediately updating test fixtures to avoid absolute-path collisions.
- **Continue:** Mandated TG sequencing when later tasks validate earlier tasks' output — it prevents ordering bugs.

**Action Items**

| Action Item | Target |
| ----------- | ------ |
| Address `jsonschema.RefResolver` deprecation warning (pre-existing, surfaced again; no immediate impact but will break on jsonschema ≥4.18 drop) | ITEM-013 (open, unscheduled) |

## Section 8: Commits

Git commits not captured in this session — commits were made by implementation and fix-pass subagents during sprint execution. Files changed during this sprint serve as the proxy record:

**Modified:** `init.py`, `config/project.config.yml`, `config/project.config.example.yml`, `profiles/react-web-app.config.yml`, `profiles/python-api.config.yml`, `profiles/monorepo-fullstack.config.yml`, `tests/test_init.py`, `.github/workflows/ci.yml`, `skills/onboarding/onboarding.skill.md`, `agents/planner.body.md`, `skills/planner/planner.skill.md`, `resolved/skills/onboarding/SKILL.md`, `.github/agents/onboarding/SKILL.md`, `.github/agents/perf/SKILL.md`, `SPRINTS.md`, `docs/planning/BACKLOG_LEDGER.md`, `docs/planning/BUG_BACKLOG.md`, `docs/CONTRIBUTING.md`, `docs/ONBOARDING.md`, `README.md`

**Created:** `scripts/check_tokens.py`, `scripts/check_build_command.py`, `tests/test_scripts.py`, `skills/onboarding/CLAUDE_CODE_SETUP.md`

## Section 9: Carry-Over

No functional work carried over — all 7 task groups completed in-sprint.

One advisory item deferred (SUGGESTION level, not a functional defect):

- **`jsonschema.RefResolver` deprecation** — flagged by both @security and @reviewer. Pre-existing warning present since Sprint 1; the deprecation will become a hard failure when `jsonschema ≥ 4.18` drops `RefResolver`. No immediate impact on current test runs (431 pass). Logged as **ITEM-013** (debt, open, unscheduled). First logged: Sprint 2. Unblock condition: pin `jsonschema` version and migrate to `jsonschema.validators` API.

## Section 10: Sprint Trends

| Metric | Sprint 1 | Sprint 2 | Signal |
| ------ | -------- | -------- | ------ |
| Sprint type | fix | mixed | — |
| Tasks planned | 3 | 7 | — |
| Tasks completed | 3 | 7 | — |
| Completion rate | 100% | 100% | ● |
| Total duration | — | — | — |
| Files changed | ~25 | ~24 | ● |
| Fix iterations | 1 | 9 | ▼ |
| Gate reruns (@qa) | 2 | 5 | ▼ |
| Gate first-pass rate | TG1/TG2 ✅; TG3 2nd pass | All TGs post-fix (5 passes) | ▼ |
| Review CRITICALs | 0 | 0 (1 fixed in-sprint) | ● |
| Review WARNINGs resolved | 2 / 2 | all / all | ● |
| Carry-over items | 0 | 0 (1 deferred SUGGESTION → ITEM-013) | ● |
| Forecast calibration | 100% | 100% | ● |
| Test count delta | +8 (393 → 401) | +30 (401 → 431) | ▲ |
| New test files | 0 | 2 (`test_scripts.py` + companion test) | ▲ |

**Drift Analysis**

- **Fix iterations and gate reruns increased sharply (1→9 fixes, 2→5 @qa runs).** This is partly scope-driven (7 TGs vs 3) but also reflects that new validation scripts are harder to get right first-pass than `init.py` logic changes. Edge-case surface area for regex-based scripts is an ongoing concern.
- **Completion rate and forecast calibration held at 100%** for the second consecutive sprint — the estimation model is performing well even as task count scaled up.
- **Test count growth accelerated (+30 vs +8)** — the two new test files (`test_scripts.py`, onboarding companion) account for most of the delta; healthy growth aligned with new script surface area.
- **Review CRITICAL count: 0 remaining in both sprints.** One CRITICAL was found and fixed in-sprint in Sprint 2; the gate is functioning as intended.
- **No functional carry-over for the second consecutive sprint.** Single deferred item (ITEM-013) is a SUGGESTION-level deprecation with no near-term risk. ● stable.

## Section 11: Owner Notes
_Reserved for project owner — no agent writes here._

<!-- /ACTUALS -->
