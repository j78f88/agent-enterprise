# agent-homebase

**Portable, multi-agent operating system for software projects.**

[![CI](https://github.com/j78f88/agent-homebase/actions/workflows/ci.yml/badge.svg)](https://github.com/j78f88/agent-homebase/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Copilot](https://img.shields.io/badge/GitHub%20Copilot-Ready-blue?logo=github)](https://github.com/features/copilot)
[![Claude](https://img.shields.io/badge/Claude%20Code-Ready-orange)](https://claude.ai)

Skills, instructions, and agents authored once in plain Markdown,
resolved with project-specific tokens by `init.py`, and emitted as
copy-ready artifacts under `resolved/` for any compatible coding
agent (GitHub Copilot, Claude Code, Cursor, Codex).

`protocol-v1` ships **complete** at `2.0.0`: contracts are frozen and
backed by JSON Schemas, frontmatter validation, and at least one
reference implementation per mode.

---

## Who this is for

- **P1 — Framework owner** (REAL): you curate substrate for one or more
  teams.
- **P3 — Pro dev with AI** (PLAUSIBLE): you ship features faster with a
  Copilot/Claude assistant and want consistent rails.
- **P2 — Enterprise platform engineer** (ASPIRATIONAL) and
  **P4 — Outcome-driven builder** (DEFERRED): the contracts are designed
  for you; reference impls land when a real signal arrives.

See [docs/PERSONAS.md](docs/PERSONAS.md) for the full evidence-tagged
matrix.

---

## Quickstart

```powershell
git clone https://github.com/j78f88/agent-homebase.git
cd agent-homebase
pip install -r requirements.txt
python init.py --config profiles/python-api.config.yml
# → resolved/skills, resolved/instructions, resolved/agents
```

Full walkthrough: [docs/QUICKSTART.md](docs/QUICKSTART.md).
First-time setup: [docs/ONBOARDING.md](docs/ONBOARDING.md).

---

## What you get

### Three modes, three contracts

| Mode | What it is | Contract | Reference impl |
|------|------------|----------|----------------|
| **1 — Team** | Substrate + interactive use (`@planner`, `@qa`, `@security`, …) | [`mode-1-contract-v1`](command-centre/02-mode-team/contract.md) | This repo itself |
| **2 — Orchestration** | Dispatch a queue of work to callables; verify | [`mode-2-contract-v1`](command-centre/03-mode-orchestration/contract.md) | [`file-queue-dispatcher`](command-centre/03-mode-orchestration/reference-impls/file-queue-dispatcher/) |
| **3 — Choreography** | Coordinate a program of works across many projects | [`mode-3-contract-v1`](command-centre/04-mode-choreography/contract.md) | [`registry-coordinator`](command-centre/04-mode-choreography/reference-impls/registry-coordinator/) |

### Protocol-v1 schemas

Every substrate file is validated at build time:

| Schema | Validates |
|--------|-----------|
| [`schemas/frontmatter-v1.schema.json`](schemas/frontmatter-v1.schema.json) | YAML frontmatter on every skill, instruction, and agent |
| [`schemas/callable-v1.schema.json`](schemas/callable-v1.schema.json) | The callable manifest on every skill |
| [`schemas/project-v1.schema.json`](schemas/project-v1.schema.json) | A single project entry in a Mode-3 registry |
| [`schemas/registry-v1.schema.json`](schemas/registry-v1.schema.json) | A full Mode-3 choreography registry |

Plus the three subagent-return tiers under `schemas/subagent-return-tierN.schema.json`.

### Thirteen skills, thirteen agents

`@a11y`, `@architect`, `@bug`, `@docs`, `@onboarding`, `@perf`,
`@planner`, `@pm`, `@qa`, `@researcher`, `@reviewer`, `@security`,
`@sprint-lead` — each one is a skill source under `skills/` plus an
agent wrapper body under `agents/`. See [docs/PERSONAS.md](docs/PERSONAS.md)
and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for how they compose.

---

## Status

- **`protocol-v1`** — frozen at 2.0.0. Schemas enforced.
- **`mode-1-contract-v1`** — substrate-aligned; this repo conforms.
- **`mode-2-contract-v1`** — reference dispatcher present, conformance test green.
- **`mode-3-contract-v1`** — reference coordinator present, conformance test green.

---

## Architecture (1 minute)

```
skills/         author once, token-templated, callable-v1 manifests
instructions/   shared rules, generic + configurable
agents/         per-agent body that wraps a skill
schemas/        JSON Schemas that gate the build
config/         project-specific token values
profiles/       pre-built configs (python-api, react-web-app, monorepo-fullstack)
command-centre/ contracts (protocol-v1, mode contracts, ADRs, ref impls)
        │
        ▼  python init.py --config <profile>
resolved/       deploy artifacts (skills/, instructions/, agents/)
```

`init.py` is the single source of truth for the build. It runs
security validation, frontmatter validation (strict by default),
resolves `{{tokens}}`, and writes deterministic output.

`resolved/` is build output — never edit it directly, never commit it.

---

## Key directories

| Path | Purpose |
| --- | --- |
| `skills/` | Skill authoring sources (`*.skill.md`) with `callable-v1` manifests |
| `instructions/generic/` | Rules that apply to every project |
| `instructions/configurable/` | Rules that consume `{{tokens}}` |
| `agents/` | Per-agent body wrappers (`*.body.md`) |
| `command-centre/` | `protocol-v1` contracts, mode contracts, ADRs, reference impls |
| `schemas/` | JSON Schemas enforced at build time |
| `profiles/` | Pre-built configs for common stacks |
| `config/` | Your own project config (or pick a profile) |
| `tools/` | Helpers — including [`migrate-frontmatter.py`](tools/migrate-frontmatter.py) |
| `tests/` | Pytest suite (conformance included) |
| `resolved/` | **Build output. Never edit. Never commit.** |

---

## Contributing

- Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:` …).
- Every PR must keep `python init.py --config config/project.config.example.yml`
  green (strict frontmatter validation on by default) and the full
  test suite green.
- New skills follow [docs/EXTENSION_GUIDE.md](docs/EXTENSION_GUIDE.md)
  and MUST include a `callable-v1` manifest.
- Run `python tools/migrate-frontmatter.py` on legacy files to bring
  them into `frontmatter-v1` shape (idempotent).

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) and
[AGENTS.md](AGENTS.md) for the agent contract that every coding
assistant in this repo defers to.

---

## License

MIT — see [LICENSE](LICENSE).
