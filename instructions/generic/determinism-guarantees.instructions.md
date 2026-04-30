# Determinism Guarantees

**Phase 4 — Reproducible Agent Execution**

This instruction establishes formal determinism guarantees for agent-homebase, enabling bit-identical replay, reproducible composition, and verifiable outcomes.

---

## Determinism Principles

1. **Same Inputs → Same Outputs** — Identical config and state produce identical results
2. **No Hidden State** — All state explicitly tracked and versioned
3. **Logical Time** — No dependency on wall-clock time or system timing
4. **Seeded Randomness** — All stochastic operations deterministically seeded
5. **Versioned Prompts** — Prompt changes detected via cryptographic hashing
6. **Verifiable Replay** — Past executions reproducible for auditing

---

## Sources of Non-Determinism

### Currently Non-Deterministic

| Source | Impact | Mitigation |
|--------|--------|------------|
| LLM sampling | Different outputs per run | Enforce `temperature=0.0` |
| Wall-clock time | Phase timing varies | Use logical time (Lamport timestamps) |
| Prompt drift | Skills change → outputs change | Version prompts (SHA256 hashes) |
| Git log parsing | Commit order varies | Use ref-based checkpoints |
| Filesystem race conditions | File read order undefined | Deterministic directory traversal |
| Composition tie-breaking | ITEM-NNN order arbitrary | Use content-based hashing |

### Intentionally Non-Deterministic

| Source | Rationale |
|--------|-----------|
| User overrides | Human judgment overrides composition rules |
| Interactive checkpoints | User input at EXIT POINTs changes flow |
| Adaptive complexity | Subagent assesses complexity based on context |

---

## LLM Determinism

### Temperature Enforcement

**Rule:** All LLM calls MUST use `temperature=0.0` for deterministic sampling.

**Enforcement in Skills:**

```markdown
## LLM Configuration

When invoking LLM APIs, ALWAYS use these settings:
- `temperature: 0.0` (REQUIRED for determinism)
- `top_p: 1.0`
- `frequency_penalty: 0.0`
- `presence_penalty: 0.0`

Example (OpenAI):
```python
response = client.chat.completions.create(
    model="gpt-4-turbo",
    temperature=0.0,  # Deterministic sampling
    messages=[...]
)
```

**Validation:**

Add runtime assertion in agent platform integration:

```python
def validate_llm_params(params):
    if params.get('temperature', 1.0) != 0.0:
        raise DeterminismViolation(
            f"LLM call with non-zero temperature: {params['temperature']}\n"
            "All LLM calls must use temperature=0.0 for determinism."
        )
```

### Prompt Versioning

**Problem:** Skills change → prompts change → outputs change (silently)

**Solution:** Hash resolved prompts to detect changes.

**Implementation:**

```python
def invoke_subagent(task: Task, skill: Skill) -> Result:
    # Render prompt from template
    prompt = render_skill_template(skill, task)
    
    # Hash prompt for versioning
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:12]
    
    # Log hash with trace
    log_event("subagent.invoked", {
        "task_id": task.id,
        "skill": skill.name,
        "prompt_version": prompt_hash,  # <-- Version tracking
    })
    
    # Invoke LLM
    result = llm_call(prompt, temperature=0.0)
    
    return result
```

**Verification:**

```bash
# Check if prompt changed between runs
cat .agent-state/events.jsonl | jq -r 'select(.event_type == "subagent.invoked") | "\(.task_id): \(.prompt_version)"'

# Example output:
# task-1: a3f2b9c1e5d7
# task-1: a3f2b9c1e5d7  <-- Same hash = same prompt
```

If hashes differ → prompt changed → replay will differ.

---

## Logical Time (Lamport Timestamps)

### Problem with Wall-Clock Time

Wall-clock time is non-deterministic:
- Machine load affects execution speed
- Parallel operations have undefined ordering
- Replay produces different timestamps

### Solution: Logical Time

Use **Lamport timestamps** for event ordering:

```python
class LogicalClock:
    def __init__(self):
        self.counter = 0
        self.lock = threading.Lock()
    
    def tick(self) -> int:
        """Increment clock and return new timestamp."""
        with self.lock:
            self.counter += 1
            return self.counter
    
    def update(self, remote_time: int):
        """Update clock from remote event (Lamport rule)."""
        with self.lock:
            self.counter = max(self.counter, remote_time) + 1
            return self.counter

# Global logical clock
clock = LogicalClock()

# Use in events
log_event("phase.started", {
    "phase": "implementation",
    "logical_time": clock.tick(),  # Deterministic ordering
    "wall_time": datetime.now(),   # For human reference only
})
```

### Event Ordering

Events ordered by logical time, not wall time:

```python
def reconstruct_event_sequence(events):
    """Replay events in deterministic order."""
    # Sort by logical time (not wall time)
    sorted_events = sorted(events, key=lambda e: e['logical_time'])
    
    for event in sorted_events:
        replay_event(event)
```

---

## Deterministic Composition

### Problem: Tie-Breaking Ambiguity

When two items have identical scores, which is selected first?

**Current (non-deterministic):**
```python
# Tie-breaking by ITEM-NNN order (arbitrary)
items.sort(key=lambda item: (item.score, item.id))  # ❌ Not content-based
```

**Solution (deterministic):**
```python
def content_hash(item) -> str:
    """Hash item content for deterministic tie-breaking."""
    content = f"{item.type}|{item.source_id}|{item.notes}|{item.created_at}"
    return hashlib.sha256(content.encode()).hexdigest()

# Tie-breaking by content hash
items.sort(key=lambda item: (item.score, content_hash(item)))  # ✓ Deterministic
```

### Composition Snapshot

Capture full input state before composition:

```python
def compose_sprint(constraints):
    # Snapshot ledger state
    snapshot = {
        "ledger": db.fetch_all("SELECT * FROM ledger WHERE status = 'open'"),
        "constraints": constraints.__dict__,
        "config": load_config_tokens(),
        "timestamp": clock.tick(),  # Logical time
    }
    
    # Hash snapshot for content-addressable storage
    snapshot_json = json.dumps(snapshot, sort_keys=True)
    snapshot_hash = hashlib.sha256(snapshot_json.encode()).hexdigest()
    
    # Store snapshot
    store_composition_snapshot(snapshot_hash, snapshot_json)
    
    # Run composition
    composition = apply_composition_algorithm(snapshot)
    
    return composition, snapshot_hash
```

### Replay Verification

Replay composition from snapshot and verify identical output:

```python
def verify_composition_determinism(snapshot_hash):
    # Load snapshot
    snapshot = load_composition_snapshot(snapshot_hash)
    
    # Replay composition
    composition_v1 = apply_composition_algorithm(snapshot)
    composition_v2 = apply_composition_algorithm(snapshot)  # Run again
    
    # Verify bit-identical
    assert composition_v1 == composition_v2, "Composition is non-deterministic!"
    
    log_event("composition.verified", {
        "snapshot_hash": snapshot_hash,
        "deterministic": True,
    })
```

---

## Git State Hardening

### Problem: Fragile Git Log Parsing

Current resume protocol uses `git log --grep='Sprint N'`:
- Fragile to commit message format changes
- Breaks if history is rebased
- Parsing logic brittle

### Solution: Ref-Based Checkpoints

Store checkpoint metadata in `.agent-state/` directory:

```python
def create_checkpoint(sprint_id: str, phase: str):
    """Create checkpoint with ref-based metadata."""
    
    # Get current commit SHA
    commit_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
    
    # Checkpoint metadata
    metadata = {
        "sprint_id": sprint_id,
        "phase": phase,
        "commit_sha": commit_sha,
        "timestamp": datetime.now().isoformat(),
        "logical_time": clock.tick(),
        "state_hash": compute_state_hash(),  # Content-addressable
    }
    
    # Store metadata
    checkpoint_path = f".agent-state/checkpoints/{sprint_id}-{phase}.json"
    with open(checkpoint_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Also store in database for querying
    db.execute("""
        INSERT INTO checkpoints (checkpoint_id, sprint_id, phase, commit_sha, state_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, metadata['state_hash'], sprint_id, phase, commit_sha, json.dumps(metadata), now())
    
    log_event("checkpoint.created", metadata)
```

### Resume Protocol (Hardened)

```python
def resume_sprint(sprint_id: str):
    """Resume from checkpoint using ref-based metadata."""
    
    # Find latest checkpoint for sprint
    checkpoint = db.fetch_one("""
        SELECT * FROM checkpoints
        WHERE sprint_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, sprint_id)
    
    if not checkpoint:
        raise ValueError(f"No checkpoint found for sprint {sprint_id}")
    
    # Verify we're at the right commit
    current_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
    if current_sha != checkpoint['commit_sha']:
        print(f"⚠ Checkpoint at {checkpoint['commit_sha']}, current at {current_sha}")
        print("  Run: git checkout {checkpoint['commit_sha']} to resume from checkpoint")
    
    # Restore state
    state = json.loads(checkpoint['state_json'])
    restore_state(state)
    
    log_event("sprint.resumed", {
        "sprint_id": sprint_id,
        "phase": checkpoint['phase'],
        "checkpoint_id": checkpoint['checkpoint_id'],
    })
    
    return checkpoint['phase']
```

---

## Filesystem Determinism

### Problem: Directory Traversal Order

`os.listdir()` and `Path.glob()` return files in undefined order (filesystem-dependent).

**Non-deterministic:**
```python
for skill_md in Path("skills").rglob("*.skill.md"):  # ❌ Order undefined
    process_skill(skill_md)
```

**Deterministic:**
```python
for skill_md in sorted(Path("skills").rglob("*.skill.md")):  # ✓ Lexicographic order
    process_skill(skill_md)
```

**Enforcement:**

Add linter rule to detect unsorted glob/listdir:

```python
# .pylintrc or ruff.toml
[tool.ruff.lint.flake8-pathlib]
check-sorted-glob = true  # Require sorted() on glob/rglob
```

---

## Regression Testing

### Determinism Test Suite

```python
def test_composition_determinism():
    """Verify composition produces identical results on replay."""
    
    # Create snapshot
    snapshot = create_composition_snapshot()
    
    # Run composition 100 times
    results = []
    for _ in range(100):
        composition = apply_composition_algorithm(snapshot)
        results.append(hash_composition(composition))
    
    # All hashes must be identical
    assert len(set(results)) == 1, "Composition is non-deterministic!"

def test_prompt_versioning():
    """Verify prompt changes are detected."""
    
    # Render prompt
    prompt_v1 = render_skill_template(skill, task)
    hash_v1 = hash_prompt(prompt_v1)
    
    # Modify skill template
    modify_skill_template(skill)
    
    # Render again
    prompt_v2 = render_skill_template(skill, task)
    hash_v2 = hash_prompt(prompt_v2)
    
    # Hashes must differ
    assert hash_v1 != hash_v2, "Prompt change not detected!"

def test_logical_time_ordering():
    """Verify events ordered by logical time."""
    
    events = [
        {"logical_time": 5, "name": "C"},
        {"logical_time": 2, "name": "A"},
        {"logical_time": 8, "name": "D"},
        {"logical_time": 3, "name": "B"},
    ]
    
    sorted_events = sorted(events, key=lambda e: e['logical_time'])
    names = [e['name'] for e in sorted_events]
    
    assert names == ["A", "B", "C", "D"], "Events not ordered by logical time!"
```

### CI/CD Integration

```yaml
# .github/workflows/determinism-tests.yml
name: Determinism Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run determinism test suite
        run: pytest tests/test_determinism.py -v
      
      - name: Verify composition replay
        run: python scripts/verify_composition_determinism.py
      
      - name: Check prompt versioning
        run: python scripts/check_prompt_hashes.py
```

---

## Debugging Non-Determinism

### Replay with Diff

```bash
# Run sprint twice and compare
python sprint.py --config sprint-042.yml --output run1/
python sprint.py --config sprint-042.yml --output run2/

# Diff outputs
diff -r run1/ run2/

# If outputs differ, investigate:
# - Check LLM temperature settings
# - Check for wall-clock time dependencies
# - Check for unsorted filesystem operations
# - Check for unversioned prompt changes
```

### Trace Comparison

```python
def compare_traces(trace1, trace2):
    """Compare two traces to identify non-determinism source."""
    
    for span1, span2 in zip(trace1.spans, trace2.spans):
        # Compare span attributes
        if span1.attributes != span2.attributes:
            print(f"⚠ Span '{span1.name}' differs:")
            print(f"  Run 1: {span1.attributes}")
            print(f"  Run 2: {span2.attributes}")
            
            # Identify which attribute changed
            for key in span1.attributes:
                if span1.attributes[key] != span2.attributes[key]:
                    print(f"  → Non-determinism in attribute: {key}")
```

---

## Configuration

Add to `project.config.yml`:

```yaml
determinism:
  enforce_temperature_zero: true     # Block LLM calls with temp != 0
  use_logical_time: true             # Use Lamport timestamps
  prompt_versioning: true            # Hash prompts for version tracking
  composition_snapshots: true        # Store composition inputs
  verify_replay: true                # Run determinism tests in CI
  seed: 42                           # RNG seed (if any stochastic ops)
```

---

## Success Metrics

**Determinism Verification:**
- [ ] Composition produces identical output on 1000 replays
- [ ] Prompt changes detected via hash mismatch
- [ ] Event ordering stable across replays (logical time)
- [ ] Resume protocol works after git history rewrite
- [ ] CI/CD determinism tests pass

**No Non-Determinism:**
- [ ] All LLM calls use `temperature=0.0`
- [ ] No wall-clock time in critical paths
- [ ] All filesystem operations sorted
- [ ] All tie-breaking uses content hashing

---

## References

- [Temporal Determinism](https://temporal.io/)
- [Lamport Timestamps](https://en.wikipedia.org/wiki/Lamport_timestamp)
- [Deterministic Simulation Testing](https://www.foundationdb.org/files/simulation.pdf)
- [Content-Addressable Storage](https://en.wikipedia.org/wiki/Content-addressable_storage)
