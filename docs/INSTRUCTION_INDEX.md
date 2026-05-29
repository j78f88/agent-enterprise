# Instruction File Index

Master directory of all instruction files in agent-enterprise. Instructions are governance rules that agents read to maintain consistent behavior.

---

## Start Here

**New to agent-enterprise?** Read these 3 instructions first:

1. **[severity-levels.instructions.md](../instructions/configurable/severity-levels.instructions.md)** — How agents classify issues (CRITICAL/WARNING/SUGGESTION)
2. **[commit-conventions.instructions.md](../instructions/generic/commit-conventions.instructions.md)** — Git commit format all agents follow
3. **[subagent-return-schemas.instructions.md](../instructions/generic/subagent-return-schemas.instructions.md)** — How agents communicate (Tier 1/2/3 responses)

These three cover 80% of what you need to understand agent behavior.

---

## Overview

| Category | Count | Purpose |
|----------|-------|---------|
| **Generic** | 10 | Cross-project standards — apply to all projects |
| **Configurable** | 14 | Project-specific behavior — use `{{tokens}}` from config |
| **Total** | 24 | |

---

## Generic Instructions

Located in `instructions/generic/`. These enforce cross-project standards and don't require configuration.

| File | Required | Purpose | Used By |
|------|----------|---------|---------|
| `askquestions-contract.instructions.md` | ✅ | Defines `#tool:askQuestions` usage patterns for interactive decisions | All skills |
| `batch-report.instructions.md` | ○ | Format for multi-item status reports | @sprint-lead, @qa |
| `commit-conventions.instructions.md` | ✅ | Git commit message format and approval markers | All skills |
| `contract-change-checklist.instructions.md` | ○ | Process for modifying contracts/schemas | @architect |
| `determinism-guarantees.instructions.md` | ○ | Reproducibility requirements for replay | Phase 4 components |
| `fsm-orchestration.instructions.md` | ✅ | State machine workflow and transitions | @sprint-lead |
| `observability.instructions.md` | ○ | Logging, tracing, and metrics standards | All skills |
| `security-model.instructions.md` | ✅ | Security assessment, secret handling, audit | @reviewer, @security, init.py |
| `state-management.instructions.md` | ○ | State handling patterns and persistence | @sprint-lead |
| `subagent-return-schemas.instructions.md` | ✅ | Agent return value contracts (Tier 1/2/3) | All skills |

**Legend:** ✅ = Required for core functionality, ○ = Optional / phase-specific

---

## Configurable Instructions

Located in `instructions/configurable/`. These instructions contain template variables (e.g., `{{paths.backlog_ledger}}`, `{{quality.coverage_threshold}}`) that `init.py` replaces with project-specific values from your `project.config.yml`. This allows instructions to reference your actual file paths, commands, and thresholds without modification.

| File | Required | Purpose | Key Tokens Used |
|------|----------|---------|-----------------|
| `backlog-ledger.instructions.md` | ✅ | Backlog schema, governance, escalation rules | `paths.backlog_ledger`, `escalation.*` |
| `bug-backlog-format.instructions.md` | ✅ | Bug entry format and categorization | `paths.bug_backlog`, `ids.bug_prefix` |
| `composition-rules.instructions.md` | ✅ | Sprint composition constraints (feature/bug balance) | `escalation.feature_cap_percent` |
| `engagement-format.instructions.md` | ○ | Engagement tracking structure | `paths.engagements`, `ids.engagement_prefix` |
| `engagement-gates.instructions.md` | ○ | Stage gates and approval criteria | (none) |
| `handoff-rejection-format.instructions.md` | ○ | Rejection entry format | `paths.rejections`, `ids.rejection_prefix` |
| `non-goals-governance.instructions.md` | ○ | Non-goal tracking and rationale | `paths.non_goals`, `team.cto_name` |
| `planning-compliance.instructions.md` | ✅ | Sprint planning rules and validation | `paths.sprints`, `commands.*` |
| `planning-preflight.instructions.md` | ✅ | Pre-sprint validation checklist | `quality.*`, `platform.*` |
| `retro-report.instructions.md` | ✅ | Retrospective format, metrics, process ledger | `paths.sprints` |
| `severity-levels.instructions.md` | ✅ | Severity definitions (CRITICAL/WARNING/SUGGESTION) | (none) |
| `security-audit.instructions.md` | ○ | Security audit scheduling, changelog governance, hash registry, SBOM governance, license compliance, remediation decision tree, git history baseline | `paths.security_*`, `paths.sbom_output`, `security.*`, `commands.sbom_generate`, `commands.sast`, `commands.secret_scan_history`, `commands.license_check`, `commands.container_scan`, `commands.iac_scan` |
| `sprint-docs-format.instructions.md` | ✅ | PLAN.md structure and quality gates | `paths.sprints`, `paths.sprints_doc` |
| `validation-framework.instructions.md` | ○ | Quality validation rules and thresholds | `quality.*` |

---

## Instruction Categories

### Planning & Backlog

Instructions that govern sprint planning and backlog management:

- `backlog-ledger.instructions.md` — Single source of truth for all backlog items
- `bug-backlog-format.instructions.md` — Bug reproduction context and categorization
- `composition-rules.instructions.md` — Feature/bug balance, priority ordering
- `planning-compliance.instructions.md` — Sprint planning validation
- `planning-preflight.instructions.md` — Pre-sprint checklist
- `sprint-docs-format.instructions.md` — PLAN.md and RETRO.md structure

### Quality & Validation

Instructions that govern quality gates and validation:

- `severity-levels.instructions.md` — CRITICAL/WARNING/SUGGESTION definitions
- `validation-framework.instructions.md` — Quality thresholds and gates
- `subagent-return-schemas.instructions.md` — Agent return contracts

### Process & Workflow

Instructions that govern execution flow:

- `fsm-orchestration.instructions.md` — State machine workflow
- `askquestions-contract.instructions.md` — Interactive decision UI
- `engagement-format.instructions.md` — Engagement tracking
- `engagement-gates.instructions.md` — Approval gates

### Documentation & Reporting

Instructions that govern documentation:

- `retro-report.instructions.md` — Retrospective format
- `batch-report.instructions.md` — Multi-item reports
- `commit-conventions.instructions.md` — Commit messages
- `handoff-rejection-format.instructions.md` — Rejection tracking
- `non-goals-governance.instructions.md` — Non-goal rationale

### Technical Standards

Instructions that govern technical implementation:

- `security-model.instructions.md` — Security requirements
- `security-audit.instructions.md` — Security audit procedures, scheduling, changelog governance
- `state-management.instructions.md` — State persistence
- `determinism-guarantees.instructions.md` — Replay requirements
- `observability.instructions.md` — Logging and tracing
- `contract-change-checklist.instructions.md` — Schema changes

---

## How Instructions Load

1. **Skill frontmatter** lists which instructions the skill reads under "Shared Rules"
2. When the skill runs, it follows all listed instruction files
3. Instructions enforce consistent behavior across skills

Example from `@sprint-lead`:
```yaml
Shared Rules:
- {{paths.instructions_dir}}/severity-levels.instructions.md
- {{paths.instructions_dir}}/sprint-docs-format.instructions.md
- {{paths.instructions_dir}}/backlog-ledger.instructions.md
```

---

## Adding Custom Instructions

See [CONTRIBUTING.md](CONTRIBUTING.md) for the instruction creation guide. Custom instructions should:

1. Use YAML frontmatter: `name`, `description`, `when_to_use`, `applyTo`
2. Be placed in `instructions/configurable/` if using tokens
3. Be placed in `instructions/generic/` if project-agnostic
4. Be listed in skill frontmatter to take effect

---

## Cross-References

- [SKILL_FLOW.md](SKILL_FLOW.md) — How skills use these instructions
- [ARCHITECTURE.md](ARCHITECTURE.md) — Why this structure exists
- [ONBOARDING.md](ONBOARDING.md) — How to set up instructions in your project
