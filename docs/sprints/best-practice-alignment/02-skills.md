# 02 — Skills Hardening: Anti-Rationalization, Red Flags, Verification

> **Depends on:** Ideally after `01-scaffolding` (so extension guide template reflects these sections)
> **Commit:** `feat(skills): add anti-rationalization, red flags, verification to all 13 skills`
> **Verify:** grep counts = 13 for each new section across skills/

---

## Task Group 1.4: Add anti-rationalization tables to all 13 skills

Files: `skills/a11y/a11y.skill.md`, `skills/architect/architect.skill.md`, `skills/bug/bug.skill.md`, `skills/docs/docs.skill.md`, `skills/onboarding/onboarding.skill.md`, `skills/perf/perf.skill.md`, `skills/planner/planner.skill.md`, `skills/pm/pm.skill.md`, `skills/qa/qa.skill.md`, `skills/researcher/researcher.skill.md`, `skills/reviewer/reviewer.skill.md`, `skills/security/security.skill.md`, `skills/sprint-lead/sprint-lead.skill.md`

**Why:** addyosmani/agent-skills pattern. Tables of common excuses agents use to skip steps, paired with counter-arguments.

- [ ] Append `## Common Rationalizations` section to each of 13 `.skill.md` files
- [ ] Use 3-column table format: Excuse | Why It's Tempting | Counter
- [ ] Each skill gets 3–5 domain-specific rationalizations:
  - **qa**: "Tests are passing, no need to check coverage", "This is a refactor so no new tests needed"
  - **architect**: "We can decide the architecture later", "This is obvious, no ADR needed"
  - **security**: "This is an internal tool, security doesn't matter", "We'll add auth later"
  - **planner**: "This is a small feature, no sprint plan needed"
  - **researcher**: "I already know the answer, no need to research"
  - **reviewer**: "It's a small change, no review needed"
  - **docs**: "The code is self-documenting"
  - **a11y**: "It's an internal tool, accessibility doesn't matter"
  - **perf**: "We can optimize later"
  - **bug**: "It's a minor bug, doesn't need reproduction steps"
  - **pm**: "Requirements are obvious, no spec needed"
  - **sprint-lead**: "We can skip the retro, nothing went wrong"
  - **onboarding**: "They'll figure it out"
- [ ] Verify: `grep -r "Common Rationalizations" skills/ | wc -l` → 13

---

## Task Group 1.5: Add Red Flags + Verification Gates to all 13 skills

Files: (same 13 skill files as above)

**Why:** Forces agents to produce concrete evidence before exiting a skill invocation.

- [ ] Append `## Red Flags` section (3+ domain-specific signs per skill) after Common Rationalizations
- [ ] Append `## Verification` section (3+ checklist items per skill) after Red Flags
- [ ] Domain-specific examples:
  - **qa**: "coverage decreased but not flagged", "tests mock everything, no integration tests"
  - **architect**: "ADR has no trade-off section", "no diagram for stateful interactions"
  - **security**: "no dependency scan ran", "secrets in env vars without vault reference"
  - **reviewer**: "PR approved with no comments on a 500-line diff"
  - **docs**: "README references files that don't exist"
  - **a11y**: "no keyboard navigation test", "color-only state indicators"
  - **perf**: "bundle size increased 20% with no justification"
  - **bug**: "root cause listed as 'unknown'", "no regression test added"
  - **pm**: "acceptance criteria are vague or unmeasurable"
  - **planner**: "no dependency graph", "no risk assessment"
  - **sprint-lead**: "tasks have no Files: annotations"
  - **researcher**: "all sources from same vendor"
  - **onboarding**: "setup instructions not tested on clean machine"
- [ ] Verify: `grep -r "## Red Flags" skills/ | wc -l` → 13
- [ ] Verify: `grep -r "## Verification" skills/ | wc -l` → 13

---

## Verification

```powershell
# Section counts
(Select-String -Path skills/*/*.skill.md -Pattern "## Common Rationalizations").Count  # 13
(Select-String -Path skills/*/*.skill.md -Pattern "## Red Flags").Count                # 13
(Select-String -Path skills/*/*.skill.md -Pattern "## Verification").Count             # 13

# init.py still resolves cleanly (skills aren't resolved, but agents reference them)
python init.py --config config/project.config.example.yml

# Tests still green
python -m pytest tests/ -v
```
