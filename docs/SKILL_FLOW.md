# Skill Execution Flow

How agent-homebase skills orchestrate work. This document shows execution sequences, dependencies, and the FSM state machine.

---

## Skill Inventory

| Skill | Role | Invokes | Invoked By |
|-------|------|---------|------------|
| **@planner** | Scope requirements, draft sprint plans | @researcher | User, @sprint-lead |
| **@sprint-lead** | Orchestrate sprint execution end-to-end | @qa, @a11y, @perf, @reviewer, @docs, unnamed subagents | User |
| **@pm** | Validate features using 5-test echo-chamber | — | @planner |
| **@qa** | Run quality pipeline (test/lint/typecheck) | — | @sprint-lead |
| **@reviewer** | Code review for patterns, security | — | @sprint-lead |
| **@architect** | Design approaches, ADRs | @researcher | User, @planner |
| **@researcher** | Surface external patterns with citations | — | @planner, @architect |
| **@bug** | Capture bugs into structured backlog | — | User, @qa |
| **@docs** | Maintain documentation post-sprint | — | @sprint-lead |
| **@a11y** | WCAG 2.1 AA accessibility audits | — | @sprint-lead |
| **@perf** | Bundle size, build time, dependency audits | — | @sprint-lead |

---

## Sprint Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant SL as @sprint-lead
    participant QA as @qa
    participant RV as @reviewer
    participant A11Y as @a11y
    participant PERF as @perf
    participant DOCS as @docs
    participant SUB as Unnamed Subagent
    
    User->>SL: "run Sprint N" or "autopilot Sprint N"
    
    rect rgb(240, 248, 255)
        Note over SL: Phase 1: Kickoff
        SL->>SL: Read PLAN.md
        SL->>SL: Build task list
        SL->>SL: Commit: "docs: Sprint N — kick off"
    end
    
    rect rgb(255, 250, 240)
        Note over SL,SUB: Phase 2: Implementation
        loop For each task
            SL->>SUB: Delegate task
            SUB-->>SL: Return: files changed, summary
            SL->>SL: Commit: "feat/fix: task description"
        end
    end
    
    rect rgb(240, 255, 240)
        Note over SL,QA: Phase 3: Quality Gates
        SL->>QA: Run quality pipeline
        QA-->>SL: typecheck, lint, test, coverage results
        alt Coverage < threshold
            SL->>SUB: Fix coverage gaps
            SUB-->>SL: Tests added
            SL->>QA: Re-run quality pipeline
        end
    end
    
    rect rgb(255, 240, 245)
        Note over SL,RV: Phase 4: Code Review
        SL->>RV: Review all changes
        RV-->>SL: Findings + recommendations
        alt Has CRITICAL findings
            SL->>SUB: Apply fixes
            SUB-->>SL: Fixes applied
            SL->>RV: Re-review
        end
    end
    
    rect rgb(240, 240, 255)
        Note over SL,DOCS: Phase 5: Documentation
        SL->>DOCS: Update docs
        DOCS-->>SL: Docs updated
        opt A11Y gate enabled
            SL->>A11Y: Audit accessibility
            A11Y-->>SL: WCAG compliance report
        end
        opt PERF gate enabled
            SL->>PERF: Audit performance
            PERF-->>SL: Bundle/build report
        end
        SL->>SL: Push to remote
    end
    
    rect rgb(255, 255, 240)
        Note over SL: Phase 6: Retrospective
        SL->>SL: Write RETRO.md
        SL->>SL: Update SPRINTS.md
        SL->>SL: Commit: "docs: Sprint N — retrospective"
    end
    
    SL-->>User: Sprint complete + report
```

---

## FSM State Machine

The sprint-lead follows a 10-state finite state machine:

```mermaid
stateDiagram-v2
    [*] --> INITIAL
    
    INITIAL --> PLANNING: start_sprint
    PLANNING --> APPROVED: plan_approved
    PLANNING --> PLANNING: plan_revision_needed
    
    APPROVED --> IMPLEMENTATION: begin_implementation
    IMPLEMENTATION --> IMPLEMENTATION: task_complete
    IMPLEMENTATION --> COMPLETE: all_tasks_done
    
    COMPLETE --> VALIDATION: begin_validation
    VALIDATION --> VALIDATION: gate_rerun
    VALIDATION --> PASSED: all_gates_passed
    VALIDATION --> IMPLEMENTATION: gate_failed_needs_fix
    
    PASSED --> SHIPPED: push_and_verify
    SHIPPED --> [*]
    
    note right of PLANNING
        Phase 1: Kickoff
        Read PLAN.md
        Build task list
    end note
    
    note right of IMPLEMENTATION
        Phase 2: Implementation
        Delegate to subagents
        One commit per task
    end note
    
    note right of VALIDATION
        Phase 3-4: Quality + Review
        Run @qa, @reviewer
        Fix loop if needed
    end note
    
    note right of SHIPPED
        Phase 5-6: Docs + Retro
        Update docs, write RETRO.md
        Push to remote
    end note
```

### State Descriptions

| State | Description | Exit Conditions |
|-------|-------------|-----------------|
| INITIAL | Sprint not started | `start_sprint` → PLANNING |
| PLANNING | Reading PLAN.md, building task list | `plan_approved` → APPROVED |
| APPROVED | Plan validated, ready to implement | `begin_implementation` → IMPLEMENTATION |
| IMPLEMENTATION | Tasks being executed by subagents | `all_tasks_done` → COMPLETE |
| COMPLETE | All tasks finished, ready for validation | `begin_validation` → VALIDATION |
| VALIDATION | Running quality gates and code review | `all_gates_passed` → PASSED, `gate_failed` → IMPLEMENTATION |
| PASSED | All gates passed, ready to ship | `push_and_verify` → SHIPPED |
| SHIPPED | Sprint complete, RETRO.md written | Terminal state |

---

## Planning Flow

```mermaid
flowchart TD
    subgraph Planning["@planner Flow"]
        A[User request] --> B{Type?}
        B -->|Feature| C[@planner: scope feature]
        B -->|Research needed| D[@researcher: gather patterns]
        D --> C
        C --> E{Complex architecture?}
        E -->|Yes| F[@architect: design approach]
        F --> G[@pm: validate via 5-test]
        E -->|No| G
        G --> H{Passes 5-test?}
        H -->|Yes| I[Draft PLAN.md]
        H -->|No| J[Add to NON_GOALS.md]
        I --> K[@sprint-lead: execute]
    end
```

---

## Quality Gate Flow

```mermaid
flowchart TD
    subgraph Gates["Quality Gate Sequence"]
        A[@qa: Start] --> B[Typecheck]
        B --> C{Pass?}
        C -->|No| D[BLOCKED: Fix types]
        C -->|Yes| E[Lint]
        E --> F{Pass?}
        F -->|No| G[BLOCKED: Fix lint]
        F -->|Yes| H[Unit Tests]
        H --> I{Pass?}
        I -->|No| J[BLOCKED: Fix tests]
        I -->|Yes| K[Coverage Check]
        K --> L{>= threshold?}
        L -->|No| M[BLOCKED: Add tests]
        L -->|Yes| N{E2E enabled?}
        N -->|Yes| O[E2E Tests]
        N -->|No| P[PASSED]
        O --> Q{Pass?}
        Q -->|No| R[BLOCKED: Fix E2E]
        Q -->|Yes| P
    end
```

---

## Subagent Return Flow

All subagents return structured data per tier:

```mermaid
flowchart LR
    subgraph Tier1["Tier 1: Analysis Only"]
        A1[Summary] --> A2[Findings array]
        A2 --> A3[Status: complete/blocked]
    end
    
    subgraph Tier2["Tier 2: With Artifacts"]
        B1[Summary] --> B2[Artifact path]
        B2 --> B3[Artifact type]
        B3 --> B4[Findings array]
    end
    
    subgraph Tier3["Tier 3: Composition"]
        C1[Summary] --> C2[Multiple artifacts]
        C2 --> C3[Metadata]
        C3 --> C4[Provenance chain]
    end
```

| Tier | Use Case | Example Skills |
|------|----------|----------------|
| **Tier 1** | Analysis, validation, recommendations | @pm, @researcher (analysis mode) |
| **Tier 2** | Single artifact creation | @planner (draft), @docs (update) |
| **Tier 3** | Multi-artifact composition | @sprint-lead (full sprint) |

---

## Skill Dependencies

```mermaid
graph TD
    subgraph Core["Core Skills (always needed)"]
        PL[@planner]
        SL[@sprint-lead]
        QA[@qa]
        RV[@reviewer]
        BUG[@bug]
    end
    
    subgraph Research["Research Layer"]
        RS[@researcher]
        AR[@architect]
        PM[@pm]
    end
    
    subgraph Quality["Quality Layer"]
        A11[@a11y]
        PERF[@perf]
    end
    
    subgraph Docs["Documentation"]
        DOCS[@docs]
    end
    
    PL --> RS
    PL --> PM
    AR --> RS
    SL --> QA
    SL --> RV
    SL --> A11
    SL --> PERF
    SL --> DOCS
    QA -.-> BUG
```

---

## Error Recovery

When a skill fails or returns `status: blocked`:

1. **@sprint-lead** logs the blocker reason
2. If recoverable (e.g., test failure), spawns fix subagent
3. Re-runs the failed skill
4. After 3 retries, escalates to user via `#tool:askQuestions`

```mermaid
flowchart TD
    A[Skill returns blocked] --> B{Retry count < 3?}
    B -->|Yes| C[Spawn fix subagent]
    C --> D[Re-run skill]
    D --> E{Passed?}
    E -->|Yes| F[Continue]
    E -->|No| B
    B -->|No| G[Escalate to user]
    G --> H{User choice}
    H -->|Skip gate| I[Mark as WARNING, continue]
    H -->|Abort sprint| J[Rollback to checkpoint]
    H -->|Manual fix| K[Wait for user fix]
    K --> D
```

---

## Cross-References

- [INSTRUCTION_INDEX.md](INSTRUCTION_INDEX.md) — Instructions each skill follows
- [ARCHITECTURE.md](ARCHITECTURE.md) — Why this orchestration model
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Common skill invocation issues
