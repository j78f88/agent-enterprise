# Determinism Guide

How agent-enterprise ensures reproducible execution through logical time, prompt versioning, and replay verification.

---

## Overview

Phase 4 provides determinism guarantees through four mechanisms:

| Mechanism | Purpose | Implementation |
|-----------|---------|----------------|
| **Logical Time** | Deterministic event ordering | Lamport timestamps |
| **Prompt Versioning** | Detect skill template changes | SHA256 content hashing |
| **Deterministic Composition** | Reproducible ordering | Content-based tie-breaking |
| **LLM Config Enforcement** | Prevent sampling variance | Temperature=0 validation |

---

## Logical Time (Lamport Timestamps)

### Why Not Wall-Clock Time?

Wall-clock time introduces non-determinism:
- Different machines have clock drift
- Daylight saving transitions
- NTP corrections can jump backwards
- Parallel events may get identical timestamps

### How Lamport Timestamps Work

```python
from src.phase4_determinism.logical_time import LogicalClock

clock = LogicalClock()

# Local event: increment counter
t1 = clock.tick()  # Returns 1

# Another local event
t2 = clock.tick()  # Returns 2

# Received remote event with timestamp 10
# Synchronize: max(local, remote) + 1
t3 = clock.update(10)  # Returns 11

# Next local event
t4 = clock.tick()  # Returns 12
```

### Properties

1. **Monotonic**: Timestamps always increase
2. **Causal ordering**: If A → B, then timestamp(A) < timestamp(B)
3. **Thread-safe**: Lock-protected increment operations
4. **Checkpoint-safe**: Clock state persisted in checkpoints

### Usage in agent-enterprise

```python
# Event recording
event = {
    "type": "task_complete",
    "logical_time": clock.tick(),
    "data": {...}
}

# Multi-agent synchronization
def receive_event(remote_event):
    clock.update(remote_event["logical_time"])
    # Process event...
```

---

## Prompt Versioning

### Why Version Prompts?

Skill templates (`SKILL.md` files) may change between executions. Without versioning:
- Replay produces different results
- Debugging becomes impossible
- Regression detection fails

### How It Works

```python
from src.phase4_determinism.prompt_versioning import PromptVersioner

versioner = PromptVersioner()

# Register a prompt template
version = versioner.register("sprint-lead", skill_content)
# Returns: "sprint-lead@a1b2c3d4"

# Check for changes
if versioner.has_changed("sprint-lead", new_content):
    print("WARNING: Prompt template modified since last execution")
```

### Hash Calculation

- **Algorithm**: SHA256
- **Truncation**: First 12 characters (collision-resistant for practical use)
- **Normalization**: Whitespace-normalized before hashing

### Integration Points

1. **Sprint kickoff**: All used skill templates are hashed and recorded
2. **Checkpoint**: Prompt versions stored in checkpoint metadata
3. **Replay**: Versions compared to detect drift
4. **CI/CD**: Version changes flagged in PR checks

---

## Deterministic Composition

### The Problem

When composing backlog items into a sprint, ties can occur:
- Same priority tier (P1 = P1)
- Same score within tier (5.0 = 5.0)

Non-deterministic tie-breaking (e.g., insertion order) breaks replay.

### Content-Based Tie-Breaking

```python
from src.phase4_determinism.deterministic_composition import DeterministicComposer

composer = DeterministicComposer()

items = [
    {"id": "ITEM-042", "tier": "P1", "score": 5.0},
    {"id": "ITEM-043", "tier": "P1", "score": 5.0},  # Tie!
    {"id": "ITEM-044", "tier": "P1", "score": 5.0},  # Three-way tie!
]

# Deterministic ordering using content hash
ordered = composer.compose(items)
# Always produces same order regardless of input order
```

### Tie-Breaking Algorithm

1. **Primary sort**: Priority tier (P0 > P1 > P2...)
2. **Secondary sort**: Score (descending)
3. **Tertiary sort**: SHA256 hash of item ID (deterministic)

```python
def tie_breaker(item):
    return hashlib.sha256(item["id"].encode()).hexdigest()
```

---

## LLM Config Enforcement

### Why Temperature = 0?

LLM sampling with temperature > 0 introduces randomness:
- Same prompt → different responses
- Replay diverges immediately
- Non-reproducible bugs

### Enforcement

```python
from src.phase4_determinism.llm_config import LLMConfigValidator

validator = LLMConfigValidator(strict=True)

config = {
    "model": "gpt-4",
    "temperature": 0.7,  # Non-deterministic!
    "max_tokens": 4096
}

result = validator.validate(config)
# result.valid = False
# result.violations = ["temperature must be 0.0 for deterministic execution"]
```

### Strict vs Non-Strict Mode

| Mode | Temperature > 0 | Behavior |
|------|-----------------|----------|
| **Strict** | Error | Blocks execution |
| **Non-strict** | Warning | Logs warning, continues |

Configure in `project.config.yml`:
```yaml
determinism:
  strict_mode: true  # Enforce temperature=0
```

---

## Replay Verification

### Recording Traces

During execution, all events are recorded:

```python
from src.phase4_determinism.replay_verification import TraceRecorder

recorder = TraceRecorder(sprint_id="042")

# Record events
recorder.record("task_started", {"task_id": "TASK-001"})
recorder.record("subagent_call", {"agent": "qa", "input_hash": "abc123"})
recorder.record("task_completed", {"task_id": "TASK-001", "output_hash": "def456"})

# Save trace
recorder.save(".agent-state/traces/sprint-042.trace")
```

### Verifying Replay

```python
from src.phase4_determinism.replay_verification import ReplayVerifier

verifier = ReplayVerifier()

# Compare original execution with replay
result = verifier.compare(
    original_trace=".agent-state/traces/sprint-042.trace",
    replay_trace=".agent-state/traces/sprint-042-replay.trace"
)

if not result.identical:
    print(f"Divergence at event {result.divergence_point}")
    print(f"Original: {result.original_event}")
    print(f"Replay: {result.replay_event}")
```

### Trace Format

```json
{
  "sprint_id": "042",
  "started_at": 1714234567,
  "prompt_versions": {
    "sprint-lead": "a1b2c3d4",
    "qa": "e5f6g7h8"
  },
  "events": [
    {
      "logical_time": 1,
      "type": "sprint_started",
      "data": {}
    },
    {
      "logical_time": 2,
      "type": "task_started",
      "data": {"task_id": "TASK-001"}
    }
  ]
}
```

---

## Debugging Non-Determinism

### Symptom: Replay Produces Different Results

**Check prompt versions:**
```bash
grep "prompt_versions" .agent-state/traces/*.trace
```

**Check for temperature violations:**
```bash
grep "temperature" .agent-state/events.jsonl
```

### Symptom: Events Out of Order

**Check logical timestamps:**
```python
with open(".agent-state/traces/sprint-042.trace") as f:
    trace = json.load(f)
    for event in trace["events"]:
        print(f"{event['logical_time']}: {event['type']}")
```

### Symptom: Composition Order Differs

**Check hash tie-breaker:**
```python
for item in items:
    h = hashlib.sha256(item["id"].encode()).hexdigest()[:12]
    print(f"{item['id']}: {h}")
```

---

## Best Practices

### DO

- Always use `clock.tick()` for local events
- Always use `clock.update()` when receiving remote events
- Record all external inputs (user responses, API calls)
- Use content hashing for any ordering decisions

### DON'T

- Use `datetime.now()` for event ordering
- Use `random.choice()` for tie-breaking
- Rely on dict/set iteration order
- Skip trace recording for "simple" operations

---

## Cross-References

- [CHECKPOINT_GUIDE.md](CHECKPOINT_GUIDE.md) — How determinism integrates with checkpoints
- [tests/test_phase4.py](../tests/test_phase4.py) — Determinism test suite
- [ARCHITECTURE.md](ARCHITECTURE.md) — Why Phase 4 exists
