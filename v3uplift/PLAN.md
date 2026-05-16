# agent-homebase 3.0.0 — Uplift Plan

Version: 3.0.0
Status: DRAFT
Created: 2026-05-16

## Mission

Unify voice, tighten discipline, and adopt best-in-class skill authoring
conventions across the entire repo. The output should read as one author
with one register — direct, imperative, no hedging.

Sources of influence:

- **Addy Osmani / agent-skills** — description discipline (what + when,
  1024 chars), writing principles, progressive disclosure, token-conscious
  authoring.
- **Matt Pocock / skills** — imperative voice, domain glossary (CONTEXT.md),
  hard/soft dependency classification (ADR-0001), skills as direct
  instructions not reference docs.
- **agent-homebase v2** — governance, promotion contract, return tiers,
  multi-project portability, build-time validation. These stay.

---

## Baseline (pre-uplift snapshot)

Record before any changes. Every phase gates on this baseline staying green.

| Check | Command | Expected |
|-------|---------|----------|
| Tests | `python -m pytest tests/ -v` | 233 pass, 7 skip, 0 fail |
| Build | `python init.py --config config/project.config.example.yml` | Exit 0, resolved/ populated |
| Determinism | Run build twice, diff resolved/ | Byte-identical |
| Git | `git status` | Clean working tree |

**Action:** Run all four checks. Record outputs to `v3uplift/baseline.log`.
Tag `v2.0.0-final` if not already tagged. Create branch `v3-uplift`.

---

## Phase 1 — Foundations

Three new files that set the rules everything else follows.

### 1A. Skill Authoring Guide

**File:** `docs/SKILL_AUTHORING_GUIDE.md`
**Staged draft:** `v3uplift/drafts/SKILL_AUTHORING_GUIDE.md`

Content — merge these conventions into one document:

**Voice rules:**
- Skills are direct instructions to an agent. Write as if briefing a
  colleague: "You are the reviewer. You read diffs. You never modify code."
- Second-person imperative throughout. No passive voice.
- No hedging words (consider, perhaps, might want to, it may be useful).
- Prohibitions use bold: **never**, **do not**. Not ALL CAPS.
  Standardise across the repo.

**Description rules (from Addy):**
- Max 1024 characters.
- First sentence: what the skill does (third person).
- Second sentence: "Use when [trigger conditions]."
- Include both what AND when. Do not summarise the workflow.
- The description is the only thing the agent sees when deciding which
  skill to load. It must be sufficient for routing.

**Section template (reconciled with existing EXTENSION_GUIDE):**

```
---
(frontmatter - unchanged from v2 schema)
---
# Title

## Overview
1-2 sentences. Elevator pitch.

## When to Use
- Positive triggers
- When NOT to use (exclusions) ← NEW, currently missing from all 13

## Core Constraints
Hard rules. Bold prohibitions.

## Workflow
Numbered steps. Imperative. Specific ("Run X" not "verify X").

## Output Contract
What the skill produces. Return tier. Artifact paths.

## Common Rationalizations
| Rationalization | Reality |
(Already present in all 13. Review for quality.)

## Red Flags
(Already present in all 13. Review for quality.)

## Verification
Checklist. Every item must be verifiable with evidence.
```

**Writing principles (from Addy, adapted):**
1. Process over knowledge — skills are workflows, not reference docs.
2. Specific over general — "Run `python -m pytest`" beats "run the tests".
3. Evidence over assumption — every verification checkbox needs proof.
4. Anti-rationalization — every skip-worthy step gets a rebuttal.
5. Progressive disclosure — SKILL.md is the entry point. Reference
   material belongs in `references/` or supporting files, not inline.
6. Token-conscious — if removing a section would not change agent
   behaviour, remove it.

**Length rules:**
- Target: under 200 lines per SKILL.md (existing EXTENSION_GUIDE rule).
- 5 skills currently exceed this (planner 310, pm 260, docs 225,
  sprint-lead 480, security 660).
- Skills over 200 lines must extract reference material into supporting
  files in the same skill directory.

**QA for 1A:**
- [ ] Guide is self-consistent (no contradictions with EXTENSION_GUIDE).
- [ ] Every rule is testable — an auditor can check pass/fail.
- [ ] Guide follows its own voice rules.

---

### 1B. Domain Glossary

**File:** `CONTEXT.md` (repo root, following Pocock convention)
**Staged draft:** `v3uplift/drafts/CONTEXT.md`

Define agent-homebase's own terms. Pin them. Flag ambiguities.

**Required entries** (minimum — add more during drafting):

| Term | Definition | Avoid |
|------|-----------|-------|
| Skill | A reusable workflow loaded by an agent at invocation time. Lives in `skills/<name>/`. | "plugin", "tool" (different concepts) |
| Instruction | A shared rule loaded by file pattern. Lives in `instructions/`. | "policy" (too formal), "config" (too vague) |
| Agent body | The persona wrapper that gives an agent its role, constraints, and skill bindings. Lives in `agents/`. | "agent definition" (ambiguous with resolved output) |
| Resolved | Build output produced by `init.py`. Lives in `resolved/`. Read-only. | "deployed", "compiled", "generated" |
| Token | A `{{placeholder}}` in a template file, replaced at build time from project config. | "variable" (too generic), "parameter" |
| Profile | A pre-built project config for a common stack. Lives in `profiles/`. | "template" (overloaded) |
| Substrate | The agent-homebase repo itself — the authoring layer that produces resolved artifacts. | "framework" (implies runtime), "platform" |
| Mode | An orchestration pattern (Mode 1 = direct, Mode 2 = file-queue, Mode 3 = registry). | "level", "tier" (those refer to return schemas) |
| Return tier | Structured JSON output shape (Tier 1/2/3) required from callables. | "mode" (different concept) |
| Promotion | Moving a pattern from a consumer project into the substrate after governance review. | "merge", "upstream" (too git-specific) |

**Flagged ambiguities** section for terms that have caused confusion.

**QA for 1B:**
- [ ] Every term used in skills, instructions, and docs appears in the glossary.
- [ ] No term has conflicting definitions across files.
- [ ] "Avoid" column entries do not appear in agent-facing files.

---

### 1C. Hard/Soft Dependency Classification

**File:** `docs/decisions/0001-hard-soft-instruction-dependencies.md`
**Staged draft:** `v3uplift/drafts/0001-hard-soft-deps.md`

Apply Pocock's ADR-0001 pattern to agent-homebase's instruction split.

**Hard dependency** — instruction requires project-specific tokens to
function. Without them, output is wrong. These are `configurable/`.
Must include explicit pointer: "Requires project config. Run `init.py`
if tokens are unresolved."

**Soft dependency** — instruction works generically. Output is less sharp
without project context but not wrong. These are `generic/`.
Reference "the project's conventions" in vague prose only.

Audit every instruction file and classify. Document the classification
and the reasoning.

**QA for 1C:**
- [ ] Every configurable instruction has explicit dependency pointer.
- [ ] Every generic instruction works without any project config.
- [ ] Classification matches actual token usage in each file.

---

## Phase 2 — Skill Audit and Rewrite

Apply the authoring guide from Phase 1A to all 13 skills.

### Pre-audit findings (from baseline audit)

**Already present in all 13 skills:**
- YAML frontmatter (consistent schema)
- Imperative voice (second-person, agent-addressed)
- Common Rationalizations table
- Red Flags list
- Verification checklist
- Core Constraints section

**Missing from all 13 skills:**
- Explicit "When NOT to use" section (4 have scope-gate redirects as
  partial equivalent)
- Overview section (elevator pitch)

**Inconsistencies across skills:**
- Prohibition style: some use bold `**never**`, some use `DO NOT` caps.
  Standardise to bold lowercase per authoring guide.
- Length: 5 skills exceed 200-line guideline. Extract to supporting files.
- Description quality: varies. All need review against 1024-char
  what+when format.

### Per-skill work

For each of the 13 skills:

1. **Review description** against authoring guide rules. Rewrite if needed.
   Verify under 1024 chars. Verify "what + when" format.
2. **Add "When to Use / When NOT to Use"** section if missing. Extract
   from existing scope-gate logic where present.
3. **Add Overview** section (1-2 sentences).
4. **Standardise prohibition style** — bold lowercase, not ALL CAPS.
5. **Review rationalization table** — are the rationalizations real? Would
   an agent actually try these excuses? Remove theatrical entries.
6. **Review red flags** — are they observable and actionable?
7. **Review verification checklist** — does every item have evidence?
8. **Length check** — if over 200 lines, extract reference material to
   supporting file in the skill directory.
9. **Voice check** — consistent with authoring guide. No passive voice,
   no hedging, no reference-doc register.
10. **Terminology check** — uses CONTEXT.md terms. No "Avoid" words.

### Skill-specific notes

| Skill | Lines | Key work |
|-------|-------|----------|
| a11y | ~130 | Description review, add When NOT, Overview |
| architect | ~195 | Description review, add When NOT, Overview |
| bug | ~165 | Description review, add When NOT, Overview |
| docs | ~225 | Over 200 — extract reference material. Description review |
| onboarding | ~175 | Align conversational tone with guide. Description review |
| perf | ~150 | Description review, add When NOT, Overview |
| planner | ~310 | Over 200 — extract reference material. Description review |
| pm | ~260 | Over 200 — extract reference material. Description review |
| qa | ~140 | Description review, add When NOT, Overview |
| researcher | ~220 | Over 200 — extract reference material. Description review |
| reviewer | ~175 | Description review, add When NOT, Overview |
| security | ~660 | Significantly over 200 — major extraction needed |
| sprint-lead | ~480 | Significantly over 200 — major extraction needed |

### QA for Phase 2

Per skill:
- [ ] Description under 1024 chars, has "what + when" format.
- [ ] Has Overview, When to Use, When NOT to Use sections.
- [ ] Prohibition style is bold lowercase only.
- [ ] Under 200 lines (or has extracted supporting files).
- [ ] No passive voice, no hedging words.
- [ ] Uses CONTEXT.md terminology only.
- [ ] Rationalization table has real, non-theatrical entries.
- [ ] Verification checklist items all have evidence requirements.

Across all skills:
- [ ] Consistent frontmatter schema.
- [ ] Consistent section order matches authoring guide template.
- [ ] `init.py` build still passes.
- [ ] All tests still pass.

---

## Phase 3 — Voice Unification

Full pass across all non-skill files. Target: one voice, one register.

### Cross-cutting fixes (from audit)

| Issue | Fix |
|-------|-----|
| Skill/agent count: "12" vs "13" in ARCHITECTURE, ONBOARDING | Correct to actual count |
| Python version: "3.8+" in ONBOARDING vs "3.12+" in AGENTS.md | Correct to 3.12+ everywhere |
| Python command: `python3` in ONBOARDING vs `python` in AGENTS.md | Standardise to `python` (Windows primary) |
| Shell dialect: PowerShell in QUICKSTART vs bash in ONBOARDING | Add cross-platform note or pick one and note the other |
| Prohibition style in agent bodies: `DO NOT` vs `**never**` | Standardise to bold lowercase per authoring guide |
| Person/voice in instructions: 2nd person vs 3rd person passive | Standardise to 2nd person imperative |
| Project-specific rules in generic files (Tailwind, factory pattern in planning-compliance, CUSTOMIZATION) | Move to example config or flag as adopter-specific |
| `@delivery-lead` referenced but not in 13-agent roster | Remove or add to roster |
| Schema description inconsistency between AGENTS.md and README | Pick one phrasing |

### File-by-file pass

**Docs** (voice target: direct, second-person, no hedging):
- [ ] README.md — clean up persona tags, align voice
- [ ] AGENTS.md — already terse, verify terminology
- [ ] docs/QUICKSTART.md — verify terminology
- [ ] docs/ONBOARDING.md — fix version, count, command inconsistencies
- [ ] docs/CUSTOMIZATION.md — strip project-specific examples or flag them
- [ ] docs/ARCHITECTURE.md — fix count, align "Why X?" tone
- [ ] docs/EXTENSION_GUIDE.md — reconcile with new authoring guide

**Instructions** (voice target: imperative, agent-addressed):
- [ ] Each generic instruction: 2nd person imperative
- [ ] Each configurable instruction: verify hard-dependency pointer

**Agent bodies** (voice target: imperative, bold-lowercase prohibitions):
- [ ] All 13 agent bodies: standardise prohibition style

### QA for Phase 3

- [ ] `grep -ri "DO NOT"` returns zero hits in skills and agent bodies
  (replaced with bold lowercase).
- [ ] `grep -ri "python3"` returns zero hits (standardised to `python`).
- [ ] `grep -ri "twelve\|12 skills\|12 agents"` returns zero hits where
  count is now 13.
- [ ] No hedging words in agent-facing files (consider, perhaps, might,
  it may be useful).
- [ ] Build passes. Tests pass.

---

## Phase 4 — Build and Test Validation

### 4A. Full build verification

```
python init.py --config config/project.config.example.yml
```

- [ ] Exit 0.
- [ ] All resolved/ files populated.
- [ ] No validation warnings or errors.
- [ ] Resolved skills reflect all Phase 2 changes.
- [ ] Resolved instructions reflect all Phase 3 changes.

### 4B. Test suite

```
python -m pytest tests/ -v
```

- [ ] All existing tests pass (233 baseline).
- [ ] No new test failures introduced.
- [ ] If new tests were added, they pass.

### 4C. Determinism check

Run build twice, diff output:

```
python init.py --config config/project.config.example.yml
cp -r resolved/ resolved-run1/
python init.py --config config/project.config.example.yml
diff -r resolved/ resolved-run1/
```

- [ ] Byte-identical output.

### 4D. Description validation

For all 13 skills, verify:

```python
# Pseudocode — can be a test or manual check
for skill in skills:
    assert len(skill.description) <= 1024
    assert "Use when" in skill.description or "Use to" in skill.description
    assert skill.description[0].isupper()  # starts with capital
```

### 4E. Terminology validation

Grep for "Avoid" terms from CONTEXT.md across all agent-facing files:

- [ ] No instances of "plugin" meaning skill.
- [ ] No instances of "variable" meaning token.
- [ ] No instances of "framework" meaning substrate.
- [ ] No instances of "deployed" meaning resolved.

### 4F. Length validation

- [ ] No SKILL.md over 200 lines (supporting files used for overflow).

---

## Phase 4.5 — Tone, Language & Glossary QA

A dedicated audit pass focused exclusively on consistency. Run by a
**separate agent session** using `v3uplift/prompts/tone-qa-audit.md`
as the full brief. This agent has no context of the build process —
it reads the repo cold and reports what it finds.

### Scope

Every agent-facing file in the repo:
- All 13 skills (`skills/**/*.skill.md` + supporting files)
- All agent bodies (`agents/*.body.md`)
- All instructions (`instructions/**/*.instructions.md`)
- All docs (`docs/*.md`, `README.md`, `AGENTS.md`, `CONTEXT.md`)

### What this audit checks

1. **Glossary compliance** — every use of a defined term matches
   CONTEXT.md. Every "Avoid" term is flagged as a violation.
2. **Voice consistency** — imperative second-person in agent-facing files.
   No passive voice. No hedging (consider, perhaps, might, may be useful).
3. **Prohibition style** — bold lowercase (`**never**`, `**do not**`)
   everywhere. No ALL CAPS prohibitions.
4. **Description format** — what + when, under 1024 chars, third person
   first sentence, trigger phrase second sentence.
5. **Cross-reference accuracy** — counts, version numbers, file paths,
   agent names all match reality.
6. **Reuse over duplication** — same concept explained in only one place,
   referenced everywhere else. No copy-paste between skills.
7. **Section ordering** — matches authoring guide template across all skills.

### Output

The QA agent produces a single report: `v3uplift/QA_REPORT.md` with:
- PASS / FAIL per check category
- Specific violations with file path, line, and fix instruction
- Summary count: total violations, critical vs cosmetic

### Gate

Phase 5 does not begin until QA_REPORT shows zero critical violations.
Cosmetic violations may be accepted with documented reasoning.

---

## Phase 5 — Release

### 5A. CHANGELOG update

Add 3.0.0 entry to `docs/CHANGELOG.md`:
- Skill authoring guide
- Domain glossary (CONTEXT.md)
- Hard/soft dependency ADR
- All 13 skills audited and rewritten
- Voice unification across docs, instructions, agent bodies
- Breaking: prohibition style standardised (bold lowercase)
- Breaking: skill section order standardised

### 5B. Version references

Update version references across the repo to 3.0.0.

### 5C. Final validation

Repeat Phase 4 in full. All checks must pass.

### 5D. Commit and tag

- Single squash commit or conventional-commit series.
- Tag: `agent-homebase@3.0.0`.

---

## Execution Order

```
Phase 0  Baseline capture and branch
Phase 1A Skill authoring guide         ← draft in v3uplift/drafts/
Phase 1B Domain glossary               ← draft in v3uplift/drafts/
Phase 1C Hard/soft dependency ADR      ← draft in v3uplift/drafts/
         ↓ Review drafts against each other for consistency
Phase 1  Promote drafts to repo
         ↓ Build + test gate
Phase 2  Skill audit (13 skills, one at a time)
         ↓ Build + test gate after each skill
Phase 3  Voice unification pass
         ↓ Build + test gate
Phase 4  Full validation suite
Phase 5  Release
```

**Exit criteria per gate:**
- `init.py` builds clean.
- `pytest` passes (≥233 tests, 0 failures).
- Resolved output is deterministic.

---

## Staging Convention

- Drafts land in `v3uplift/drafts/` first.
- Each draft gets reviewed against the authoring guide before promotion.
- Promoted files move to their final paths in the repo.
- `v3uplift/drafts/` is empty when the phase is complete.
- `v3uplift/PLAN.md` is the single source of truth for progress.
  Mark each checkbox as work proceeds.
