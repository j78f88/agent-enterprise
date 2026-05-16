# Glossary

| Term | Definition |
|------|-----------|
| **agent-homebase** | This repo. The deployable library containing skills, instructions, profiles, and (post-restructure) the three delivery modes. |
| **Substrate** | Shared content used by all three modes: `skills/`, `instructions/`, `profiles/`, `starters/`, `schemas/`, `policies/`, `init.py`. Lives at homebase root. Not duplicated per mode. |
| **Delivery Mode** | A way of deploying agent-homebase. Three modes exist: Team, Orchestration, Choreography. Each lives in `delivery-modes/<mode>/`. |
| **Mode 1 / Team** | Single-repo deployment. Drops a 13-agent team into one project. Human-invoked. |
| **Mode 2 / Orchestration** | Single-project deployment with autonomous tracker-driven dispatch. Wraps Mode 1 with `@dispatcher` and `@verifier`. |
| **Mode 3 / Choreography** | Multi-project program-of-works deployment. A command-centre workspace coordinates N projects. |
| **Profile** | A YAML config (`profiles/*.config.yml`) that maps to a project archetype (react-web-app, python-api, monorepo-fullstack). Projects pick one and override values. |
| **Project Profile** | A specific project's `.agent-config/profile.yml` — token values for `init.py` substitution. |
| **Skill** | A `.skill.md` file in `skills/<name>/`. Canonical agent definition. |
| **Agent** | Thin VS Code wrapper (`.agent.md`) around a skill. |
| **Resolved Output** | `resolved/` folder produced by `init.py` — substrate with all `{{tokens}}` substituted from a project profile. |
| **Command Centre** | Two meanings: (1) the temporary `command centre/` folder in agent-homebase used as a workbench during this restructure; (2) the runtime workspace scaffolded by Mode 3 install. |
| **Workbench** | The `command centre/` folder. Holds specs, runbooks, decisions during restructure. Graduates contents to `delivery-modes/choreography/` in Phase 6. |
| **Registry** | `registry.yml` in a Mode 3 workspace. Lists all projects under choreography, their profiles, and deployment state. |
| **sync CLI** | The Mode 3 command-line tool: `deploy`, `diff`, `status`, `harvest`. Operates on the registry. |
| **Harvest** | Process of extracting mature patterns from a deployed project, diffing against substrate, identifying back-port candidates. |
| **Back-port** | Promoting an improvement from a project repo into the substrate so all projects can benefit. |
| **Graduation** | Phase 6 act of moving stable contents from `command centre/` into `delivery-modes/choreography/template/`. |
| **Absorption** | Phase 2 act of moving the `agent-orchestration` repo's contents into `delivery-modes/orchestration/`. |
| **Three-repo composition** | Old model (pre-restructure): homebase + agent-orchestration + project, overlaid at runtime via `afterCreate.sh`. Replaced in Mode 2 by single-repo composition (homebase + project). |
| **Meta-agent** | An agent in the Mode 3 workspace whose job is improving the framework itself (auditing, harvesting, writing tests for skills). Distinct from the 13 delivery agents. |
| **Dogfooding** | Using Mode 3 to do its own harvest work — `sync harvest verk-web` runs against Verk Web in Phase 4. |
| **Ghost-done** | Anti-pattern from `ANTI_FRAGILITY.md`: marking work Done without verifying artifacts exist. Prevented by `@verifier` in Mode 2/3. |
