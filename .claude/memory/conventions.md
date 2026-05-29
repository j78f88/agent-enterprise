---
name: Project Conventions
description: Coding conventions and style rules for this project — loaded by agents before reviewing or generating code
type: reference
---

# Conventions

<!-- Fill in the coding conventions specific to your project.
@reviewer uses this to enforce project-specific patterns.
@architect uses this to extend rather than break existing conventions. -->

## Code Style

- Python 3.12+ — use modern syntax (match/case, type hints, f-strings)
- No external dependencies in `init.py` beyond PyYAML — it must stay standalone
- `src/` contains a standalone phase library (not imported by init.py)
- Skill files use Markdown with YAML frontmatter — no HTML unless necessary

## Testing Conventions

- Pytest with `tests/` directory, run via `python -m pytest tests/ -v`
- Set `$env:PYTHONIOENCODING='utf-8'` before running tests on Windows
- Tests validate token resolution, security checks, frontmatter parsing, and deterministic output
- 393+ tests must stay green before any PR

## Git Conventions

- Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`
- Main branch: `main`, integration branch: `develop`
- Never commit anything inside `resolved/` — it is build output
- Every PR must keep `python init.py` green and test suite green

## Naming Conventions

- Skills: `skills/<name>/<name>.skill.md`
- Agent bodies: `agents/<name>.body.md`
- Instructions (generic): `instructions/generic/<name>.instructions.md`
- Instructions (configurable): `instructions/configurable/<name>.instructions.md`
- Profiles: `profiles/<stack>.config.yml`
- Resolved output mirrors source structure under `resolved/`
