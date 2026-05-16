---
applyTo: "docs/sprints/best-practice-alignment/**"
---

# Best-Practice Alignment — Run Sheet

Execution instruction for the best-practice-alignment work packages. Work one step at a time. After each step: verify, report results, and **stop for owner approval** before continuing.

> **Scope note:** This instruction auto-attaches only inside `docs/sprints/best-practice-alignment/`. When working on the files it touches (init.py, skills, references, etc.), open this run sheet explicitly so the assistant sees the verification commands and approval gates.

> **Rule:** Do NOT proceed to the next step without explicit owner approval.
> **Rule:** Do NOT delete any files in `docs/sprints/best-practice-alignment/`. Cleanup is manual-only by the owner.
> **Rule:** Before **re-running** a step that previously failed mid-way, clear stale build output: `Remove-Item -Recurse -Force resolved/*`. init.py will rebuild it. Do not do this on a first attempt — only on retry.
> **Rule:** Each verify block sets `$ErrorActionPreference = 'Stop'` and checks `$LASTEXITCODE` after every `python …` call. Do not strip these.

---

## Step 0: Pre-flight

**Status:** `pending`

Establish baseline before any changes.

```powershell
$env:PYTHONIOENCODING='utf-8'
python -m pytest tests/ -v
python init.py --config config/project.config.example.yml
```

**Expected:** ≥120 passed, ~14 skipped, 0 failed | ≥27 resolved, ≥10 copied, 13 agents, exactly 2 expected token warnings (`{{tokens}}` in onboarding, `{{ secrets.* }}` in security). Record the exact numbers here as the locked baseline for this sprint:
- tests passed: _____
- tests skipped: _____
- resolved files: _____
- copied files: _____

**On complete:** Report baseline numbers. Ask owner to approve Step 1.

---

## Step 1: Scaffolding

**Status:** `pending`

**Work package:** `docs/sprints/best-practice-alignment/01-scaffolding.md`

> **Note:** Task 1.7 appends a skill template to `docs/EXTENSION_GUIDE.md` that documents Common Rationalizations / Red Flags / Verification sections. These sections do not exist on any skill until Step 2 lands them. The template is forward-looking by design — do not flag this as drift.

Execute task groups 1.1, 1.2, 1.3, 1.6, 1.7 from that file.

**Creates:**
- `AGENTS.md` (repo root)
- `CLAUDE.md` (repo root)
- `instructions/generic/honesty-contract.instructions.md`
- `references/testing-patterns.md`
- `references/security-checklist.md`
- `references/accessibility-checklist.md`
- `references/performance-checklist.md`

**Edits:**
- `docs/EXTENSION_GUIDE.md` — appends "Skill Template" section (task 1.7)
- `skills/qa/qa.skill.md` — adds reference line to `references/testing-patterns.md` (task 1.6)
- `skills/security/security.skill.md` — adds reference line to `references/security-checklist.md` (task 1.6)
- `skills/a11y/a11y.skill.md` — adds reference line to `references/accessibility-checklist.md` (task 1.6)
- `skills/perf/perf.skill.md` — adds reference line to `references/performance-checklist.md` (task 1.6)

**Verify:**
```powershell
$ErrorActionPreference = 'Stop'

python init.py --config config/project.config.example.yml
if ($LASTEXITCODE -ne 0) { throw "init.py failed" }
python -m pytest tests/ -v
if ($LASTEXITCODE -ne 0) { throw "pytest failed" }

# Source files exist
Test-Path AGENTS.md                                                            # expect True
Test-Path CLAUDE.md                                                            # expect True
Test-Path instructions/generic/honesty-contract.instructions.md                # expect True
(Get-ChildItem references/*.md).Count                                          # expect 4

# Build pipeline emitted the new instruction (QA criterion #4)
Test-Path resolved/instructions/honesty-contract.instructions.md               # expect True

# Resolved instruction count grew by 1 (24 → 25, QA criterion #5)
(Get-ChildItem resolved/instructions/*.md).Count                               # expect ≥25

# At least 4 skills now reference the checklists (QA criterion #6, from task 1.6)
(Select-String -Path skills/*/*.skill.md -Pattern "references/").Count          # expect ≥4

# Audit trail
git log --oneline -1
```

**Commit:** `feat(docs): add AGENTS.md, CLAUDE.md, honesty contract, references, skill template`

**On complete:** Report verification results. Ask owner to approve Step 2.

> **⛔ APPROVAL GATE — Step 1 → Step 2.** Wait for explicit owner approval before proceeding. Do not start the next step's tasks, edits, or verification.

---

## Step 2: Skills Hardening

**Status:** `pending`

**Work package:** `docs/sprints/best-practice-alignment/02-skills.md`

Execute task group 1.4 (anti-rationalization) first, then 1.5 (red flags + verification). Order matters.

**Edits:** All 13 `skills/*/*.skill.md` files

**Verify:**
```powershell
$ErrorActionPreference = 'Stop'

# Ordering check: 1.4 must complete before 1.5 — confirm Common Rationalizations landed first
$rat = (Select-String -Path skills/*/*.skill.md -Pattern "## Common Rationalizations").Count
if ($rat -ne 13) { throw "Task 1.4 incomplete: expected 13 'Common Rationalizations' sections, got $rat" }

(Select-String -Path skills/*/*.skill.md -Pattern "## Red Flags").Count                # expect 13
(Select-String -Path skills/*/*.skill.md -Pattern "## Verification").Count             # expect 13

python init.py --config config/project.config.example.yml
if ($LASTEXITCODE -ne 0) { throw "init.py failed" }
python -m pytest tests/ -v
if ($LASTEXITCODE -ne 0) { throw "pytest failed" }

# Audit trail
git log --oneline -1
```

**Commit:** `feat(skills): add anti-rationalization, red flags, verification to all 13 skills`

**On complete:** Report grep counts and test results. Ask owner to approve Step 3.

> **⛔ APPROVAL GATE — Step 2 → Step 3.** Wait for explicit owner approval before proceeding. Do not start the next step's tasks, edits, or verification.

---

## Step 3: Format Upgrades

**Status:** `pending`

**Work package:** `docs/sprints/best-practice-alignment/03-formats.md`

Execute task groups 2.1 (handoff fields) then 2.2 (hash-chain).

**Edits:** `instructions/configurable/handoff-rejection-format.instructions.md`, `starters/FILE_HASHES.md`
**Creates:** `scripts/verify-hash-chain.py`, `tests/test_hash_chain.py`

**Verify:**
```powershell
$ErrorActionPreference = 'Stop'

python init.py --config config/project.config.example.yml
if ($LASTEXITCODE -ne 0) { throw "init.py failed" }

# Handoff format gained the Fix field (task 2.1)
$fix = Select-String -Path resolved/instructions/handoff-rejection-format.instructions.md -Pattern "Fix"
if (-not $fix) { throw "Handoff format missing 'Fix' field after init.py resolve" }

# Hash-chain script exists and validates
if (!(Test-Path scripts/verify-hash-chain.py)) { throw "scripts/verify-hash-chain.py missing" }
python scripts/verify-hash-chain.py starters/FILE_HASHES.md
if ($LASTEXITCODE -ne 0) { throw "hash-chain verification failed" }

python -m pytest tests/ -v
if ($LASTEXITCODE -ne 0) { throw "pytest failed" }

# Audit trail
git log --oneline -1
```

**Commit:** `feat(formats): structured handoff fields, hash-chain signing for FILE_HASHES`

**On complete:** Report verification results. Ask owner to approve Step 4.

> **⛔ APPROVAL GATE — Step 3 → Step 4.** Wait for explicit owner approval before proceeding. Do not start the next step's tasks, edits, or verification.

---

## Step 4: Multi-Platform

**Status:** `pending`

**Work package:** `docs/sprints/best-practice-alignment/04-platform.md`

Execute 3.1 (path-scoped frontmatter) before 3.2 (cursor emission). Then 3.3 and 3.4 in any order.

**Precondition gate before starting 3.2:** confirm 3.1 landed by checking resolved instructions carry a `scope:` field:
```powershell
Select-String -Path resolved/instructions/*.instructions.md -Pattern "^scope:" | Select-Object -First 1
# expect at least one match before proceeding to 3.2
```

**⚠️ Only step that modifies `init.py`. Write tests before changing production code.** Tests for 3.1 and 3.2 must exist and fail in the expected way *before* the init.py changes are written. The Step 4 verify block records the post-fix test count delta vs Step 0 baseline.

**Edits:** `init.py`, `config/project.config.example.yml`, `config/plugin.json`, `tests/test_init.py`
**Creates:** `prompts/` (5 files), `hooks/` (2 files)

**Verify:**
```powershell
$ErrorActionPreference = 'Stop'

# init.py changes — security validator must accept new targets
Select-String -Path init.py -Pattern "VALID_EDITOR_TARGETS" -Context 0,5 | Select-String -Pattern "cursor"  # expect match
Select-String -Path init.py -Pattern "VALID_EDITOR_TARGETS" -Context 0,5 | Select-String -Pattern "'all'"   # expect match

# New tests landed and pass — record delta vs Step 0 baseline
python -m pytest tests/ -v
if ($LASTEXITCODE -ne 0) { throw "pytest failed" }
# Expected: test count strictly greater than Step 0 baseline (new tests in test_init.py for 3.1 + 3.2)

# Build pipeline still green
python init.py --config config/project.config.example.yml
if ($LASTEXITCODE -ne 0) { throw "init.py failed" }

# Cursor emission worked
Test-Path .cursor/rules                    # expect True (created when target includes cursor)
(Get-ChildItem .cursor/rules/*.mdc -ErrorAction SilentlyContinue).Count  # expect > 0

# Prompt + hook deliverables
(Get-ChildItem prompts/*.prompt.md).Count  # expect 5
Get-ChildItem prompts/*.prompt.md | Select-Object -ExpandProperty Name  # expect: spec, plan, build, review, ship
Test-Path hooks/session-start.sh           # expect True

# Audit trail
git log --oneline -1
```

**Rollback:** If any check fails, `git reset --hard HEAD` to drop Step 4 changes and re-attempt. Do **not** partially commit.

**Commit:** `feat(init): path-scoped frontmatter, cursor emission, lifecycle commands, session hook`

**On complete:** Report test results including new tests. Ask owner to approve Step 5.

> **⛔ APPROVAL GATE — Step 4 → Step 5.** Wait for explicit owner approval before proceeding. Do not start the next step's tasks, edits, or verification.

---

## Step 5: Audit

**Status:** `pending`

**Work package:** `docs/sprints/best-practice-alignment/05-audit.md`

Execute task group 4.1. Read-only analysis of OPA Rego policies.

**Creates:** `docs/POLICY_AUDIT.md`

**Verify:**
```powershell
$ErrorActionPreference = 'Stop'

Test-Path docs/POLICY_AUDIT.md  # expect True

# Audit trail
git log --oneline -1
```

**Commit:** `docs(audit): OPA Rego policy catch-rate assessment`

**On complete:** Report audit findings and recommendation. Ask owner whether to run Step 5b (cleanup) before Step 6, or jump straight to Step 6.

> **⛔ APPROVAL GATE — Step 5 → Step 5b / Step 6.** Wait for explicit owner approval before proceeding. The owner chooses whether Step 5b runs before Step 6, after Step 6, or is deferred to a later PR.

---

## Step 5b: OPA Rego Cleanup (audit follow-through)

**Status:** `pending`
**Optional:** runs only if the owner approves the audit's "drop OPA layer" recommendation.

**Work package:** `docs/sprints/best-practice-alignment/05b-policy-cleanup.md`

Execute the three-commit cleanup on a **separate branch** (`chore/policy-cleanup`). Do not mix these commits into the sprint branch. The work package contains the full mechanical edit table, per-commit verify blocks, and stop-and-ask triggers.

**Creates:** `tools/sprint_lint.py`, `tests/test_sprint_lint.py`
**Deletes:** `policies/composition.rego`, `policies/security.rego`, `policies/` dir, `src/phase1_verification/policy_engine.py`, `docs/POLICIES.md`
**Edits:** `AGENTS.md`, `README.md`, `tests/README.md`, `docs/CONTRIBUTING.md`, `command centre/00-overview/architecture.md`, `command centre/00-overview/glossary.md`, `command centre/decisions/0004-shared-substrate-at-root.md`, `docs/DUAL_PLATFORM_PLAN.md`, `starters/FILE_HASHES.md`, `instructions/configurable/security-audit.instructions.md`, `src/phase1_verification/__init__.py`, `tests/test_contracts.py`

**Pre-flight (mandatory):**

```powershell
$ErrorActionPreference = 'Stop'

# Audit commit must be on main
git log --oneline -5
# Working tree must be clean of unrelated changes (do NOT git stash to hide them)
git status --short
# If anything unrelated is dirty, STOP and ask the owner.

git switch -c chore/policy-cleanup

# Record baseline test counts (used in commit 3 message)
python -m pytest tests/ 2>&1 | Select-Object -Last 5
```

**Per-commit verify:** see the work package. Each of the three commits has its own fail-fast block (`$ErrorActionPreference='Stop'` + `throw` on regression). Commit 3 includes a leak grep with the exact allow-list and a hash-chain re-validation (no re-signing required — `starters/FILE_HASHES.md` has no chained data rows yet).

**Approval gate inside the step:**

> **⛔ STOP after commit 2 verify.** Confirm the `PolicyEngine` leak grep returned zero unexpected hits before proceeding to commit 3. If anything surfaced, do not proceed — ask the owner.

**Test-count delta is expected.** Removing `TestPolicyEngine` reduces the skipped count. Record both the pre-cleanup and post-cleanup `X passed, Y skipped` lines in the commit 3 message. If `docs/sprints/best-practice-alignment/QA.md` hard-codes a criterion-9 baseline, update it in the same commit.

**On complete:** Report the three commit SHAs, pre/post pytest numbers, and confirmation that the leak grep is clean. Open PR titled `chore: remove unused OPA Rego layer` linking `docs/POLICY_AUDIT.md`.

> **⛔ APPROVAL GATE — Step 5b → Step 6.** Wait for explicit owner approval before proceeding. If Step 5b ran, Step 6's criterion 9 baseline may need updating to match the post-cleanup pytest numbers.

---

## Step 6: Final QA

**Status:** `pending`

**Checklist:** `docs/sprints/best-practice-alignment/QA.md`

Run full verification against all 10 success criteria from `QA.md`.

```powershell
$ErrorActionPreference = 'Stop'

python -m pytest tests/ -v
if ($LASTEXITCODE -ne 0) { throw "pytest failed" }
python init.py --config config/project.config.example.yml
if ($LASTEXITCODE -ne 0) { throw "init.py failed" }

# Criterion 1: AGENTS.md + CLAUDE.md exist
Test-Path AGENTS.md ; Test-Path CLAUDE.md
# Criterion 2: 13 skills have Common Rationalizations
(Select-String -Path skills/*/*.skill.md -Pattern "## Common Rationalizations").Count   # 13
# Criterion 3: 13 skills have Red Flags + Verification
(Select-String -Path skills/*/*.skill.md -Pattern "## Red Flags").Count                  # 13
(Select-String -Path skills/*/*.skill.md -Pattern "## Verification").Count               # 13
# Criterion 4: honesty contract deployed to resolved/
Test-Path resolved/instructions/honesty-contract.instructions.md                         # True
# Criterion 5: resolved instructions ≥ 25
(Get-ChildItem resolved/instructions/*.md).Count                                          # ≥25
# Criterion 6: references/ has 4 checklists, ≥4 skills reference them
(Get-ChildItem references/*.md).Count                                                     # 4
(Select-String -Path skills/*/*.skill.md -Pattern "references/").Count                    # ≥4
# Criterion 7: handoff rejection format has Fix + Link fields
Select-String -Path resolved/instructions/handoff-rejection-format.instructions.md -Pattern "Fix"
Select-String -Path resolved/instructions/handoff-rejection-format.instructions.md -Pattern "Link"
# Criterion 8: hash-chain script validates FILE_HASHES.md
python scripts/verify-hash-chain.py starters/FILE_HASHES.md ; $LASTEXITCODE  # expect 0
# Criterion 9: test suite green, count ≥ Step 0 baseline (record exact delta)
# Criterion 10: no new unresolved {{tokens}} beyond the 2 expected — eyeball init.py warnings
```

Report pass/fail for each criterion. Include the recorded Step 0 baseline numbers for criterion 9 comparison.

**On complete:** Report full QA results. Notify owner that cleanup is ready.

> **⛔ Cleanup is manual-only.** Do NOT delete `docs/sprints/best-practice-alignment/`. The owner will do this when ready.
