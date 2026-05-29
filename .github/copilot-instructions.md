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

agent-enterprise is a portable, multi-agent operating system for software projects. Skills, instructions, and agents live as plain Markdown, get resolved with project-specific tokens by `init.py`, and emit copy-ready artifacts for any compatible coding agent.

## Key directories

| Path | Purpose |
| --- | --- |
| `skills/` | Skill authoring sources (`*.skill.md`) |
| `instructions/` | Shared rules (generic + configurable) |
| `agents/` | Per-agent body wrappers (`*.body.md`) |
| `config/` | Project token configs |
| `tests/` | Pytest suite (393+ tests) |
| `src/` | Standalone Python phase library |
| `resolved/` | Build output — never edit by hand |

## Technology stack

Python 3.12+, PyYAML, Pytest

## Agent routing notes

- Use `@reviewer` for all code reviews
- Use `@architect` for design decisions and ADRs
- Use `@planner` for sprint planning
- Use `@sprint-lead` for execution orchestration
- Use `@security` for vulnerability scanning and audit
