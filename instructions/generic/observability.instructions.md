---
id: instruction.observability
kind: instruction
version: 1.0.0
applies_to: '**'
description: observability instruction
---

# Observability & Traceability

**Phase 0 Foundation — Production-Grade Instrumentation**

This instruction establishes the observability layer for agent-enterprise, enabling distributed tracing, session replay, performance profiling, and time-travel debugging.

---

## Design Principles

1. **Trace Everything** — Every subagent invocation creates a span
2. **Structured Events** — No unstructured logs, all events have schemas
3. **Deterministic Replay** — Sessions reproducible from traces
4. **Low Overhead** — <10% performance impact from instrumentation
5. **Queryable** — All traces and events searchable, filterable, aggregatable

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│           OpenTelemetry SDK                     │
│  (Tracing, Metrics, Logs)                       │
└────────────────┬────────────────────────────────┘
                 │ OTLP Protocol
                 ↓
┌─────────────────────────────────────────────────┐
│        Observability Backend                    │
│  • Jaeger (traces)                              │
│  • Prometheus (metrics)                         │
│  • Elasticsearch (logs, events)                 │
└─────────────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────┐
│           Observability Dashboard               │
│  • Session replay                               │
│  • Flame graphs                                 │
│  • Cost attribution                             │
│  • Drift detection                              │
└─────────────────────────────────────────────────┘
```

---

## Distributed Tracing

### Trace Hierarchy

```
Session (root span)
├── Phase: Planning (span)
│   ├── Subagent: @planner composition (span)
│   │   ├── LLM Call: gpt-4 (span)
│   │   ├── File Read: BACKLOG_LEDGER.md (span)
│   │   └── File Write: SPRINT-042-PLAN.md (span)
│   └── Validation: composition constraints (span)
├── Phase: Implementation (span)
│   ├── Subagent: task-1 implementation (span)
│   │   ├── LLM Call: gpt-4 (span)
│   │   ├── File Edit: src/utils/helpers.ts (span)
│   │   └── Git Commit: abc123 (span)
│   └── Subagent: task-2 implementation (span)
└── Phase: Quality Gates (span)
    ├── Gate: TypeScript check (span)
    ├── Gate: Linting (span)
    └── Gate: Tests (span)
```

### Span Attributes

**Session Span:**
```json
{
  "span.kind": "session",
  "session.id": "sprint-042",
  "session.mode": "autopilot",
  "session.start_time": "2026-04-27T10:00:00Z",
  "session.agent": "sprint-lead",
  "session.plan_path": "sprints/042/PLAN.md"
}
```

**Subagent Span:**
```json
{
  "span.kind": "subagent",
  "subagent.name": "task-1-impl",
  "subagent.agent": "unnamed",
  "subagent.write_permit": "[WRITE:IMPLEMENTATION]",
  "subagent.task_id": "ITEM-123",
  "subagent.complexity": "moderate",
  "subagent.files_changed": 3,
  "subagent.lines_added": 45,
  "subagent.lines_deleted": 12,
  "subagent.commits": 2
}
```

**LLM Call Span:**
```json
{
  "span.kind": "llm",
  "llm.provider": "openai",
  "llm.model": "gpt-4-turbo",
  "llm.temperature": 0.0,
  "llm.prompt_tokens": 2500,
  "llm.completion_tokens": 800,
  "llm.cost_usd": 0.045,
  "llm.latency_ms": 3200
}
```

**Gate Span:**
```json
{
  "span.kind": "gate",
  "gate.name": "typescript-check",
  "gate.status": "pass",
  "gate.duration_ms": 4500,
  "gate.errors": 0,
  "gate.warnings": 2
}
```

### Trace Propagation

Traces propagate across agent boundaries via **W3C Trace Context** headers:

```python
# Parent agent creates span
with tracer.start_as_current_span("subagent.implementation") as span:
    trace_id = span.get_span_context().trace_id
    span_id = span.get_span_context().span_id
    
    # Pass trace context to subagent
    result = invoke_subagent(
        task=task,
        trace_parent=f"00-{trace_id:032x}-{span_id:016x}-01"
    )
```

---

## Structured Event Logging

### Event Schema

All events follow a structured format (JSON Lines):

```json
{
  "timestamp": "2026-04-27T10:15:30.123Z",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "event_type": "subagent.completed",
  "severity": "info",
  "agent": "sprint-lead",
  "subagent": "task-1-impl",
  "attributes": {
    "status": "success",
    "commits": 2,
    "complexity": "moderate"
  }
}
```

### Event Types

| Event Type                | Severity | Description                              |
|---------------------------|----------|------------------------------------------|
| `session.started`         | info     | Sprint orchestration session begins      |
| `session.completed`       | info     | Sprint session completes successfully    |
| `session.failed`          | error    | Sprint session fails                     |
| `subagent.invoked`        | info     | Subagent invoked with task               |
| `subagent.completed`      | info     | Subagent returns successfully            |
| `subagent.failed`         | error    | Subagent fails or times out              |
| `subagent.retry`          | warn     | Subagent retrying after failure          |
| `gate.started`            | info     | Quality gate begins execution            |
| `gate.passed`             | info     | Gate passes                              |
| `gate.failed`             | error    | Gate fails with findings                 |
| `phase.transition`        | info     | Orchestration moves to new phase         |
| `checkpoint.created`      | info     | State checkpoint written                 |
| `security.violation`      | error    | Security policy violation detected       |
| `policy.violation`        | warn     | Governance policy violation              |
| `llm.call`                | info     | LLM API call                             |
| `file.read`               | debug    | File read operation                      |
| `file.write`              | info     | File write operation                     |
| `git.commit`              | info     | Git commit created                       |

### Event Storage

Events written to `.agent-state/events.jsonl` (append-only):

```bash
# Query events with jq
cat .agent-state/events.jsonl | jq 'select(.event_type == "gate.failed")'

# Count events by type
cat .agent-state/events.jsonl | jq -r '.event_type' | sort | uniq -c
```

---

## Session Replay

### Replay Data Model

Session replay captures full execution history for deterministic replay:

```json
{
  "session_id": "sprint-042",
  "start_time": "2026-04-27T10:00:00Z",
  "end_time": "2026-04-27T11:23:45Z",
  "duration_seconds": 5025,
  "status": "completed",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "checkpoints": [
    {
      "phase": "planning",
      "timestamp": "2026-04-27T10:05:30Z",
      "state_hash": "sha256:abc123...",
      "artifacts": ["sprints/042/PLAN.md"]
    },
    {
      "phase": "implementation",
      "timestamp": "2026-04-27T10:35:00Z",
      "state_hash": "sha256:def456...",
      "artifacts": ["src/utils/helpers.ts", ".agent-state/checkpoint-impl.json"]
    }
  ],
  "events": [...],  // All events from session
  "spans": [...],   // All trace spans
  "cost_usd": 2.45,
  "llm_tokens": 125000
}
```

### Replay Capability

**Time-Travel Debugging:**
```bash
# Replay session from start
agent-replay --session sprint-042

# Replay from specific checkpoint
agent-replay --session sprint-042 --from-checkpoint implementation

# Replay with modifications (A/B testing)
agent-replay --session sprint-042 --override-config modified.yml
```

**Verification:**
- Replay produces identical outputs (bit-for-bit) when deterministic
- Trace IDs differ, but span structure and attributes match
- Useful for debugging, testing orchestration changes

---

## Metrics

### System Metrics

| Metric                         | Type      | Description                              |
|--------------------------------|-----------|------------------------------------------|
| `session.duration_seconds`     | histogram | Total session execution time             |
| `session.success_rate`         | gauge     | % of sessions completed successfully     |
| `subagent.invocations_total`   | counter   | Total subagent invocations               |
| `subagent.duration_seconds`    | histogram | Subagent execution time                  |
| `subagent.retry_count`         | counter   | Number of retries                        |
| `gate.duration_seconds`        | histogram | Gate execution time                      |
| `gate.failure_rate`            | gauge     | % of gate failures                       |
| `llm.tokens_total`             | counter   | Total tokens consumed                    |
| `llm.cost_usd_total`           | counter   | Total LLM cost                           |
| `llm.latency_seconds`          | histogram | LLM API latency                          |
| `phase.duration_seconds`       | histogram | Per-phase timing                         |
| `checkpoint.size_bytes`        | histogram | Checkpoint artifact size                 |

### Business Metrics

| Metric                         | Type      | Description                              |
|--------------------------------|-----------|------------------------------------------|
| `tasks.completed_total`        | counter   | Total tasks completed                    |
| `tasks.complexity`             | histogram | Task complexity distribution             |
| `bugs.fixed_total`             | counter   | Total bugs fixed                         |
| `features.delivered_total`     | counter   | Total features delivered                 |
| `code.lines_changed`           | counter   | Lines of code changed                    |
| `commits.total`                | counter   | Total commits created                    |
| `sprint.velocity`              | gauge     | Story points / sprint                    |

### Cost Attribution

Track spend per agent, per task, per session:

```json
{
  "session_id": "sprint-042",
  "cost_breakdown": {
    "total_usd": 2.45,
    "by_agent": {
      "@planner": 0.15,
      "@sprint-lead": 0.25,
      "subagent-impl-1": 0.80,
      "subagent-impl-2": 0.65,
      "@qa": 0.35,
      "@reviewer": 0.25
    },
    "by_phase": {
      "planning": 0.15,
      "implementation": 1.45,
      "quality-gates": 0.85
    },
    "by_model": {
      "gpt-4-turbo": 2.15,
      "gpt-3.5-turbo": 0.30
    }
  }
}
```

---

## Performance Profiling

### Flame Graphs

Generate flame graphs for any session to identify bottlenecks:

```bash
# Generate flame graph
agent-profile --session sprint-042 --output flame.svg

# View slowest spans
agent-profile --session sprint-042 --top 10
```

**Example Output:**
```
Top 10 Slowest Spans (sprint-042):
1. subagent.task-3-impl      18m 32s  (complexity: high, 3 retries)
2. gate.e2e-tests            12m 15s  (504 tests, 2 failures)
3. subagent.task-1-impl       8m 47s  (complexity: moderate)
4. gate.typescript-check      4m 23s  (large codebase)
5. subagent.task-2-impl       3m 56s  (complexity: low)
...
```

### Bottleneck Detection

Automated bottleneck detection flags slow operations:

```json
{
  "event_type": "performance.bottleneck",
  "severity": "warn",
  "span_id": "subagent.task-3-impl",
  "duration_seconds": 1112,
  "threshold_seconds": 600,
  "recommendation": "Task marked 'high complexity' but took 18+ minutes. Split into subtasks."
}
```

---

## Drift Detection

Monitor sprint trends and alert on degrading health:

```json
{
  "event_type": "drift.detected",
  "severity": "warn",
  "metric": "sprint.velocity",
  "current_value": 18.5,
  "expected_value": 25.0,
  "deviation_percent": -26,
  "trend": "degrading",
  "sprints_analyzed": 5,
  "recommendation": "Velocity declining for 3 consecutive sprints. Review technical debt and complexity trends."
}
```

### Anomaly Detection

Statistical anomaly detection on key metrics:
- Z-score analysis (> 2σ from mean)
- Exponential moving average (EMA)
- Seasonal trend decomposition

---

## Dashboard Widgets

### Real-Time Session View

```
┌─────────────────────────────────────────────────┐
│ Sprint 042 — In Progress (Phase 3/6)           │
├─────────────────────────────────────────────────┤
│ ✓ Planning          5m 30s   $0.15             │
│ ✓ Implementation   45m 12s   $1.45             │
│ ⟳ Quality Gates    Running   $0.60             │
│   ├─ ✓ TypeCheck    4m 23s                     │
│   ├─ ✓ Lint         1m 15s                     │
│   ├─ ⟳ Tests       Running                     │
│   └─ ⏸ E2E         Pending                     │
└─────────────────────────────────────────────────┘
```

### Cost Tracking

```
┌─────────────────────────────────────────────────┐
│ LLM Cost — Last 30 Days                        │
├─────────────────────────────────────────────────┤
│ Total:     $347.82                              │
│ Average:   $11.59 / day                         │
│ Trend:     ↗ +15% vs previous month            │
│                                                 │
│ Top Agents:                                     │
│ 1. subagents (impl)  $245.30  (71%)            │
│ 2. @reviewer          $45.20  (13%)            │
│ 3. @qa                $32.10   (9%)            │
│ 4. @planner           $15.22   (4%)            │
└─────────────────────────────────────────────────┘
```

### SLO Dashboard

```
┌─────────────────────────────────────────────────┐
│ Service Level Objectives (30d)                 │
├─────────────────────────────────────────────────┤
│ Sprint Success Rate:  96.7%  ✓ (target: 95%)   │
│ Mean Time to Recovery: 4.2m  ✓ (target: <5m)   │
│ Gate Pass Rate:       98.1%  ✓ (target: 95%)   │
│ Subagent Retry Rate:   2.3%  ✓ (target: <5%)   │
│ Observability Overhead: 8%   ✓ (target: <10%)  │
└─────────────────────────────────────────────────┘
```

---

## Implementation Roadmap

### Phase 0 (Current)
- [x] Event schema design
- [x] Security audit logging
- [ ] Basic span instrumentation (manual)
- [ ] Event storage (`.agent-state/events.jsonl`)

### Phase 1
- [ ] OpenTelemetry SDK integration
- [ ] Automatic span creation decorators
- [ ] Jaeger backend deployment
- [ ] Basic dashboard

### Phase 2
- [ ] Session replay capability
- [ ] Checkpoint-restart integration
- [ ] Cost attribution tracking

### Phase 3
- [ ] Flame graph generation
- [ ] Bottleneck detection
- [ ] Drift detection with anomaly alerts

---

## Configuration

Add to `project.config.yml`:

```yaml
observability:
  enabled: true
  backend: "jaeger"              # jaeger | tempo | honeycomb
  endpoint: "http://localhost:4318"
  sample_rate: 1.0               # 1.0 = trace everything
  log_level: "info"              # debug | info | warn | error
  cost_tracking: true
  metrics_port: 9090
```

---

## References

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [AgentOps Observability](https://docs.agentops.ai/)
- [Jaeger Tracing](https://www.jaegertracing.io/)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)
