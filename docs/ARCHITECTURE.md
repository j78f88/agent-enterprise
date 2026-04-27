# Architecture

Design decisions and rationale for agent-homebase.

---

## Overview

agent-homebase is a library of agent skills, instructions, and supporting infrastructure for VS Code Copilot agent mode. It provides:

- **11 specialized skills** for software delivery workflows
- **23 instruction files** for governance and contracts
- **4-phase implementation** for production-grade execution

---

## Core Design Principles

### 1. Thin Orchestration

Orchestrators (`@sprint-lead`) delegate ALL heavy work to subagents:

```
@sprint-lead (thin)
    ├── Reads plans
    ├── Tracks state
    ├── Collects summaries
    └── Delegates to:
        ├── Unnamed subagents (implementation)
        ├── @qa (quality gates)
        ├── @reviewer (code review)
        └── @docs (documentation)
```

**Why?** Context limits. An orchestrator that reads source files and runs commands will exhaust its context window. Delegation keeps each agent focused.

### 2. Contract-First Design

All agent interactions follow defined contracts:

- **Return schemas**: Tier 1/2/3 JSON schemas define what agents return
- **Write permits**: Agents can only write to permitted paths
- **Severity levels**: Findings use consistent CRITICAL/WARNING/SUGGESTION

**Why?** Predictability. When `@qa` returns `status: blocked`, `@sprint-lead` knows exactly how to handle it.

### 3. Configuration Over Code

Behavior is controlled through `project.config.yml`, not code changes:

```yaml
quality:
  coverage_threshold: 85    # Change threshold without editing skills
  
commands:
  test: "pnpm test"         # Use project's actual commands
```

**Why?** Portability. The same skills work across different projects with different toolchains.

### 4. Progressive Enhancement

Four phases add capabilities incrementally:

| Phase | Capability | Required |
|-------|------------|----------|
| 0 | Security validation, observability | ✅ |
| 1 | Formal contracts, policy engine | ✅ |
| 2 | Durable execution, checkpoints | ○ |
| 3 | Sandboxed execution | ○ |
| 4 | Deterministic replay | ○ |

**Why?** Not every project needs full durability. Start simple, add phases as needed.

### When to Use Each Phase

**Phase 0** (Security): Always required. Protects against dangerous commands and path traversal.

**Phase 1** (Contracts): Always required. Ensures agents return predictable data for orchestration.

**Phase 2** (Durability): Use for sprints longer than 4 hours or when interruptions are likely. Enables checkpoint/resume.
- **Skip if**: Short sprints (<1 hour), disposable work
- **Use if**: Multi-day sprints, unstable network, need audit trail

**Phase 3** (Sandboxing): Use when running untrusted code or limiting resource usage.
- **Skip if**: Trusted codebase, local development only
- **Use if**: CI/CD pipelines, unknown dependencies, resource quotas required

**Phase 4** (Determinism): Use when reproducibility is critical (debugging, audits, compliance).
- **Skip if**: Results don't need to be bit-for-bit identical
- **Use if**: Regulatory requirements, troubleshooting non-deterministic failures

---

## Why 4 Phases?

### Phase 0: Foundation

**Problem**: Agent systems can execute dangerous commands, leak secrets, or produce unpredictable output.

**Solution**: Security validation in `init.py`:
- Command whitelist (no `rm -rf`)
- Path traversal detection (no `../../../etc/passwd`)
- Secret scanning (no API keys in config)

### Phase 1: Formal Verification

**Problem**: Agents return inconsistent data, making orchestration brittle.

**Solution**: JSON Schema validation + Rego policies:
- Return schemas enforce structure
- Policies enforce business rules (feature/bug balance, capacity)
- FSM ensures valid state transitions

### Phase 2: Durable Execution

**Problem**: Long-running sprints can fail mid-execution, losing progress.

**Solution**: SQLite persistence + checkpoints:
- State snapshots at phase boundaries
- Resume from any checkpoint
- Bidirectional markdown ↔ SQLite migration

### Phase 3: Sandboxing

**Problem**: Agent tasks (tests, builds) can affect host system or access unauthorized resources.

**Solution**: Docker container isolation:
- Resource limits (CPU, memory, time)
- Network policies (deny by default)
- Capability framework (fine-grained permissions)

### Phase 4: Determinism

**Problem**: Replaying a sprint produces different results due to time, randomness, composition order.

**Solution**: Deterministic execution:
- Lamport timestamps (logical time)
- Prompt versioning (detect skill changes)
- Content-based tie-breaking (reproducible ordering)
- LLM config enforcement (temperature=0)

---

## Why Rego for Policies?

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| **Hardcoded Python** | Simple | Not configurable, hard to audit |
| **YAML rules** | Readable | Limited expressiveness |
| **JSON Schema** | Standard | Only validates structure, not logic |
| **Rego** | Powerful, auditable, standard | Learning curve |

### Decision: Rego

Rego (Open Policy Agent) provides:

1. **Declarative rules**: Easy to read and audit
2. **Composition**: Policies can reference each other
3. **Testing**: Built-in test framework
4. **Ecosystem**: Industry standard for policy-as-code

Example policy:
```rego
# Violation if feature allocation exceeds cap
violation[msg] {
    input.constraints.featurePercent > 70
    msg := sprintf("Feature allocation %v%% exceeds 70%% cap", [input.constraints.featurePercent])
}
```

---

## Why 3 Return Schema Tiers?

### Tier 1: Analysis Only

Returns that produce no artifacts. Used for validation, recommendations.

```json
{
  "tier": 1,
  "status": "complete",
  "summary": "Analysis complete",
  "findings": [...]
}
```

**Use cases**: @pm validation, @qa pipeline, @reviewer feedback

### Tier 2: With Artifact

Returns that produce a single artifact (document, code file).

```json
{
  "tier": 2,
  "status": "complete",
  "summary": "Draft created",
  "artifactPath": "docs/draft.md",
  "artifactType": "draft"
}
```

**Use cases**: @planner drafts, @docs updates, @bug reports

### Tier 3: Composition

Returns with multiple artifacts, metadata, provenance. Used by orchestrators.

```json
{
  "tier": 3,
  "status": "complete",
  "summary": "Sprint complete",
  "artifacts": [...],
  "metadata": {...},
  "provenance": {...}
}
```

**Use cases**: @sprint-lead sprint completion

### Why Not One Schema?

- Tier 1 agents shouldn't need to specify artifact paths
- Tier 3 metadata is irrelevant for simple validations
- Validation can be stricter when tier is known

### When to Use Each Tier

**Use Tier 1** when:
- Agent performs analysis only (no files created)
- Returns findings, recommendations, or validation results
- Examples: `@pm` validating requirements, `@qa` checking coverage, `@reviewer` suggesting improvements

**Use Tier 2** when:
- Agent creates **one** artifact (document, code file, report)
- Artifact needs to be tracked for downstream processing
- Examples: `@planner` creating draft plan, `@docs` updating README, `@bug` writing bug report

**Use Tier 3** when:
- Agent orchestrates multiple subagents
- Need to track provenance (which subagents ran, how many retries)
- Need metadata (duration, commit count, coverage delta)
- Examples: `@sprint-lead` completing sprint, `@architect` generating multi-file solution

**Decision matrix**:
| Created Files | Orchestrates Others | Recommended Tier |
|---------------|---------------------|------------------|
| 0 | No | Tier 1 |
| 1 | No | Tier 2 |
| 0+ | Yes | Tier 3 |

---

## Why SQLite Over Other Databases?

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| **JSON files** | Simple | No ACID, no queries |
| **PostgreSQL** | Powerful | Requires server |
| **MongoDB** | Flexible schema | Requires server |
| **SQLite** | Embedded, ACID, standard | Limited concurrency |

### Decision: SQLite

1. **Zero configuration**: No server to run
2. **ACID guarantees**: Crash-safe writes
3. **SQL queries**: Powerful ad-hoc analysis
4. **WAL mode**: Good read concurrency
5. **Portable**: Single file, easy to backup

For agent workflows with single-writer, SQLite is ideal.

---

## Why Lamport Timestamps?

### The Problem with Wall-Clock Time

```python
# Non-deterministic
event_a = {"time": datetime.now(), "type": "task_start"}
# ... some processing ...
event_b = {"time": datetime.now(), "type": "task_end"}

# Replay: wall-clock times will differ
```

### Lamport's Solution

```python
clock = LogicalClock()

event_a = {"time": clock.tick(), "type": "task_start"}  # time=1
# ... some processing ...
event_b = {"time": clock.tick(), "type": "task_end"}    # time=2

# Replay: logical times are identical
```

**Properties**:
- If A → B, then timestamp(A) < timestamp(B)
- Monotonically increasing
- Independent of wall-clock

---

## Configuration vs Instructions vs Skills

| Layer | Purpose | Location | Uses Tokens |
|-------|---------|----------|-------------|
| **Config** | Project-specific values | `project.config.yml` | N/A |
| **Instructions** | Governance rules | `instructions/` | Some |
| **Skills** | Agent behavior | `skills/` | Yes |

### Flow

```
project.config.yml
        ↓
   init.py (token substitution)
        ↓
   resolved/skills/
   resolved/instructions/
        ↓
   .github/agents/
   .github/instructions/
```

---

## Security Model

### Defense in Depth

```
Layer 1: Config Validation (init.py)
    ↓ Command whitelist, path validation, secret scanning
    
Layer 2: Policy Enforcement (Rego)
    ↓ Business rules, composition constraints
    
Layer 3: Sandbox Isolation (Docker)
    ↓ Resource limits, network policies, capabilities
    
Layer 4: Audit Trail (JSONL logs)
    ↓ All operations logged for forensics
```

### Threat Model

| Threat | Mitigation |
|--------|------------|
| Command injection | Whitelist + pattern detection |
| Path traversal | Validation + sandbox isolation |
| Secret exposure | Scanning + audit logging |
| Resource exhaustion | Container limits |
| Network exfiltration | Deny-by-default policies |

---

## Future Considerations

### Not Implemented (Yet)

1. **Multi-agent coordination**: Parallel agent execution
2. **Custom LLM backends**: Support beyond Copilot
3. **Visual workflow editor**: GUI for skill composition
4. **Plugin marketplace**: Community skill sharing

### Design Constraints

- **VS Code dependency**: Skills are VS Code Copilot agents
- **Single-writer**: SQLite assumes one writer at a time
- **Docker dependency**: Phase 3 requires Docker

---

## Cross-References

- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) — Original design document
- [PHASE_4_IMPLEMENTATION_SUMMARY.md](PHASE_4_IMPLEMENTATION_SUMMARY.md) — Latest phase details
- [SKILL_FLOW.md](SKILL_FLOW.md) — Execution diagrams
- [POLICIES.md](POLICIES.md) — Policy file documentation
