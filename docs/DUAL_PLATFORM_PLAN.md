# Dual-Platform Plan: Skills + Optional Agent Generation

> **Status:** Implemented — Phases 1-7 complete
> **Date:** 2026-04-28
> **Scope:** Make agent-homebase service both VS Code (Copilot) and Claude Code users from a single source

---

## TL;DR

Keep skills as the canonical single-source-of-truth. Add a hybrid agent layer: `init.py` generates VS Code agent frontmatter from skill `agent:` metadata, while agent bodies are hand-crafted for quality. Claude Code users use skills directly. Users pick their platform at config time.

---

## Architecture

```
skills/                ← canonical source (both platforms)
  architect/SKILL.md
  qa/SKILL.md
  ...

resolved/              ← generated output
  skills/              ← always generated (works on both platforms)
  agents/              ← generated only when editor.target includes "vscode"
  instructions/        ← always generated
```

**Key insight:** An agent wrapper is a thin shell (frontmatter + persona + constraints) that *references* the skill's procedures. The skill stays the knowledge base; the agent adds enforcement boundaries.

**Key insight:** Skills and agents aren't either/or — they serve different roles. Agent = judgment and restriction. Skill = execution and procedure. The hybrid pattern (agent delegates to skill) is strongest.

---

## Platform Comparison

| Capability | Claude Code (skills only) | VS Code (agents + skills) |
|-----------|---------------------------|---------------------------|
| Skill procedures & workflows | Direct from SKILL.md | Referenced from agent body |
| Tool restrictions | ❌ Simulated via instructions | ✅ Native frontmatter |
| Subagent context isolation | ❌ | ✅ Native |
| Write permit enforcement | Soft (instructions) | Soft + hooks available |
| Bundled assets (scripts/templates) | ✅ Skill folder | ✅ Still in skill folder, referenced |
| Progressive context loading | ✅ | ❌ (lean bodies mitigate) |
| Model selection per role | ❌ | ✅ |
| Return schema enforcement | Soft (instructions) | Soft (instructions) |
| Handoff protocol | Instruction-driven | Instruction-driven + native `handoffs` hint |

---

## Implementation Phases

### Phase 1: Config Extension ✅

**Files:** `config/project.config.example.yml`, `init.py`, `profiles/*.config.yml`

1. Add `editor.target` to `project.config.example.yml`:
   ```yaml
   editor:
     target: "both"  # "vscode" | "claude-code" | "both"
   ```
2. Add validation in `init.py` SecurityValidator:
   ```python
   VALID_EDITOR_TARGETS = {'vscode', 'claude-code', 'both'}
   ```
3. ~~Update all profile configs to include the new field~~ Done — all 3 profiles already have `editor.target`

### Phase 2: Agent Metadata in Skills ✅

**Files:** All `skills/*/SKILL.md` (12 files — including `security`)

Done — all 12 skills already have the `agent:` block in frontmatter. Example:

```yaml
---
name: architect
description: "Designs technical approaches and writes ADRs..."
when_to_use: "write an ADR, design this, how should we architect..."
user-invocable: true
agent:
  tools: [read, search]
  agents: []
  model: null
  handoffs: [planner]
---
```

### Phase 3: Hybrid Agent Assembly in init.py

**Files:** `init.py`, `agents/` (new source directory for hand-crafted bodies)

Hybrid approach — generate frontmatter from skill metadata, use hand-crafted bodies:

1. Read each skill's `agent:` frontmatter block
2. Generate VS Code-compatible frontmatter (tools, agents, model, description)
3. Concatenate with hand-crafted body from `agents/<name>.body.md`
4. Apply `{{token}}` substitution to the combined output
5. Only runs when `editor.target` is `"vscode"` or `"both"`
6. Output to `resolved/agents/<name>.agent.md`

**Why hybrid:** Generic body extraction is fragile — each skill is structured differently. Sprint-lead is 80% orchestration logic; researcher has scope-gate flows; PM has the validation framework. Per-skill extraction rules would be hand-crafting with extra steps. Hand-crafted bodies are higher quality and simpler to maintain.

### Phase 4: Agent Body Authoring Guidelines

Each `agents/<name>.body.md` file should:

- **Include:** Identity paragraph, core constraints, output format/template
- **Reference:** `"For detailed workflow procedures, see skills/<name>/SKILL.md"`
- **Drop:** `## Subagent Mode` (native agent behavior), `## Documents You Own` / `## Shared Rules` (inline critical rules only), `## Session Lifecycle`
- **Target:** Under ~100 lines per agent body (context budget)
- **Use `{{token}}` placeholders** — resolved by init.py at build time, same as skills

### Phase 5: Tool Restriction Mapping

| Agent | tools | user-invocable | agents | Rationale |
|-------|-------|----------------|--------|-----------|
| sprint-lead | `[read, search, agent, edit]` | true | `[qa, a11y, perf, security, reviewer, docs]` | Orchestrator — delegates everything |
| qa | `[read, search, execute, edit]` | false | `[]` | Runs tests, fixes failures |
| a11y | `[read, search, execute]` | false | `[]` | Audit only — reports findings |
| perf | `[read, search, execute]` | false | `[]` | Audit only — reports findings |
| security | `[read, search, execute]` | false | `[]` | Runs dependency scans, audits code — reports findings |
| reviewer | `[read, search]` | false | `[]` | Read-only enforces "report, don't fix" |
| docs | `[read, search, edit]` | false | `[]` | Writes documentation artifacts |
| architect | `[read, search]` | true | `[]` | "Never implements code" enforced by no edit |
| pm | `[read, search]` | true | `[]` | Analysis only — no artifacts |
| planner | `[read, search, edit]` | true | `[]` | Writes sprint plans |
| researcher | `[read, search, web]` | true | `[]` | Needs web for external research |
| bug | `[read, search, edit]` | true | `[]` | Writes to bug backlog |

### Phase 6: Duplicate Discovery Resolution

**Problem:** On VS Code, both `skills/architect/SKILL.md` (discoverable as `/architect`) and `.github/agents/architect.agent.md` (discoverable as `@architect`) would appear. Users see both — confusing.

**Solution:** When `editor.target` includes `"vscode"`, `init.py` sets `user-invocable: false` on resolved skills that have generated agent wrappers. Skills become internal knowledge; agents become the user-facing layer. On Claude Code, skills stay `user-invocable: true`.

Implementation:
1. `generate_agents()` tracks which skills produced agents
2. Post-generation pass updates `resolved/skills/*/SKILL.md` frontmatter to add `user-invocable: false`
3. Source `skills/*/SKILL.md` files are never modified — only resolved copies

### Phase 7: Documentation

1. Update `README.md` — explain the dual-platform story
2. Add "Platform Selection" section to `docs/ONBOARDING.md`
3. Document what each platform gets and what's lost/gained

---

## Known Issues & Resolutions

### HIGH Impact

| # | Issue | Description | Resolution |
|---|-------|-------------|------------|
| 1 | Loss of bundled assets | Agents are single files — no `scripts/`, `references/`, `assets/` folders | Keep `skills/` folders alongside agents; agents reference them |
| 2 | Context budget explosion | Agents load entire body every invocation; skills progressively load | Keep agent bodies ≤100 lines; reference skill for procedures |
| 3 | No return schema enforcement | Tier 1/2/3 JSON schemas have no native agent equivalent | Accept soft enforcement via body instructions. Current skills also soft-enforce — schemas are LLM-followed, never machine-validated |
| 11 | Duplicate discovery | Both `/skill` and `@agent` appear for same role | Set `user-invocable: false` on resolved skills when agents exist (Phase 6) |

### MEDIUM Impact

| # | Issue | Description | Resolution |
|---|-------|-------------|------------|
| 4 | No Rego policy enforcement | `policies/*.rego` not consumable by native agents | Convert critical rules to natural language in agent bodies; use hooks for validation |
| 5 | Handoff protocol degradation | Native `handoffs` frontmatter lacks REJ-NNN lifecycle | Keep protocol in body text; native `handoffs` is ergonomic hint, not replacement |
| 6 | Phase 2-4 infrastructure | SQLite checkpoints, Docker sandboxing, Lamport timestamps — no agent equivalent | These are external tooling consumed BY agents, not converted to agents |
| 7 | Sprint-lead state management | Multi-phase orchestration has no native state machine | Sprint-lead continues using memory files + todo tool for state; hooks for lifecycle |
| 10 | Hooks can't scope to agents | `PreToolUse` fires for ALL agents, not per-agent | Per-agent write rules stay soft (body instructions only) |
| 12 | init.py needs new code | Agent assembly is new functionality | Reduced scope — frontmatter generation + body concatenation, no body extraction logic |
| 13 | Instruction loading diverges | Skills reference `.instructions.md` files that load differently per platform | Accept advisory references; actual loading is platform-configured |

### LOW Impact

| # | Issue | Description | Resolution |
|---|-------|-------------|------------|
| 1f | `when_to_use` has no agent equivalent | Must fold into `description` (1024 char limit) | Concatenate carefully; trim to fit |
| 4r | Runtime vs build-time templates | `{N}` (runtime) vs `{{paths}}` (build-time) | Document the distinction; both work as-is |
| 5t | `#tool:agent` is VS Code-specific | Claude Code has no equivalent invocation syntax | Accept platform-specific body text; skills use it for VS Code already |
| 7d | Dual-use agents (user + subagent) | Some skills behave differently per invocation mode | Use conditional body instructions: "When invoked as subagent, skip X" |
| 9 | Retry = new subagent invocation | Doubles cost on schema validation failures | Acceptable trade-off; rare in practice |

---

## Relevant Files

| File | Role | Change Needed |
|------|------|---------------|
| `skills/*/SKILL.md` (12) | Canonical source | ✅ Already have `agent:` frontmatter block |
| `agents/*.body.md` (12) | Hand-crafted agent bodies | New — one per skill, ≤100 lines each |
| `init.py` | Template resolution engine | Add `generate_agents()`, editor target validation, conditional skill visibility |
| `config/project.config.example.yml` | Config schema | Add `editor.target` field |
| `profiles/*.config.yml` (3) | Pre-filled configs | ✅ Already have `editor.target` field |
| `config/plugin.json` | Plugin manifest | Add `resolved/agents/` to output paths when editor.target includes vscode |
| `instructions/` | Shared instruction files | No change — referenced by both platforms |
| `policies/*.rego` | Policy enforcement | No change — external tooling |
| `schemas/subagent-return-tier*.schema.json` | Return schemas | No change — soft-enforced on both platforms |
| `resolved/` | Output directory | Gains `resolved/agents/` |

---

## Design Decisions

1. **Skills are the single source of truth for procedures** — agent bodies are hand-crafted but reference skills for detailed workflows
2. **Hybrid generation** — frontmatter is generated from skill `agent:` metadata (single source of truth for tool restrictions); bodies are hand-crafted (higher quality, simpler pipeline)
3. **Deterministic enforcement is soft on both platforms** — schemas, write permits, and return validation are LLM-followed instructions, not machine-validated contracts
4. **Bundled assets stay in skill folders** — agents reference them; no migration needed
5. **init.py handles all platform-conditional logic** — source files are platform-agnostic
6. **Phase 2-4 infrastructure is orthogonal** — checkpoints, sandboxing, and determinism are consumed by agents/skills, not converted to either
7. **12 skills, not 11** — `security` is a full skill with its own agent metadata

---

## When to Use What (User Guidance)

| If your role needs... | Use a... | Why |
|-----------------------|----------|-----|
| Tool restrictions (read-only, no execute) | Agent | Native enforcement via frontmatter |
| Bundled scripts/templates/assets | Skill | Folder structure with `scripts/`, `assets/` |
| Context isolation (subagent returns summary) | Agent | Native subagent context boundary |
| Procedural multi-step workflow | Skill | Progressive loading, step-by-step procedures |
| Model selection (cheap model for simple tasks) | Agent | `model:` frontmatter |
| Cross-platform portability | Skill | Works on both VS Code and Claude Code |

**Best pattern:** Agent delegates to skill. Agent provides persona + tool boundary. Skill provides procedural knowledge + bundled assets.
