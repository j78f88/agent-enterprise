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
cp config/project.config.example.yml project.config.yml
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

See [docs/ONBOARDING.md](docs/ONBOARDING.md) for full step-by-step guidance.

---

## Project Structure

```
agent-homebase/
├── src/                          # Source code (multi-phase architecture)
│   ├── phase1_verification/      # Formal verification (schemas, policies)
│   ├── phase2_durability/        # Durable execution (SQLite, checkpoints)
│   ├── phase3_isolation/         # Sandboxing & isolation (Docker, capabilities)
│   └── phase4_determinism/       # Determinism & replay (logical time, versioning)
├── docs/                         # Documentation and implementation guides
├── config/                       # Configuration templates
├── tests/                        # Integration tests
├── instructions/                 # Governance and workflow instructions
├── skills/                       # Agent skill definitions
├── profiles/                     # Pre-configured project templates
├── schemas/                      # JSON schemas for validation
├── policies/                     # Rego policy files
└── starters/                     # Starter files for new projects
```

See [docs/PHASE_4_IMPLEMENTATION_SUMMARY.md](docs/PHASE_4_IMPLEMENTATION_SUMMARY.md) for architecture details.

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

## Documentation

| Guide | Description |
|-------|-------------|
| [ONBOARDING.md](docs/ONBOARDING.md) | Step-by-step setup guide |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues and solutions |
| [SKILL_FLOW.md](docs/SKILL_FLOW.md) | Skill execution diagrams and FSM states |
| [INSTRUCTION_INDEX.md](docs/INSTRUCTION_INDEX.md) | Master index of all 23 instruction files |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Design decisions and rationale |
| [CONTRIBUTING.md](docs/CONTRIBUTING.md) | How to add skills and instructions |

### Phase Guides

| Guide | Description |
|-------|-------------|
| [DETERMINISM_GUIDE.md](docs/DETERMINISM_GUIDE.md) | Lamport timestamps, prompt versioning, replay |
| [CHECKPOINT_GUIDE.md](docs/CHECKPOINT_GUIDE.md) | Checkpoint-restart system |
| [SANDBOX_GUIDE.md](docs/SANDBOX_GUIDE.md) | Container isolation and capabilities |
| [MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md) | Markdown to SQLite migration |

### Examples

| File | Description |
|------|-------------|
| [EXAMPLE_PROJECT_CONFIG.yml](docs/EXAMPLE_PROJECT_CONFIG.yml) | Filled-in config example |
| [EXAMPLE_SPRINT_FLOW.md](docs/EXAMPLE_SPRINT_FLOW.md) | Complete sprint walkthrough |
| [EXAMPLE_SKILL_OUTPUTS.md](docs/EXAMPLE_SKILL_OUTPUTS.md) | Sample return values per tier |

---

## What's not included

`@delivery-lead` — the engagement orchestration layer — is intentionally excluded. It represents a personal workflow preference sitting on top of these skills. Consuming projects build their own version, or none at all.

---

## License

MIT
