<!-- copilot-instructions.md — Platform entry point for GitHub Copilot.
     Copy this file to .github/copilot-instructions.md in your project. -->

<!-- If your project has AGENTS.md, point to it here. Otherwise, this file
     is your project's primary agent context. -->

Read [AGENTS.md](../AGENTS.md) first. It is the single source of truth for
setup, build, test, architecture, and PR conventions in this repo.

## Copilot-specific notes

- Regenerate deployable artifacts with:
  `python init.py --config config/project.config.example.yml`
- **Never edit anything under `resolved/` directly.** It is build output;
  edits will be overwritten the next time `init.py` runs. Change the
  source under `skills/`, `instructions/`, or `agents/` instead.
- When in doubt about a skill's contract, prefer the source `*.skill.md`
  over the resolved `SKILL.md`.

## What this project is

<!-- Replace with a 1-2 sentence description of your project. -->

## Key directories

<!-- List the directories most relevant to day-to-day development.
     Example:
     | Path | Purpose |
     | --- | --- |
     | `src/` | Application source code |
     | `tests/` | Test suite |
-->

## Technology stack

<!-- List primary languages, frameworks, and infrastructure.
     Example: Python 3.12, FastAPI, PostgreSQL, Azure Container Apps -->

## Agent routing notes

<!-- Document any agent-specific routing or preferences.
     Example: Use @reviewer for all PR reviews. Use @architect for
     design decisions. -->
