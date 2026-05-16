# v3 Uplift — QA Audit Prompt

Use this prompt verbatim in a new agent session. The agent has no prior
context — it reads the repo cold and reports findings.

---

## Prompt (copy from here)

You are auditing the agent-homebase repository for tone, language, glossary
compliance, and internal consistency. You have NO prior context about this
repo. Read everything fresh.

### Your inputs

1. Read `CONTEXT.md` at the repo root. This is the domain glossary.
   Every term defined there is canonical. Every "Avoid" term is a violation
   if found in agent-facing files.

2. Read `docs/SKILL_AUTHORING_GUIDE.md`. This defines the rules for
   skill voice, section order, description format, length limits, and
   prohibition style.

3. Read all 13 skills in `skills/*/` — both the main `.skill.md` and
   any supporting files.

4. Read all agent bodies in `agents/*.body.md`.

5. Read all instructions in `instructions/**/*.instructions.md`.

6. Read user-facing docs: `README.md`, `AGENTS.md`, `docs/QUICKSTART.md`,
   `docs/ONBOARDING.md`, `docs/CUSTOMIZATION.md`, `docs/ARCHITECTURE.md`,
   `docs/EXTENSION_GUIDE.md`.

### Your checks

For every file, evaluate against these 7 categories. Log every violation.

**1. Glossary compliance**
- Every use of a CONTEXT.md term matches the defined meaning.
- No "Avoid" term appears where the canonical term should be used.
- Flag: term used with different meaning than glossary definition.

**2. Voice consistency**
- Agent-facing files (skills, agent bodies, instructions): imperative,
  second-person ("You are…", "You **never**…").
- No passive voice in agent-facing files.
- No hedging words: consider, perhaps, might, may be useful, it could be,
  you might want to, potentially.
- Docs may use second-person pedagogical voice but not passive.

**3. Prohibition style**
- Prohibitions use bold lowercase: `**never**`, `**do not**`.
- No ALL CAPS prohibitions (`DO NOT`, `NEVER`, `MUST NOT` in caps).
- Exception: section headings may use standard title case.

**4. Description format (skills only)**
- Under 1024 characters.
- First sentence: what the skill does (third person).
- Second/subsequent: "Use when [triggers]" or "Use after [condition]".
- Does not summarise the workflow (that's the body's job).

**5. Cross-reference accuracy**
- Agent/skill counts match actual count in repo.
- Version numbers are consistent (Python version, repo version).
- File paths referenced in docs actually exist.
- Agent names referenced in instructions/skills match `agents/` filenames.
- Shell commands use `python` (not `python3`).

**6. Reuse over duplication**
- Same concept defined in only ONE place.
- Other files reference it, not redefine it.
- Flag: identical or near-identical paragraphs across multiple files.
- Flag: rules stated in a skill that duplicate an instruction verbatim.

**7. Section ordering (skills only)**
- Matches authoring guide template order:
  Overview → When to Use → Core Constraints → Workflow → Output Contract →
  Common Rationalizations → Red Flags → Verification.
- Missing sections are noted.
- Extra sections are noted (not necessarily violations — just flagged).

### Your output

Write your full report to `v3uplift/QA_REPORT.md` with this structure:

```markdown
# v3 Uplift — Tone & Language QA Report

Date: [today]
Auditor: [agent session]
Files scanned: [count]

## Summary

| Category | Pass/Fail | Violations |
|----------|-----------|-----------|
| Glossary compliance | | |
| Voice consistency | | |
| Prohibition style | | |
| Description format | | |
| Cross-reference accuracy | | |
| Reuse over duplication | | |
| Section ordering | | |

**Total:** X violations (Y critical, Z cosmetic)

## Critical Violations

[Each with: file path, line number or section, what's wrong, exact fix]

## Cosmetic Violations

[Same format, lower priority]

## Observations

[Patterns noticed, systemic issues, recommendations]
```

### Classification

- **Critical:** Glossary "Avoid" term in agent-facing file, wrong count/version,
  passive voice in a skill, ALL CAPS prohibition, description over 1024 chars,
  duplicated rule that could diverge.
- **Cosmetic:** Slight hedging in a doc (not skill), minor section order
  deviation, "Avoid" term in a non-agent-facing doc, soft-dependency instruction
  that could reference glossary but doesn't.

### Rules for you

- Be exhaustive. Check every file.
- Be specific. Quote the violation. Give file path and section.
- Do NOT fix anything. Report only.
- Do NOT skip files because they "seem fine." Read them.
- If CONTEXT.md or SKILL_AUTHORING_GUIDE.md do not exist yet, report that
  as a blocking finding and stop.
