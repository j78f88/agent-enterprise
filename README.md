# agent-homebase

A portable skills library for software delivery. Eleven agent skills covering product validation, sprint planning, execution, quality gates, and documentation — extracted from real delivery methodology and designed to work in any project via a single config file.

Works in **GitHub Copilot (VS Code)** and **Claude Code / Cowork** without modification.

---

## What's included

| Skill | Role |
|-------|------|
| `pm` | Validates features using a 5-test echo-chamber filter |
| `planner` | Scopes requirements and drafts sprint plans |
| `sprint-lead` | Orchestrates sprint execution end-to-end |
| `qa` | Runs typecheck, lint, tests, coverage, and E2E |
| `reviewer` | Reviews code for patterns, security, and quality |
| `architect` | Designs approaches and writes ADRs |
| `researcher` | Surfaces external patterns with citations and failure modes |
| `bug` | Captures bugs fast into a structured backlog |
| `docs` | Maintains all project documentation post-sprint |
| `a11y` | WCAG 2.1 AA accessibility audit |
| `perf` | Bundle size, build time, and dependency audit |

Plus 18 supporting instruction files covering governance, escalation, severity, commit conventions, retrospective format, and more.

---

## Quick start

```bash
# 1. Clone or install as a submodule
git submodule add https://github.com/j78f88/agent-homebase.git skills-library
cd skills-library

# 2. Copy and fill in the config
cp project.config.example.yml project.config.yml
# Edit project.config.yml with your paths, thresholds, and commands

# 3. Run substitution
python3 init.py --config project.config.yml

# 4. Copy output to your project
cp -r resolved/skills/* ../.github/agents/
cp -r resolved/instructions/* ../.github/instructions/

# 5. Copy starter planning files (first-time setup only)
cp starters/BACKLOG_LEDGER.md ../docs/planning/
cp starters/BUG_BACKLOG.md ../docs/planning/
cp starters/HANDOFF_REJECTIONS.md ../docs/planning/
cp starters/SPRINTS.md ../
cp starters/NON_GOALS.md ../docs/
cp starters/memory-architecture.md ../.claude/memory/architecture.md
cp starters/memory-conventions.md ../.claude/memory/conventions.md
```

See [ONBOARDING.md](ONBOARDING.md) for full step-by-step guidance.

---

## Profiles

Pre-filled configs for common project types in `profiles/`:

- `monorepo-fullstack.config.yml` — TypeScript monorepo (pnpm + Vite + Expo) — reference implementation
- `react-web-app.config.yml` — Single-package React + Vite app
- `python-api.config.yml` — Python API (FastAPI / Flask / Django)

---

## Upgrading

If installed as a submodule:

```bash
git submodule update --remote skills-library
cd skills-library
python3 init.py --config project.config.yml
cp -r resolved/skills/* ../.github/agents/
cp -r resolved/instructions/* ../.github/instructions/
```

---

## What's not included

`@delivery-lead` — the engagement orchestration layer — is intentionally excluded. It represents a personal workflow preference sitting on top of these skills. Consuming projects build their own version, or none at all.

---

## License

MIT
