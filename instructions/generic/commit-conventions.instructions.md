---
id: instruction.commit-conventions
kind: instruction
version: 1.0.0
applies_to: .gitmessage, .github/**, docs/**
description: Conventional Commits format used by every agent and ad-hoc commit in this repo.
---

# Commit Conventions

Single source of truth for commit message format across all agents and ad-hoc sessions.

## Format

```
<type>: [Sprint N — ]<description>
```

Sprint prefix is included when the commit is part of a sprint.

## Types

| Type       | Use case                         |
| ---------- | -------------------------------- |
| `feat`     | New feature or capability        |
| `fix`      | Bug fix                          |
| `test`     | Adding or updating tests         |
| `docs`     | Documentation only               |
| `chore`    | Maintenance, config, build       |
| `refactor` | Code restructuring, no new behaviour |

## Sprint Conventions

- Kickoff: `docs: Sprint N — kick off`
- Completion: `docs: Sprint N — complete`
- Per-task: `feat: Sprint N — <description>` / `fix:` / `test:` as appropriate

## Non-Sprint Commits

`docs: <action>`, `fix: <action>` — no sprint number required.

## NON_GOALS.md Commits

Must include `(approved by <User> YYYY-MM-DD)` in the commit body. See `.github/instructions/non-goals-governance.instructions.md`.

## Tool Attribution Trailer

Every durable commit must carry a `Tool:` trailer naming the tool that authored
it (e.g. `Tool: claude-cli`, `Tool: vscode`). This makes authorship queryable by
tool without surfacing a personal identity. Ephemeral `wip`/`fixup!`/`squash!`
checkpoints are exempt. The `.gitmessage` template pre-fills the trailer; enable
it once per clone with `git config commit.template .gitmessage`. The
`.githooks/commit-msg` hook rejects durable commits that omit it.

```
feat(schemas): add registry-v1

Why this change is needed.

Tool: claude-cli
```

## Squashing

Each task is its own commit by default. Squash only on explicit user request.
