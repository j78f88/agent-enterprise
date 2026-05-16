# CLAUDE.md

Claude Code: read [AGENTS.md](AGENTS.md) first. It is the single source of
truth for setup, build, test, architecture, and PR conventions in this repo.

## Claude Code-specific notes

- Regenerate deployable artifacts with:
  `python init.py --config config/project.config.example.yml`
- **Never edit anything under `resolved/` directly.** It is build output;
  edits will be overwritten the next time `init.py` runs. Change the
  source under `skills/`, `instructions/`, or `agents/` instead.
- When in doubt about a skill's contract, prefer the source `*.skill.md`
  over the resolved `SKILL.md`.
