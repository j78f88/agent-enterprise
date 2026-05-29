# Skill Authoring Guide

Rules for writing, reviewing, and maintaining skills in agent-enterprise.
Every skill under `skills/<name>/` follows these rules. No exceptions.

---

## Voice

Write skills as direct instructions to an agent. Address the agent in
second person, imperative mood: "You read diffs. You report findings.
You **never** modify code."

### Rules

1. Second-person imperative throughout. No passive voice.
2. No hedging words: ~~consider~~, ~~perhaps~~, ~~might want to~~,
   ~~it may be useful~~, ~~you could~~. State what to do.
3. Mark prohibitions in bold: **never**, **do not**. Not ALL CAPS.
4. One register. The skill reads as one author briefing a colleague —
   direct, confident, specific.

### Examples

| Wrong | Right |
|-------|-------|
| "You might want to check the tests." | "Run the tests. Report the exit code." |
| "Consider reviewing the diff." | "Read the diff. Flag violations." |
| "It may be useful to verify coverage." | "Verify coverage exceeds the threshold." |
| "DO NOT MODIFY CODE" | "You **never** modify code." |

### Prohibition Style in List Items

- **Skills** (prose): `**never** verb` — lowercase, keyword-only bold.
- **Agent bodies and instructions** (list items): `**Never** verb phrase`
  (capital N, full phrase bold) is acceptable at the start of list items.

---

## Description

The `description` field in frontmatter is the only text an agent sees
when deciding which skill to load. It must be sufficient for routing.

### Rules

1. Maximum 1024 characters.
2. First sentence: what the skill does (third person, present tense).
3. Second sentence: "Use when [trigger conditions]."
4. Include both what AND when. Do not summarise the workflow.
5. Do not repeat the skill name as the first word.

### Example

```yaml
description: >-
  Runs a WCAG 2.1 AA accessibility audit using automated tooling and
  manual checks. Use after touching UI components to scan key routes
  and check keyboard navigation, ARIA semantics, colour contrast, and
  screen reader behaviour.
```

---

## Frontmatter

Every skill file begins with YAML frontmatter conforming to
`schemas/frontmatter-v1.schema.json`. Required fields:

```yaml
---
id: skill.<name>           # globally unique, lowercase, dot-separated
kind: skill
version: 1.0.0             # file-level semver
applies_to: '**'           # path glob(s) where this skill is active
name: <name>
description: <see rules above>
when_to_use: <comma-separated trigger phrases>
user-invocable: true
inputs:
  type: object
  required: [task]
  properties:
    task:
      type: string
      description: What the skill should do.
outputs:
  - return_tier: <1|2|3>
verifier: null
agent:
  tools: [read, search]    # only capabilities the skill actually needs
  agents: []               # subagents this skill may dispatch
  model: null
  handoffs: []
---
```

Do not add fields absent from the schema. Do not omit required fields.

---

## Section Template

Every `SKILL.md` body follows this structure. Sections appear in this
order. Do not rename, reorder, or omit sections — downstream tooling
and reviews depend on the structure.

### 1. Title (H1)

```markdown
# <Role Title>
```

### 2. Opening Paragraph

One to two sentences. State the agent's role, mission, and hard boundary.
The opening paragraph is the skill's Overview — mandatory, 1–2 sentences,
elevator pitch. It has no heading of its own; it sits between the H1 title
and the `## When to Use` section.

```markdown
You are the code review specialist for {{project.name}}. You review
code for quality, pattern compliance, and tech debt. You **never**
modify code — you report findings only.
```

### 3. When to Use

Positive triggers and exclusions. This section is mandatory.

```markdown
## When to Use

Use this skill when:
- <trigger condition>
- <trigger condition>

**Do not** use this skill when:
- <exclusion — redirect to correct skill>
- <exclusion — redirect to correct skill>
```

### 4. Constraints

Hard rules the agent must obey. Bold all prohibitions.

The canonical heading is `## Constraints`. `## Core Constraints` is also
acceptable.

```markdown
## Constraints

- You **never** modify source code. You report only.
- You **do not** downgrade severity without new evidence.
- <additional hard rules>
```

### 5. Shared Rules

Cite instruction files and reference checklists this skill reads.
Shared Rules may appear before or after workflow sections — position
is flexible.

```markdown
## Shared Rules

This agent reads and follows:

- `{{paths.instructions_dir}}/severity-levels.instructions.md`
- `references/<relevant-checklist>.md`
```

### 6. Workflow

Numbered steps. Imperative. Specific commands and tool calls.

```markdown
## Workflow

1. Read the diff: `git diff <range>`.
2. Check each file against the security checklist.
3. Classify findings by severity.
4. Produce the report.
```

Every step starts with a verb. Every command is the actual command the
agent runs — not a paraphrase.

### 7. Output Contract

What the skill produces. Cite the return tier schema. The heading is
flexible — `## Report Format` or `## Machine-Readable Summary` are
acceptable alternatives depending on skill type.

```markdown
## Output Contract

Return a Tier 2 structured report:
- `summary`: one-line verdict
- `findings[]`: each with file, line, severity, description
- `status`: completed | blocked
```

### 8. Common Rationalizations

A table of excuses the agent might generate and why they fail.

```markdown
## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The test is flaky." | One failure is not proof of flakiness. Re-run and capture both results. |
| "It's just whitespace." | The pipeline is a contract. Run every gate. |
```

### 9. Red Flags

Observable signals that the skill execution went wrong.

```markdown
## Red Flags

- Claims of success without a cited command or file read.
- Severity softened without new evidence.
- Steps in the workflow silently skipped.
```

### 10. Verification

A checklist a reviewer uses to confirm correct execution. Every item
must be verifiable with evidence — no subjective judgements.

```markdown
## Verification

- [ ] Every command in the workflow has a captured exit code.
- [ ] Every finding cites file + line or command + output.
- [ ] No edits outside the skill's declared write surface.
```

---

## Writing Principles

Apply these when drafting or reviewing any skill content.

1. **Process over knowledge.** Skills are workflows the agent executes,
   not reference docs it reads for background. If a section does not
   drive action, extract it to a supporting file or delete it.

2. **Specific over general.** "Run `python -m pytest tests/ -v`" beats
   "run the tests." Name the command, the flag, the path.

3. **Evidence over assumption.** Every verification checkbox requires
   proof: an exit code, a file path, a line number. "Looks correct" is
   not evidence.

4. **Anti-rationalization.** Every step the agent might skip gets a
   matching row in Common Rationalizations. Anticipate laziness.

5. **Progressive disclosure.** `SKILL.md` is the entry point. Reference
   material belongs in supporting files within the skill directory or in
   `references/`. Do not inline lookup tables, checklists, or examples
   that exceed 20 lines.

6. **Token-conscious.** If removing a section would not change agent
   behaviour, remove the section. Every line costs context budget.

---

## Length Rules

- Target: under 200 lines per `SKILL.md`.
- Skills exceeding 200 lines must extract reference material into
  supporting files in the same skill directory (e.g.,
  `skills/security/threat-model-template.md`).
- The `SKILL.md` links to supporting files; it does not inline them.
- Supporting files have no frontmatter — they are not standalone skills.

---

## Extraction Criteria

Move content to a supporting file when:

- It is a lookup table, checklist, or template longer than 20 lines.
- It is reference material the agent consults but does not execute as
  workflow steps.
- It repeats across multiple skills (move to `references/` instead).

Keep content in `SKILL.md` when:

- It is a workflow step the agent executes.
- It is a constraint that gates behaviour.
- It is a rationalization or red flag (these are behavioural controls).

---

## Naming Conventions

| Artifact | Pattern | Example |
|----------|---------|---------|
| Skill directory | `skills/<name>/` | `skills/reviewer/` |
| Skill file | `<name>.skill.md` | `reviewer.skill.md` |
| Supporting file | descriptive kebab-case | `threat-model-template.md` |
| Frontmatter id | `skill.<name>` | `skill.reviewer` |

---

## QA Checklist

Use this checklist when reviewing any skill — new or rewritten.

- [ ] Frontmatter conforms to `schemas/frontmatter-v1.schema.json`.
- [ ] Description is under 1024 characters with what + when.
- [ ] All 10 sections present in correct order.
- [ ] "When to Use" includes both positive triggers and exclusions.
- [ ] Voice is second-person imperative throughout.
- [ ] No hedging words (consider, perhaps, might, could, may be useful).
- [ ] Prohibitions use bold, not ALL CAPS.
- [ ] Every workflow step starts with a verb and names the exact command.
- [ ] Every verification item is evidence-checkable.
- [ ] File is under 200 lines (or material is extracted with links).
- [ ] No unresolved `{{tokens}}` outside of backtick-wrapped documentation examples.
- [ ] Common Rationalizations table has at least 2 entries.
- [ ] Red Flags list has at least 3 entries.

---

## Relationship to EXTENSION_GUIDE.md

`docs/EXTENSION_GUIDE.md` covers how external projects consume and
extend agent-enterprise without forking. This guide covers how to author
skill content within agent-enterprise itself. The skill template section
in EXTENSION_GUIDE is superseded by this document — use this guide as
the authoritative reference for section structure and voice.
