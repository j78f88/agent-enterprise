# Run-Sheet Revisions — Apply Spec

Mechanical edit spec for `run-sheet.instructions.md`. Each item lists the section, the **current** text, and the **replacement** text. Apply verbatim. No interpretation.

Severity: **E** = error/correctness, **O** = omission/robustness, **I** = improvement/polish.

When all E and O items are applied, delete this file (manual cleanup, owner only).

---

## E1 — Step 1 "Creates" list omits skill edits from task 1.6

**Section:** Step 1: Scaffolding, the `**Creates:**` block.

**Why:** Task 1.6 in `01-scaffolding.md` modifies four skill files (`qa`, `security`, `a11y`, `perf`) to add reference lines. The run sheet currently shows only file creations, hiding the skill edits — misleading scope, wrong commit message coverage, and risk of merge friction with Step 2.

**Current:**
```markdown
**Creates:**
- `AGENTS.md` (repo root)
- `CLAUDE.md` (repo root)
- `instructions/generic/honesty-contract.instructions.md`
- `references/testing-patterns.md`
- `references/security-checklist.md`
- `references/accessibility-checklist.md`
- `references/performance-checklist.md`
- Appends skill template section to `docs/EXTENSION_GUIDE.md`
```

**Replacement:**
```markdown
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
```

---

## E2 — Step 0 baseline is stricter than QA.md guarantees

**Section:** Step 0: Pre-flight, the `**Expected:**` line.

**Why:** `QA.md` documents the baseline as "120+ tests pass" and "27+ resolved, 10+ copied". The run sheet hard-codes exact numbers, so any benign test addition before this sprint runs produces a false negative.

**Current:**
```markdown
**Expected:** 120 passed, 14 skipped | 27 resolved, 10 copied, 13 agents, 2 token warnings
```

**Replacement:**
```markdown
**Expected:** ≥120 passed, ~14 skipped, 0 failed | ≥27 resolved, ≥10 copied, 13 agents, exactly 2 expected token warnings (`{{tokens}}` in onboarding, `{{ secrets.* }}` in security). Record the exact numbers here as the locked baseline for this sprint:
- tests passed: _____
- tests skipped: _____
- resolved files: _____
- copied files: _____
```

---

## E3 — Step 4 verify block lacks the checks Step 4 most needs

**Section:** Step 4: Multi-Platform, the `**Verify:**` block.

**Why:** Step 4 is the only step that touches `init.py` and `SecurityValidator`. Current verify confirms file counts but not (a) that new tests exist and pass, (b) that `cursor`/`all` were added to `VALID_EDITOR_TARGETS`, or (c) that the security validator accepts them. ADOPTION_PLAN.md flags all three as required.

**Current:**
```powershell
**Verify:**
```powershell
python -m pytest tests/ -v
python init.py --config config/project.config.example.yml
(Get-ChildItem prompts/*.prompt.md).Count  # 5
Test-Path hooks/session-start.sh           # True
```
```

**Replacement:**
```powershell
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
```

**Rollback:** If any check fails, `git reset --hard HEAD` to drop Step 4 changes and re-attempt. Do **not** partially commit.
```

---

## E4 — Step 1 verifies source files only, not resolved output

**Section:** Step 1: Scaffolding, the `**Verify:**` block.

**Why:** QA criterion #4 requires `resolved/instructions/honesty-contract.instructions.md` to exist after init.py. The current verify only checks the source file, telling us nothing about whether the generic glob actually picked it up.

**Current:**
```powershell
**Verify:**
```powershell
python init.py --config config/project.config.example.yml
python -m pytest tests/ -v
Test-Path AGENTS.md
Test-Path CLAUDE.md
Test-Path instructions/generic/honesty-contract.instructions.md
(Get-ChildItem references/*.md).Count  # expect 4
```
```

**Replacement:**
```powershell
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
```
```

---

## O1 — PowerShell verify blocks need fail-fast + exit-code checks

**Section:** Step 2 and Step 3 verify blocks. (Step 1 and Step 4 are already updated by E3/E4.)

**Why:** Without `$ErrorActionPreference = 'Stop'` and `$LASTEXITCODE` checks, a failing `python` call still lets subsequent assertions run and the user reads a green-looking report.

**Step 2 — Current:**
```powershell
**Verify:**
```powershell
(Select-String -Path skills/*/*.skill.md -Pattern "## Common Rationalizations").Count  # 13
(Select-String -Path skills/*/*.skill.md -Pattern "## Red Flags").Count                # 13
(Select-String -Path skills/*/*.skill.md -Pattern "## Verification").Count             # 13
python init.py --config config/project.config.example.yml
python -m pytest tests/ -v
```
```

**Step 2 — Replacement:**
```powershell
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
```
```

**Step 3 — Current:**
```powershell
**Verify:**
```powershell
python init.py --config config/project.config.example.yml
Select-String -Path resolved/instructions/handoff-rejection-format.instructions.md -Pattern "Fix"
python scripts/verify-hash-chain.py starters/FILE_HASHES.md
python -m pytest tests/ -v
```
```

**Step 3 — Replacement:**
```powershell
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
```
```

---

## O2 — Add re-run cleanup note to the top-of-file rules

**Section:** Top of file, immediately after the two existing `> **Rule:** ...` lines.

**Why:** If a step fails partway through and the user re-runs it, stale `resolved/` artifacts can mask new failures. init.py rebuilds `resolved/`, so wiping it before retry is safe.

**Insert after:**
```markdown
> **Rule:** Do NOT proceed to the next step without explicit owner approval.
> **Rule:** Do NOT delete any files in `docs/sprints/best-practice-alignment/`. Cleanup is manual-only by the owner.
```

**Add these lines:**
```markdown
> **Rule:** Before **re-running** a step that previously failed mid-way, clear stale build output: `Remove-Item -Recurse -Force resolved/*`. init.py will rebuild it. Do not do this on a first attempt — only on retry.
> **Rule:** Each verify block sets `$ErrorActionPreference = 'Stop'` and checks `$LASTEXITCODE` after every `python …` call. Do not strip these.
```

---

## O3 — Step 4 ordering rule is prose only

**Section:** Step 4: Multi-Platform, under the "Execute 3.1 … before 3.2 …" line.

**Why:** The 3.1 → 3.2 dependency is documented in `04-platform.md` ("path-scoped frontmatter must land before cursor emission — reuses `scope` field") but is asserted only in prose. Make it a precondition the verify block can catch.

**Current:**
```markdown
Execute 3.1 (path-scoped frontmatter) before 3.2 (cursor emission). Then 3.3 and 3.4 in any order.

**⚠️ Only step that modifies `init.py`. Write tests before changing production code.**
```

**Replacement:**
```markdown
Execute 3.1 (path-scoped frontmatter) before 3.2 (cursor emission). Then 3.3 and 3.4 in any order.

**Precondition gate before starting 3.2:** confirm 3.1 landed by checking resolved instructions carry a `scope:` field:
```powershell
Select-String -Path resolved/instructions/*.instructions.md -Pattern "^scope:" | Select-Object -First 1
# expect at least one match before proceeding to 3.2
```

**⚠️ Only step that modifies `init.py`. Write tests before changing production code.** Tests for 3.1 and 3.2 must exist and fail in the expected way *before* the init.py changes are written. The Step 4 verify block records the post-fix test count delta vs Step 0 baseline.
```

---

## O4 — Step 6 doesn't enumerate the 10 criteria

**Section:** Step 6: Final QA, the verify block.

**Why:** "Walk through every criterion in QA.md" is unstructured. Inline the 10 checks so they're copy-pasteable and the audit trail is concrete.

**Current:**
```markdown
Run full verification against all 10 success criteria.

```powershell
python -m pytest tests/ -v
python init.py --config config/project.config.example.yml
```

Walk through every criterion in QA.md. Report pass/fail for each.
```

**Replacement:**
```markdown
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
```

---

## O5 — Step 4 needs an explicit rollback line (covered by E3)

**Status:** Already folded into the E3 replacement (`**Rollback:**` line). No separate edit needed.

---

## I1 — Broaden `applyTo` scope or add explicit-attach note

**Section:** Frontmatter at top of file.

**Why:** This run sheet drives changes throughout the repo (`skills/`, `instructions/`, `init.py`, `config/`, `docs/`), but `applyTo` only matches the sprint directory itself. Agents working on the affected files won't see this guidance auto-attached. Two valid responses; pick one:

**Current:**
```markdown
---
applyTo: "docs/sprints/best-practice-alignment/**"
---
```

**Option A (broaden — auto-attaches everywhere the sprint touches):**
```markdown
---
applyTo: "docs/sprints/best-practice-alignment/**,AGENTS.md,CLAUDE.md,skills/**,instructions/**,references/**,init.py,config/**,prompts/**,hooks/**,scripts/verify-hash-chain.py,tests/test_init.py,tests/test_hash_chain.py"
---
```

**Option B (keep narrow, add note):** keep frontmatter as-is and add immediately after the title:
```markdown
> **Scope note:** This instruction auto-attaches only inside `docs/sprints/best-practice-alignment/`. When working on the files it touches (init.py, skills, references, etc.), open this run sheet explicitly so the assistant sees the verification commands and approval gates.
```

Owner choice. Option B is the safer default (no risk of accidentally attaching during unrelated work on `init.py` after the sprint completes).

---

## I2 — Replace prose approval cues with explicit gate blocks

**Section:** After each step's `**On complete:**` line (Steps 1–5).

**Why:** "Ask owner to approve Step N" reads as advisory. An explicit gate block is harder to skip.

**Pattern — append after each `**On complete:** …` line:**
```markdown

> **⛔ APPROVAL GATE — Step N → Step N+1.** Wait for explicit owner approval before proceeding. Do not start the next step's tasks, edits, or verification.
```

Apply for Steps 1, 2, 3, 4, 5 (Step 0 already has its gate; Step 6 ends the sprint).

---

## I3 — Capture commit hash after each commit

**Section:** Each step's verify block, immediately after the existing checks.

**Why:** Run sheet currently shows the commit *message* but never records the resulting hash, hurting the audit trail.

**Append to each verify block (Steps 1–5):**
```powershell
# Audit trail
git log --oneline -1
```

---

## I4 — Note Step 1.7 template intentionally describes future-state sections

**Section:** Step 1: Scaffolding, immediately under the `**Work package:**` line.

**Why:** Task 1.7 documents skill sections (Common Rationalizations, Red Flags, Verification) that won't exist on any skill until Step 2 runs. This is intentional (it's a template). Reviewers may otherwise flag the template as describing non-existent fields.

**Add line:**
```markdown
> **Note:** Task 1.7 appends a skill template to `docs/EXTENSION_GUIDE.md` that documents Common Rationalizations / Red Flags / Verification sections. These sections do not exist on any skill until Step 2 lands them. The template is forward-looking by design — do not flag this as drift.
```

---

## Application order

Apply E1 → E4, then O1 → O4, then (owner choice) I1, then I2 → I4. Each edit is independent; failures do not block other items.

After applying, run the Step 0 verify block once to confirm the run sheet itself hasn't broken any baseline assumption, then delete this file.
