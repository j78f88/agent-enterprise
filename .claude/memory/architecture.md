---
name: Project Architecture
description: Core architectural patterns and decisions for this project — loaded by agents before making technical suggestions
type: reference
---

# Architecture

<!-- Fill in the key architectural decisions and patterns for your project.
Agents like @reviewer, @architect, and @planner read this file to understand
what patterns to enforce and extend. The more specific this is, the better
the agents will align with your actual codebase. -->

## Core Patterns

- **Token-templated skills:** Skills are authored in `skills/` as `*.skill.md` with `{{token}}` placeholders. `init.py` resolves these against `project.config.yml` and writes deterministic output to `resolved/`.
- **Hybrid agent generation:** Agent wrappers use frontmatter from skill files + hand-crafted bodies from `agents/*.body.md`. Falls back to auto-extraction if no body file exists.
- **Never edit resolved/:** All output under `resolved/` is regenerated on every build. Source of truth is `skills/`, `instructions/`, `agents/`, and `config/`.
- **Security-first config:** `init.py` runs security validation on every config value (command whitelist, path traversal checks) before token substitution.
- **Frontmatter protocol-v1:** Every source file has YAML frontmatter with `id`, `kind`, `version`, `applies_to` fields validated at build time.
- **Dual-platform delivery:** Generates VS Code `.agent.md` wrappers AND Claude Code skill files from the same sources.

## Key Technologies

- Python 3.12+ (build system, tests)
- PyYAML for config parsing
- Pytest for test suite (393+ tests)
- No runtime dependencies beyond PyYAML — init.py is standalone

## Architecture Decisions

- ADR-0001: Hard vs soft instruction dependencies (see `docs/decisions/`)
- Body files are hand-crafted for quality over auto-extracted agent bodies
- `substitute()` intentionally skips tokens inside backtick code spans (treats them as documentation literals)
- Skills are the single source of truth; agent wrappers are derived artifacts
