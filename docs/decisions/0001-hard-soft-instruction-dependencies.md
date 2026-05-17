# ADR-0001: Hard and Soft Instruction Dependencies

**Status:** Accepted
**Date:** 2026-05-16
**Context:** v3 uplift — classify instruction dependencies to enforce correct consumption.

---

## Context

agent-homebase ships instructions in two directories:

- `instructions/generic/` — 11 files
- `instructions/configurable/` — 14 files

The split exists but the distinction is implicit. Consumers and skill
authors have no formal rule for when an instruction requires project
config versus when it works standalone. This ADR makes the contract
explicit.

---

## Decision

Classify every instruction as either a **hard dependency** or a
**soft dependency** based on token usage.

### Hard dependency (configurable)

The instruction contains `{{token}}` placeholders that require
project-specific values from a config file. Without resolution:

- Output contains literal `{{placeholder}}` strings.
- Agent behaviour is wrong — paths, thresholds, and IDs are missing.
- The instruction is non-functional until `init.py` runs.

**Rule:** Every hard-dependency instruction must include this notice
in its opening paragraph or frontmatter description:

> Requires project config. Run `init.py` with your profile if tokens
> are unresolved.

### Soft dependency (generic)

The instruction works without any project config. It references no
tokens. Output is fully correct for any project consuming
agent-homebase.

**Rule:** Soft-dependency instructions reference "the project's
conventions" in general prose only. They never assume specific paths,
IDs, or thresholds.

---

## Classification

### Soft Dependencies — `instructions/generic/` (11 files)

All verified to contain zero `{{token}}` references.

| File | Purpose | Token count | Notes |
|------|---------|-------------|-------|
| `askquestions-contract.instructions.md` | Rules for using the askQuestions tool | 0 | Behavioural contract — works universally |
| `batch-report.instructions.md` | Save-by-default rules for non-destructive artifacts | 0 | References path patterns but as prose, not tokens |
| `commit-conventions.instructions.md` | Commit message format rules | 0 | Conventional Commits — project-agnostic |
| `contract-change-checklist.instructions.md` | Pre-commit checklist for contract edits | 0 | References file types, not specific paths |
| `determinism-guarantees.instructions.md` | Reproducible execution principles | 0 | Aspirational architecture — no runtime config |
| `fsm-orchestration.instructions.md` | Sprint orchestration state machine | 0 | Defines states and transitions generically |
| `honesty-contract.instructions.md` | Hard rules against fabrication | 0 | Universal behavioural rules |
| `observability.instructions.md` | Tracing and instrumentation design | 0 | Architecture spec — no project-specific values |
| `security-model.instructions.md` | Threat model and security hardening | 0 | Defines defences generically |
| `state-management.instructions.md` | ACID guarantees and checkpoint design | 0 | Architecture spec — no project-specific values |
| `subagent-return-schemas.instructions.md` | Return tier definitions and write permits | 0 | Protocol definitions — project-agnostic |

### Hard Dependencies — `instructions/configurable/` (14 files)

All verified to contain one or more `{{token}}` references.

| File | Purpose | Key tokens | Why hard |
|------|---------|-----------|----------|
| `backlog-ledger.instructions.md` | Ledger schema and governance | `{{ids.item_prefix}}`, `{{paths.backlog_ledger}}`, `{{escalation.*}}` | IDs, paths, and escalation thresholds are project-specific |
| `bug-backlog-format.instructions.md` | Bug entry schema | `{{ids.bug_prefix}}`, `{{paths.bug_backlog}}` | Bug ID prefix and file path are project-specific |
| `composition-rules.instructions.md` | Sprint composition priority and scoring | `{{escalation.*}}`, `{{paths.validation}}` | Thresholds and capacity limits vary per project |
| `engagement-format.instructions.md` | Engagement entry schema | `{{ids.engagement_prefix}}`, `{{paths.engagements}}` | ID prefix and path are project-specific |
| `engagement-gates.instructions.md` | Gate 1–4 lifecycle definitions | `{{git.*}}`, `{{paths.*}}`, `{{platform.*}}`, `{{scope_upgrade.*}}` | Branch names, paths, CI config, upgrade thresholds all vary |
| `handoff-rejection-format.instructions.md` | Rejection entry schema | `{{ids.rejection_prefix}}`, `{{paths.rejections}}` | ID prefix and path are project-specific |
| `non-goals-governance.instructions.md` | Non-goals ownership and enforcement | `{{paths.non_goals}}`, `{{paths.decisions}}`, `{{team.cto_name}}` | Path and approver name are project-specific |
| `planning-compliance.instructions.md` | Plan draft validation rules | `{{paths.drafts}}`, `{{quality.*}}` | Draft path and coverage thresholds vary |
| `planning-preflight.instructions.md` | Pre-flight document checklist | `{{paths.*}}` (9 distinct paths) | Every row references a project-specific path |
| `retro-report.instructions.md` | Retrospective schema and lifecycle | `{{paths.sprints}}` | Sprint directory path is project-specific |
| `security-audit.instructions.md` | Security scan workflow | `{{paths.*}}`, `{{security.*}}`, `{{git.main_branch}}` | Paths, licence lists, tracked files, branch all vary |
| `severity-levels.instructions.md` | Finding severity definitions | `{{paths.*}}`, `{{quality.*}}` | Thresholds and paths are project-specific |
| `sprint-docs-format.instructions.md` | Sprint document structure | `{{commands.test}}`, `{{paths.*}}` (10 paths) | Commands and paths are deeply project-specific |
| `validation-framework.instructions.md` | 5-test feature validation | `{{paths.validation}}`, `{{paths.non_goals}}`, `{{paths.roadmap}}` | Output path and reference paths are project-specific |

---

## Verification

The classification is mechanically verifiable:

```powershell
# Confirm all generic files have zero tokens:
Get-ChildItem instructions/generic/ -File |
  Where-Object { (Get-Content $_.FullName -Raw) -match '\{\{[^}]+\}\}' } |
  ForEach-Object { Write-Host "VIOLATION: $($_.Name) has tokens" }

# Confirm all configurable files have at least one token:
Get-ChildItem instructions/configurable/ -File |
  Where-Object { (Get-Content $_.FullName -Raw) -notmatch '\{\{[^}]+\}\}' } |
  ForEach-Object { Write-Host "VIOLATION: $($_.Name) has no tokens" }
```

Both checks must produce no output. If a file moves between directories,
re-run verification.

---

## Consequences

1. **For skill authors:** When a skill references a configurable
   instruction in its Shared Rules section, the skill inherits a hard
   dependency on project config. Document this in the skill's frontmatter
   or opening paragraph.

2. **For consumer projects:** Generic instructions work immediately after
   copying `resolved/instructions/` into the project. Configurable
   instructions require running `init.py` with a project profile first.

3. **For the build system:** `init.py` already handles this correctly —
   it resolves tokens in configurable files and copies generic files
   unchanged. This ADR documents the existing behaviour as a contract.

4. **For future instructions:** Place new instructions in `generic/` only
   if they contain zero tokens. If any token is needed, use
   `configurable/`. There is no middle ground.
