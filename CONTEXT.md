# CONTEXT.md — Domain Glossary

Canonical definitions for every domain term used in agent-homebase.
When writing skills, instructions, agents, or docs, use these terms
exactly as defined here. When a term has an "Avoid" entry, do not use
that word in agent-facing files.

---

## Core Concepts

| Term | Definition | Lives in | Avoid |
|------|-----------|----------|-------|
| **Skill** | A reusable workflow loaded by an agent at invocation time. Contains frontmatter, constraints, numbered steps, and verification criteria. One skill per directory. | `skills/<name>/<name>.skill.md` | "plugin" (implies runtime extension), "tool" (refers to agent capabilities like read/search/execute) |
| **Instruction** | A shared rule loaded by file-pattern match. Applies to any agent whose context includes matching files. Composes automatically — multiple instructions stack. | `instructions/generic/` or `instructions/configurable/` | "policy" (too formal), "config" (too vague), "rule file" |
| **Agent body** | The persona wrapper that gives an agent its role, constraints, and skill bindings. Defines what the agent is, not what it does step-by-step (that's the skill). | `agents/<name>.body.md` | "agent definition" (ambiguous with resolved output), "persona file" |
| **Resolved** | Build output produced by `init.py`. Token-substituted, ready to deploy into a consumer project. Read-only — never edit by hand. | `resolved/` | "deployed" (implies runtime), "compiled" (implies binary), "generated" (too generic) |
| **Token** | A `{{placeholder}}` in a source file, replaced at build time with a value from project config. Tokens in backticks are documentation and pass through unchanged. | Source files in `skills/`, `instructions/configurable/`, `agents/` | "variable" (too generic), "parameter" (implies runtime) |
| **Profile** | A pre-built project config for a common stack. Maps token names to values appropriate for that stack. | `profiles/` | "template" (overloaded — used for sprint plan templates, file templates) |
| **Substrate** | The agent-homebase repo itself — the authoring and build layer that produces resolved artifacts for consumer projects. | Repository root | "framework" (implies runtime), "platform" (implies hosting) |

---

## Orchestration

| Term | Definition | Avoid |
|------|-----------|-------|
| **Mode** | An orchestration pattern describing how agents coordinate. Mode 1 = team (direct invocation). Mode 2 = orchestration (file-queue dispatch). Mode 3 = choreography (registry-based multi-project). | "level" (refers to severity or complexity), "tier" (refers to return schemas) |
| **Sprint** | A bounded unit of work with a plan, execution phase, quality gates, and retrospective. Orchestrated by `@sprint-lead`. | "iteration" (too Agile-generic), "cycle" |
| **Subagent** | An agent invoked by another agent (the caller) with isolated context. Returns structured data per its write permit. | "child agent", "nested agent" |
| **Callable** | Any unit of work that can be dispatched by Mode 2 orchestration — a skill, prompt file, MCP tool, or external process. Declares inputs, outputs, and a verifier. | "task" (too generic), "job" |
| **Handoff** | The structured transfer of work from one agent to another with explicit context, constraints, and acceptance criteria. | "delegation" (implies hierarchy) |
| **Dispatch** | The act of routing a unit of work to a callable based on classification rules. Belongs in the orchestration layer, not in agent-homebase. | "assignment" (implies human manager) |

---

## Build System

| Term | Definition | Avoid |
|------|-----------|-------|
| **init.py** | The single build script. Validates security, resolves tokens, produces resolved output, and generates agent wrappers. Source of truth for the build. | "compiler", "generator", "bundler" |
| **Frontmatter** | YAML metadata block at the top of every substrate file. Schema: `schemas/frontmatter-v1.schema.json`. Required fields: `id`, `kind`, `version`, `applies_to`. | "header", "metadata block" (be specific — say "frontmatter") |
| **Security validation** | Build-time check that config values do not contain command injection, path traversal, or unsafe patterns. Runs before token resolution. | "sanitization" (implies runtime) |
| **Token resolution** | The build step that replaces `{{placeholders}}` with config values. Runs after security validation. | "interpolation" (too technical), "expansion" |

---

## Governance

| Term | Definition | Avoid |
|------|-----------|-------|
| **Promotion** | Moving a pattern from a consumer project into the substrate after governance review. Requires: generic, reused/reusable, stable for N cycles. | "merge" (too git-specific), "upstream" (directional ambiguity) |
| **Return tier** | Structured JSON output shape required from callables. Tier 1 = minimal (status + artifacts). Tier 2 = standard (adds verifier output, findings). Tier 3 = composition (adds sprint-level metadata). | "mode" (different concept), "level" |
| **Write permit** | A token included in a subagent prompt that declares which output paths the subagent may write to. Violations are rejection-worthy. | "permission" (too generic), "scope" (overloaded) |
| **Gate** | A quality checkpoint that must pass before sprint advancement. Gates are run by specialist agents (`@qa`, `@reviewer`, `@a11y`, `@perf`, `@security`). | "check" (too informal for the blocking semantics) |
| **Severity** | Finding classification: CRITICAL (blocks gate), WARNING (logged, non-blocking), SUGGESTION (optional). Defined in `severity-levels.instructions.md`. | "priority" (different axis — P0–P6 is priority) |
| **Priority** | Composition-time ranking of backlog items: P0 (mandatory) through P6 (cosmetic). Computed fresh each composition cycle from ledger attributes. | "severity" (different axis — CRITICAL/WARNING/SUGGESTION is severity) |

---

## Artifacts

| Term | Definition | Avoid |
|------|-----------|-------|
| **Backlog ledger** | The single source of truth for item status. 10-column table tracking ID, type, source, age, deferrals, sprint, status, blocked-by, draft link, and notes. | "tracker" (implies external tool), "task list" |
| **Bug backlog** | Detail store for bug reproduction context. Status is tracked in the ledger, not here. | "issue list", "bug tracker" |
| **Rejection log** | Detail store for handoff rejections between agents. Records why a handoff failed and what the upstream agent should do. Status tracked in ledger. | "error log" |
| **Validation record** | Output of the 5-test echo-chamber filter applied to feature recommendations before planning. Labels: VALIDATED, REFRAMED, NEW, REJECTED, DEFERRED. | "approval" (validation is evidence-based, not authority-based) |
| **ADR** | Architecture Decision Record. Documents a design choice with context, decision, and consequences. Immutable once merged — supersede with a new ADR, do not edit. | "design doc" (too vague) |
| **Non-goals** | Explicit list of things the project will not do. Owned by `@planner`. Modification requires user approval. Conflicts must be flagged, not worked around. | "out of scope" (too temporary — non-goals are standing decisions) |
| **Sprint report** | The final artifact of a sprint: summary, task outcomes, gate results, metrics, and retrospective seed. | "status update", "progress report" |
| **Retrospective** | Post-sprint analysis comparing forecast complexity against actual complexity. Captures lessons and calibrates future estimates. | "post-mortem" (implies failure) |

---

## Agent Roles

| Agent | Role | Write Surface |
|-------|------|--------------|
| `@sprint-lead` | Thin orchestrator. Reads plans, delegates to subagents, collects results, produces sprint report. | Sprint report, RETRO.md seed |
| `@planner` | Scopes requirements, drafts sprint plans, manages backlog ledger and non-goals. | Plans, ledger, non-goals, drafts |
| `@pm` | Validates features using the 5-test framework. Kill/keep decisions. | Validation records |
| `@researcher` | Surfaces external evidence. Cites sources, quantifies adoption, includes failure modes. | Research docs |
| `@architect` | Designs approaches, writes ADRs. Pressure-tests before planning. | ADR drafts, architecture docs |
| `@reviewer` | Reviews code for pattern compliance, security, quality. Reports findings. | None (read-only) |
| `@qa` | Runs full quality pipeline: typecheck, lint, tests, coverage, E2E. | None (read-only, reports only) |
| `@security` | Audits codebase for vulnerabilities. Manages security changelog and file integrity. | Security docs only |
| `@a11y` | WCAG 2.1 AA accessibility audit. Automated + manual checks. | None (read-only) |
| `@perf` | Audits bundle size, build time, dependency health. | None (read-only) |
| `@bug` | Captures bugs to bug backlog with sequential ID, severity, and repro steps. | Bug backlog entries, ledger entries |
| `@docs` | Generates/maintains all project documentation after a sprint. | Documentation files |
| `@onboarding` | Guides first-time setup. Self-removes after completion. | Config files, seeded docs |

---

## Protocol Terms

| Term | Definition |
|------|-----------|
| **Protocol version** | `protocol-vN`. Bumps only on breaking changes to files under `command-centre/01-protocols/`. |
| **Contract tag** | A stable identifier for a specific contract (e.g., `callable-contract-v1`, `frontmatter-v1`). Referenced by implementations. |
| **FSM** | Finite State Machine defining sprint orchestration states and transitions. Ensures deterministic state progression. |
| **Checkpoint** | A saved FSM state that enables resume after interruption. Contains full state context. |
| **Hash chain** | Cryptographic chain linking sequential artifacts (sprints, reports) for tamper detection. |
| **Determinism** | Same inputs produce same outputs. Enforced by: `temperature=0.0`, logical time, seeded randomness, versioned prompts. |

---

## Instruction Categories

| Category | Location | Token dependency | Behaviour without config |
|----------|----------|-----------------|--------------------------|
| **Generic** | `instructions/generic/` | None | Fully functional |
| **Configurable** | `instructions/configurable/` | Requires `{{tokens}}` from project config | Broken — unresolved placeholders |

---

## Flagged Ambiguities

Terms that have caused confusion or have overlapping usage:

| Term | Ambiguity | Resolution |
|------|-----------|------------|
| **scope** | Used as (1) frontmatter field alias for `applies_to`, (2) "sprint scope" meaning planned work, (3) "write scope" meaning permitted output paths. | Frontmatter: use `applies_to` (deprecated alias sunsets at frontmatter-v2). Sprint: say "sprint plan" or "planned work." Write: say "write surface" or "write permit." |
| **template** | Used as (1) sprint plan template, (2) profile template, (3) token template (source file with placeholders). | Sprint: "plan template." Profile: say "profile." Token: say "source file" or "template file" only in build-system context. |
| **agent** | Used as (1) the runtime entity that executes, (2) the `.body.md` authoring file, (3) the resolved `.agent.md` output. | Runtime entity: "agent." Authoring file: "agent body." Resolved output: "resolved agent wrapper." |
| **contract** | Used as (1) protocol-level callable contract, (2) honesty contract (behavioural rules), (3) output contract (what a skill produces). | Always qualify: "callable contract," "honesty contract," "output contract." Never use bare "contract" without a qualifier. |
| **gate** | Used as (1) quality gate (specialist agent check), (2) engagement gate (Gate 1–4 lifecycle checkpoints). | Quality: "quality gate" or just "gate" in sprint context. Engagement: always say "engagement gate" or "Gate N." |
| **finding** | Used as (1) reviewer/security/a11y output (severity-classified), (2) audit finding (backlog item type). | Severity-classified output: "finding" with severity. Backlog: "audit-finding" (hyphenated, as the ledger type value). |
| **draft** | Used as (1) sprint plan draft in `docs/planning/drafts/`, (2) ledger Draft column (link to plan), (3) staging area for v3uplift. | Plan draft: "draft plan." Ledger: "draft link." Staging: "staged draft." |
