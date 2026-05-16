---
description: "Conventional Commits format used by every agent and ad-hoc commit in this repo."
scope: ".gitmessage, .github/**, docs/**"
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

## Squashing

Each task is its own commit by default. Squash only on explicit user request.
