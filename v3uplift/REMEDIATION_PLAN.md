# v3 Uplift — QA Remediation Plan

Fixes for the 10 critical and 37 cosmetic violations from Phase 4.5.
Grouped by work package. Execute in order — later packages depend on
decisions made in earlier ones.

---

## Decisions (all confirmed)

| # | Decision | Choice | Effect |
|---|----------|--------|--------|
| 1 | Section ordering (CS-04) | **Option A** — update the guide to match delivered skills | Eliminates 13 cosmetic violations. 1 file edit. |
| 2 | Dead ADR-0008 link (CV-06) | **Remove** the reference | Dead link deleted. No retroactive ADR. |
| 3 | Prohibition style in list items (CS-01) | **Document both** conventions in guide | Skills: `**never** verb`. List items in agent bodies: `**Never** verb phrase` is acceptable. Eliminates 19 cosmetic fixes. |
| 4 | Reviewer duplication (CS-06) | **Reference** the instruction | Replace inlined rules with reference to `planning-compliance` instruction. |
| 5 | "Consider" in instructions (CS-03) | **Rewrite** with context | Read each instance; use imperative if mandatory, conditional if optional. |

**Net impact of decisions:** 13 + 19 = 32 cosmetic violations resolved by
documenting conventions. Remaining work: 10 critical fixes + 5 cosmetic
rewrites + 1 guide update.

---

## Work Package 1 — Prohibition Style (mechanical)

**Violations:** CV-01, CV-02, CS-01, CS-02  
**Files affected:** 1 skill, 3 instructions, 5 agent bodies, 1 instruction  
**Method:** grep + replace  
**Estimated edits:** ~30

### Critical (must fix)

| File | Find | Replace |
|------|------|---------|
| `skills/reviewer/reviewer.skill.md` (×6) | `MUST` | `**must**` |
| `instructions/configurable/batch-report.instructions.md` | `These MUST use` | `These **must** use` |
| `instructions/configurable/determinism-guarantees.instructions.md` | `MUST use` | `**must** use` |
| `instructions/configurable/sprint-docs-format.instructions.md` | `MUST include` | `**must** include` |

### Cosmetic (CS-02 only)

**File:** `instructions/generic/askquestions-contract.instructions.md` line 19
**Fix:** `**Never render…**` → `**never** render…`

**CS-01 (19 agent body list items) — resolved by Decision 3.** The guide
will document that `**Never** verb phrase` is acceptable at the start of
list items. No edits needed in agent bodies.

### Post-fix validation

```powershell
grep -ri "MUST\b" skills/ instructions/ agents/ | grep -v "must\*\*"
```

Should return empty.

---

## Work Package 2 — Voice Fixes (judgement required)

**Violations:** CV-03, CV-04, CS-03, CS-05  
**Files affected:** 2 skills, 4 instructions, 1 agent body  
**Method:** manual rewrite of specific lines

### Critical

| File | Line | Current | Rewrite |
|------|------|---------|---------|
| `skills/bug/bug.skill.md` | 157 | "cleanup is handled by `/plan-cleanup`" | "`/plan-cleanup` handles cleanup" |
| `skills/pm/pm.skill.md` | 167 | "standing rejections the current request might conflict with" | "standing rejections the current request conflicts with" |

### Cosmetic

| File | Line | Word | Action |
|------|------|------|--------|
| `instructions/configurable/handoff-rejection-format.instructions.md` | 74 | "consider" | Replace with direct imperative |
| `instructions/configurable/validation-framework.instructions.md` | 30 | "Consider" | Replace with direct imperative |
| `instructions/configurable/retro-report.instructions.md` | 222 | "consider" | Replace with direct imperative |
| `instructions/configurable/observability.instructions.md` | 368 | "Consider" | Replace with direct imperative |
| `agents/pm.body.md` | 107 | "is defined in" (passive) | "lives in" |

### Post-fix validation

```powershell
grep -rn "consider\|might\|perhaps\|potentially" skills/ agents/
```

Should return zero hits in skill files. Instruction hits acceptable
only if used as a noun ("consideration") not as hedging.

---

## Work Package 3 — Cross-Reference Accuracy (specific edits)

**Violations:** CV-05, CV-06, CV-07  
**Files affected:** 2 docs, 1 Python file, 1 potential new file

| ID | File | Fix |
|----|------|-----|
| CV-05 | `docs/ARCHITECTURE.md` line 13 | Change "24 instruction files" → "25 instruction files" |
| CV-06 | References to `command-centre/decisions/0008-ship-protocol-v1-complete.md` | **Remove** the dead reference (Decision 2) |
| CV-07 | `init.py` lines 6–8 and 359 | Change `python3 init.py` → `python init.py` (4 occurrences) |

### Post-fix validation

```powershell
grep -rn "python3" *.py docs/ instructions/
grep -rn "0008" command-centre/ docs/
```

---

## Work Package 4 — Duplication (CS-06)

**Violation:** `skills/reviewer/reviewer.skill.md` lines 71–80 duplicates
rules from `instructions/configurable/planning-compliance.instructions.md`.

**Fix:** Replace the inlined rules with a reference:

```markdown
## Pattern Compliance

Validate patterns declared in the project's `planning-compliance`
instruction. Flag deviations. **do not** enforce patterns not declared there.
```

This prevents divergence if the instruction is updated independently.

### Post-fix validation

Verify the reviewer skill still reads coherently and that no test asserts
the removed inline content.

---

## Work Package 5 — Guide Update (Decision 1 + Decision 3)

**File:** `docs/SKILL_AUTHORING_GUIDE.md`

Update the guide to reflect delivered conventions:

1. **Section headings:** Change "Core Constraints" → "Constraints" as
   the canonical heading. Document that the output section heading is
   flexible — "Report Format" or "Machine-Readable Summary" depending
   on skill type (not "Output Contract"). Note that Shared Rules
   position is flexible (before or after workflow sections).

2. **Prohibition style in list items:** Add a note that `**Never** verb
   phrase` (capital N, full phrase bold) is acceptable at the start of
   list items in agent bodies and instructions. Skills use `**never**
   verb` (lowercase, keyword-only bold) in prose.

### Post-fix validation

Read the updated guide. Confirm it matches what all 13 skills actually do.

---

## Execution Order

1. Work Package 5 (guide update) — establishes conventions before fixes
2. Work Package 1 (prohibition style) — mechanical, low risk
3. Work Package 3 (cross-references) — mechanical, low risk
4. Work Package 2 (voice) — requires reading context around each line
5. Work Package 4 (duplication) — requires checking reviewer coherence
6. Run build + tests
7. Run QA grep checks from all packages
8. Confirm zero critical violations remain

---

## Gate Criteria

Phase 4.5 remediation is complete when:

- [ ] Zero critical violations remain
- [ ] All grep checks return empty
- [ ] `python init.py --config config/project.config.example.yml` passes
- [ ] `python -m pytest tests/ -v` — 233 pass, 0 fail
- [ ] Cosmetic violations either fixed or documented as accepted deviations
