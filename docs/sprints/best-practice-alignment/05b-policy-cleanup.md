# 05b — OPA Rego Cleanup (Audit Follow-Through)

> **Depends on:** Step 5 (`docs/POLICY_AUDIT.md` committed)
> **Branch:** `chore/policy-cleanup` (separate from the sprint branch)
> **Commits:** Three, in order. Do not squash.
> **Verify:** All three commits land green; no `policies/`, `.rego`, or `OPA Rego` references remain outside the allow-list below.

This work package executes the audit's recommended disposition. It is sequenced as a separate, owner-approved cleanup so the sprint's Step 6 QA gate can sign off the sprint independently.

---

## Pre-flight

```powershell
$ErrorActionPreference = 'Stop'

# 1. Confirm the audit commit exists on main
git log --oneline -5
# Expect: a recent commit with message "docs(audit): OPA Rego policy catch-rate assessment"

# 2. Confirm working tree is clean of unrelated changes
git status --short
# If anything unrelated is dirty, STOP and ask the owner before continuing.
# Do NOT git stash — unrelated dirty files in this repo have caused conflicts before.

# 3. Branch off
git switch -c chore/policy-cleanup

# 4. Record baseline (will be compared after commit 3)
python -m pytest tests/ -v 2>&1 | Tee-Object -Variable baselineOutput | Select-Object -Last 5
# Note the "X passed, Y skipped" line. Record both numbers in the final commit message.
```

**Stop-and-ask trigger:** if the audit commit isn't on `main`, or the tree has unrelated dirty files, stop and ask the owner.

---

## Commit 1: Port composition rules to Python

**Creates:** `tools/sprint_lint.py`
**Commit message:** `feat(tools): add sprint composition linter (ports composition.rego rules)`

Port the 9 rules from `policies/composition.rego` into a small, dependency-free Python module. Each rule's message prefix must match the Rego version exactly so existing references stay valid.

**Required rules (all 9 from composition.rego):**

| Rule | Severity | Message prefix |
|---|---|---|
| Priority order (P0 > P1 > …) | violation | `PRIORITY_ORDER:` |
| Intra-tier score order | violation | `SCORE_ORDER:` |
| Feature mix < 50% | violation | `FEATURE_BALANCE:` |
| Feature mix > 80% | violation | `FEATURE_BALANCE:` |
| Capacity used > 100% | violation | `CAPACITY_EXCEEDED:` |
| Capacity used 90–100% | warning | `CAPACITY_HIGH:` |
| Excluded P0 bugs | violation | `BUG_POLICY:` |
| Debt pressure ≥ 40, no P2 debt | violation | `DEBT_PRESSURE:` |
| Age ≥ 3, tier ≥ P3 | warning | `AGE_ESCALATION:` |
| Item count > 15 | warning | `ITEM_COUNT:` |

**Input shape** (mirrors what `composition.rego` consumed):

```python
{
  "composition": [
    {"itemId": str, "type": "feature"|"bug"|"debt", "tier": "P0".."P6",
     "score": float, "age": int, "index": int},   # index is 0-based position
    ...
  ],
  "excluded": [
    {"itemId": str, "type": ..., "tier": ...},
    ...
  ],
  "constraints": {
    "featurePercent": float,    # 0–100
    "capacityUsed": float,      # 0–100+
    "debtPressure": float       # 0–100
  }
}
```

**Public API:**

```python
def lint(composition: dict) -> dict:
    """Return {'violations': [str, ...], 'warnings': [str, ...]}."""
```

A future Python orchestrator (or a CI step) can import `tools.sprint_lint.lint`. The `planner` skill's procedure references it by path; the skill itself remains Markdown.

**Tests:** add a minimal `tests/test_sprint_lint.py` with at least one positive and one negative case per rule (10 cases total minimum). No external dependencies.

**Verify:**

```powershell
$ErrorActionPreference = 'Stop'
python -m pytest tests/test_sprint_lint.py -v
if ($LASTEXITCODE -ne 0) { throw "sprint_lint tests failed" }
python -m pytest tests/ -v
if ($LASTEXITCODE -ne 0) { throw "full suite regressed" }
python init.py --config config/project.config.example.yml
if ($LASTEXITCODE -ne 0) { throw "init.py failed" }
```

---

## Commit 2: Delete OPA layer

**Commit message:** `chore(policies): remove unused OPA Rego layer (per POLICY_AUDIT.md)`

**Deletes:**

- `policies/composition.rego`
- `policies/security.rego`
- `policies/` directory (it will be empty after the two deletions)
- `src/phase1_verification/policy_engine.py`

**Edits:**

- `src/phase1_verification/__init__.py` — remove the line `from .policy_engine import *` (keep `from .validator import *`).
- `tests/test_contracts.py` — remove the line `from policy_engine import PolicyEngine` (around line 19) and the entire `class TestPolicyEngine:` block (starts ~line 209). Leave all other test classes untouched.

**Verify:**

```powershell
$ErrorActionPreference = 'Stop'

# Files removed
if (Test-Path policies/composition.rego) { throw "composition.rego not deleted" }
if (Test-Path policies/security.rego)    { throw "security.rego not deleted"    }
if (Test-Path policies)                  { throw "policies/ directory not deleted" }
if (Test-Path src/phase1_verification/policy_engine.py) { throw "policy_engine.py not deleted" }

# No PolicyEngine callers remain outside the deleted test class
$callers = Select-String -Path . -Pattern 'PolicyEngine' -Recurse `
  -Include *.py,*.md `
  | Where-Object { $_.Path -notmatch '\\\.git\\|\\resolved\\|POLICY_AUDIT\.md$|\\docs\\sprints\\best-practice-alignment\\' }
if ($callers) {
  $callers | Format-Table -AutoSize
  throw "PolicyEngine still referenced outside allow-list — STOP and ask owner"
}

# Suite still green
python -m pytest tests/ -v
if ($LASTEXITCODE -ne 0) { throw "pytest regressed after deletion" }
python init.py --config config/project.config.example.yml
if ($LASTEXITCODE -ne 0) { throw "init.py failed" }
```

**Stop-and-ask trigger:** any unexpected `PolicyEngine` caller surfaced by the grep.

---

## Commit 3: Documentation cleanup

**Commit message:** `docs: remove OPA Rego references (per POLICY_AUDIT.md)`

**Edits** (all references to `policies/`, `*.rego`, and `OPA Rego` must go, except in the allow-list at the bottom of this file):

| File | Location | Action |
|---|---|---|
| [AGENTS.md](../../../AGENTS.md) | Key directories table (~line 62) | Delete the `\| `policies/` \| OPA Rego guardrails \|` row. |
| [README.md](../../../README.md) | Directory tree (~line 345) | Delete the `├── policies/         # Rego policy rules` line. |
| [tests/README.md](../../../../tests/README.md) | Troubleshooting table (~line 155) | Delete the `\| FileNotFoundError: policies/ \| Wrong working directory \| cd to agent-homebase root \|` row. *(This was previously mis-attributed to repo-root README.md — it lives in `tests/README.md`.)* |
| [docs/POLICIES.md](../../POLICIES.md) | Whole file | Delete the file. It documents the now-removed OPA layer end-to-end; a stub would mislead. The audit (`docs/POLICY_AUDIT.md`) supersedes it. |
| [docs/CONTRIBUTING.md](../../CONTRIBUTING.md) | ~line 51 (tree row) and ~lines 280–325 (Rego example block) | Delete the `policies/` tree row and the "Adding a new Rego policy" example block. |
| `command centre/00-overview/architecture.md` *(in retired v1 workbench)* | ~lines 17 and 74 | Remove `policies/` from both substrate listings. |
| `command centre/00-overview/glossary.md` *(in retired v1 workbench)* | ~line 6 | Remove `policies/` from the Substrate row. |
| `command centre/decisions/0004-shared-substrate-at-root.md` *(in retired v1 workbench)* | ~line 24 | Remove the `policies/` tree row. |
| [docs/DUAL_PLATFORM_PLAN.md](../../DUAL_PLATFORM_PLAN.md) | ~lines 164 and 195 | Delete the two table rows referencing `policies/*.rego`. |
| [starters/FILE_HASHES.md](../../../starters/FILE_HASHES.md) | ~line 21 | Remove the `policies/*.rego, SECURITY_CHANGELOG.md` bullet from the `Tracked file categories` HTML comment. The data table below is currently empty (no chained rows exist yet), so **no re-signing is required**. Verify with `python scripts/verify-hash-chain.py starters/FILE_HASHES.md` — exit code 0. |
| [instructions/configurable/security-audit.instructions.md](../../../instructions/configurable/security-audit.instructions.md) | ~line 127 | Remove the `policies/*.rego, ` fragment from the security-policy bullet, leaving the `{{paths.security_changelog}}` reference. After this edit, re-run `python init.py` so the resolved copy is regenerated. |

**Allow-list (these references stay — they document history or are inside the audit/sprint scratch):**

- `docs/POLICY_AUDIT.md` — the audit itself.
- `docs/sprints/best-practice-alignment/**` — sprint scratch; protected by the no-delete rule.
- `resolved/**` — build output, regenerated from sources.
- `.git/**`.

**Verify:**

```powershell
$ErrorActionPreference = 'Stop'

# Hash-chain still valid
python scripts/verify-hash-chain.py starters/FILE_HASHES.md
if ($LASTEXITCODE -ne 0) { throw "hash chain broken — STOP and ask owner" }

# Suite green, build clean
python -m pytest tests/ -v
if ($LASTEXITCODE -ne 0) { throw "pytest failed" }
python init.py --config config/project.config.example.yml
if ($LASTEXITCODE -ne 0) { throw "init.py failed" }

# Leak check — must return zero hits
$leaks = Get-ChildItem -Recurse -File -Include *.md,*.py,*.yml,*.yaml,*.json `
  | Where-Object { $_.FullName -notmatch '\\\.git\\|\\resolved\\|POLICY_AUDIT\.md$|\\docs\\sprints\\best-practice-alignment\\' } `
  | Select-String -Pattern 'policies/|\.rego|OPA Rego|policy_engine|PolicyEngine'
if ($leaks) {
  $leaks | Format-Table Path,LineNumber,Line -AutoSize
  throw "Stale OPA references remain outside allow-list"
}

# Record post-cleanup baseline for the commit message
python -m pytest tests/ 2>&1 | Select-Object -Last 3
```

**Commit message body must include:**

```
Pre-cleanup baseline: <X passed, Y skipped>   (from pre-flight)
Post-cleanup result : <X' passed, Y' skipped> (delta: removed N skipped tests from TestPolicyEngine)
```

If `docs/sprints/best-practice-alignment/QA.md` references a hard-coded test count for criterion 9, update it in this commit and note the change in the message.

---

## Final report to owner

Report:
1. The three commit SHAs in order.
2. Pre- and post-cleanup pytest numbers.
3. Confirmation that the leak grep returned zero hits.
4. Any items where you stopped and asked vs. proceeded.

Then open the PR with title `chore: remove unused OPA Rego layer` and link `docs/POLICY_AUDIT.md` as the rationale.
