---
applyTo: "docs/sprints/best-practice-alignment/**"
---

# Best-Practice Alignment — Run Sheet

Execution instruction for the best-practice-alignment work packages. Work one step at a time. After each step: verify, report results, and **stop for owner approval** before continuing.

> **Rule:** Do NOT proceed to the next step without explicit owner approval.
> **Rule:** Do NOT delete any files in `docs/sprints/best-practice-alignment/`. Cleanup is manual-only by the owner.

---

## Step 0: Pre-flight

**Status:** `pending`

Establish baseline before any changes.

```powershell
$env:PYTHONIOENCODING='utf-8'
python -m pytest tests/ -v
python init.py --config config/project.config.example.yml
```

**Expected:** 120 passed, 14 skipped | 27 resolved, 10 copied, 13 agents, 2 token warnings

**On complete:** Report baseline numbers. Ask owner to approve Step 1.

---

## Step 1: Scaffolding

**Status:** `pending`

**Work package:** `docs/sprints/best-practice-alignment/01-scaffolding.md`

Execute task groups 1.1, 1.2, 1.3, 1.6, 1.7 from that file.

**Creates:**
- `AGENTS.md` (repo root)
- `CLAUDE.md` (repo root)
- `instructions/generic/honesty-contract.instructions.md`
- `references/testing-patterns.md`
- `references/security-checklist.md`
- `references/accessibility-checklist.md`
- `references/performance-checklist.md`
- Appends skill template section to `docs/EXTENSION_GUIDE.md`

**Verify:**
```powershell
python init.py --config config/project.config.example.yml
python -m pytest tests/ -v
Test-Path AGENTS.md
Test-Path CLAUDE.md
Test-Path instructions/generic/honesty-contract.instructions.md
(Get-ChildItem references/*.md).Count  # expect 4
```

**Commit:** `feat(docs): add AGENTS.md, CLAUDE.md, honesty contract, references, skill template`

**On complete:** Report verification results. Ask owner to approve Step 2.

---

## Step 2: Skills Hardening

**Status:** `pending`

**Work package:** `docs/sprints/best-practice-alignment/02-skills.md`

Execute task group 1.4 (anti-rationalization) first, then 1.5 (red flags + verification). Order matters.

**Edits:** All 13 `skills/*/*.skill.md` files

**Verify:**
```powershell
(Select-String -Path skills/*/*.skill.md -Pattern "## Common Rationalizations").Count  # 13
(Select-String -Path skills/*/*.skill.md -Pattern "## Red Flags").Count                # 13
(Select-String -Path skills/*/*.skill.md -Pattern "## Verification").Count             # 13
python init.py --config config/project.config.example.yml
python -m pytest tests/ -v
```

**Commit:** `feat(skills): add anti-rationalization, red flags, verification to all 13 skills`

**On complete:** Report grep counts and test results. Ask owner to approve Step 3.

---

## Step 3: Format Upgrades

**Status:** `pending`

**Work package:** `docs/sprints/best-practice-alignment/03-formats.md`

Execute task groups 2.1 (handoff fields) then 2.2 (hash-chain).

**Edits:** `instructions/configurable/handoff-rejection-format.instructions.md`, `starters/FILE_HASHES.md`
**Creates:** `scripts/verify-hash-chain.py`, `tests/test_hash_chain.py`

**Verify:**
```powershell
python init.py --config config/project.config.example.yml
Select-String -Path resolved/instructions/handoff-rejection-format.instructions.md -Pattern "Fix"
python scripts/verify-hash-chain.py starters/FILE_HASHES.md
python -m pytest tests/ -v
```

**Commit:** `feat(formats): structured handoff fields, hash-chain signing for FILE_HASHES`

**On complete:** Report verification results. Ask owner to approve Step 4.

---

## Step 4: Multi-Platform

**Status:** `pending`

**Work package:** `docs/sprints/best-practice-alignment/04-platform.md`

Execute 3.1 (path-scoped frontmatter) before 3.2 (cursor emission). Then 3.3 and 3.4 in any order.

**⚠️ Only step that modifies `init.py`. Write tests before changing production code.**

**Edits:** `init.py`, `config/project.config.example.yml`, `config/plugin.json`, `tests/test_init.py`
**Creates:** `prompts/` (5 files), `hooks/` (2 files)

**Verify:**
```powershell
python -m pytest tests/ -v
python init.py --config config/project.config.example.yml
(Get-ChildItem prompts/*.prompt.md).Count  # 5
Test-Path hooks/session-start.sh           # True
```

**Commit:** `feat(init): path-scoped frontmatter, cursor emission, lifecycle commands, session hook`

**On complete:** Report test results including new tests. Ask owner to approve Step 5.

---

## Step 5: Audit

**Status:** `pending`

**Work package:** `docs/sprints/best-practice-alignment/05-audit.md`

Execute task group 4.1. Read-only analysis of OPA Rego policies.

**Creates:** `docs/POLICY_AUDIT.md`

**Verify:**
```powershell
Test-Path docs/POLICY_AUDIT.md  # True
```

**Commit:** `docs(audit): OPA Rego policy catch-rate assessment`

**On complete:** Report audit findings and recommendation. Ask owner to approve Final QA.

---

## Step 6: Final QA

**Status:** `pending`

**Checklist:** `docs/sprints/best-practice-alignment/QA.md`

Run full verification against all 10 success criteria.

```powershell
python -m pytest tests/ -v
python init.py --config config/project.config.example.yml
```

Walk through every criterion in QA.md. Report pass/fail for each.

**On complete:** Report full QA results. Notify owner that cleanup is ready.

> **⛔ Cleanup is manual-only.** Do NOT delete `docs/sprints/best-practice-alignment/`. The owner will do this when ready.
