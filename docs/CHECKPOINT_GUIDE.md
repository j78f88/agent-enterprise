# Checkpoint Guide

How to use the checkpoint-restart system for durable execution and recovery.

---

## Overview

Phase 2 checkpoints enable:

- **Resume-safe execution**: Continue from any saved state
- **Failure recovery**: Rollback to last known good state
- **Debugging**: Inspect state at any phase boundary
- **Audit trail**: Track state changes over time

---

## Creating Checkpoints

### Automatic Checkpoints

@sprint-lead creates checkpoints automatically at phase boundaries:

| Phase | Checkpoint Name |
|-------|-----------------|
| Kickoff complete | `sprint-{N}-kickoff` |
| Task complete | `sprint-{N}-task-{M}` |
| Gates complete | `sprint-{N}-validation` |
| Review complete | `sprint-{N}-review` |
| Sprint complete | `sprint-{N}-complete` |

### Manual Checkpoints

```python
from src.phase2_durability.checkpoint import CheckpointManager
from src.phase2_durability.db import Database

db = Database(".agent-state/agent.db")
manager = CheckpointManager(db, sprint_id="042")

# Create checkpoint
checkpoint_id = manager.create_checkpoint(
    phase="mid-implementation",
    state=current_state,
    artifacts=["docs/planning/BACKLOG_LEDGER.md"]
)
# Returns: "chk-042-1714234567-a1b2c3"
```

---

## Checkpoint Contents

Each checkpoint stores:

```python
@dataclass
class CheckpointState:
    sprint_id: str              # "042"
    phase: str                  # "implementation"
    fsm_state: str              # "IMPLEMENTATION"
    logical_time: int           # Lamport timestamp
    context: Dict[str, Any]     # Sprint context data
    ledger_items: List[Dict]    # Backlog state
    active_tasks: List[Dict]    # In-progress tasks
    completed_tasks: List[Dict] # Finished tasks
    environment: Dict[str, str] # Config snapshot
    metadata: Dict[str, Any]    # Prompt versions, etc.
    
    # Phase 3 additions
    active_sandboxes: List[Dict]  # Running containers
    sandbox_history: List[Dict]   # All sandboxes used
```

---

## Restoring Checkpoints

### Restore to Latest

```python
# Get most recent checkpoint for sprint
latest = manager.get_latest_checkpoint()
state = manager.restore_checkpoint(latest.checkpoint_id)

print(f"Restored to phase: {state.phase}")
print(f"FSM state: {state.fsm_state}")
print(f"Logical time: {state.logical_time}")
```

### Restore to Specific Checkpoint

```python
# List available checkpoints
checkpoints = manager.list_checkpoints()
for cp in checkpoints:
    print(f"{cp.checkpoint_id}: {cp.phase} at {cp.created_at}")

# Restore specific checkpoint
state = manager.restore_checkpoint("chk-042-1714234567-a1b2c3")
```

### Restore with Verification

```python
state, verified = manager.restore_checkpoint_verified(checkpoint_id)

if not verified:
    print("WARNING: Checkpoint may be corrupted")
    print(f"Expected hash: {expected}")
    print(f"Actual hash: {actual}")
```

---

## Checkpoint Storage

### File Structure

```
.agent-state/
├── agent.db                    # SQLite database
├── checkpoints/
│   ├── chk-042-1714234567-a1b2c3.json.gz
│   ├── chk-042-1714234890-d4e5f6.json.gz
│   └── ...
└── events.jsonl                # Event log
```

### Compression

Checkpoints are gzip-compressed:
- Typical compression ratio: 5-10x
- 100KB state → ~15KB on disk

### Content Addressing

Each checkpoint has a SHA256 hash:
- Used for integrity verification
- Enables deduplication
- Supports diff operations

---

## Common Operations

### Resume Interrupted Sprint

```python
# 1. Find latest checkpoint
latest = manager.get_latest_checkpoint()

# 2. Restore state
state = manager.restore_checkpoint(latest.checkpoint_id)

# 3. Resume from restored state
sprint_lead.resume_from_state(state)
```

### Rollback After Failure

```python
# 1. List checkpoints for sprint
checkpoints = manager.list_checkpoints()

# 2. Find last successful checkpoint
good_checkpoint = None
for cp in reversed(checkpoints):
    if cp.phase != "failed":
        good_checkpoint = cp
        break

# 3. Restore and retry
if good_checkpoint:
    state = manager.restore_checkpoint(good_checkpoint.checkpoint_id)
    sprint_lead.retry_from_state(state)
```

### Compare Checkpoints (Diff)

```python
diff = manager.diff_checkpoints(
    checkpoint_a="chk-042-1714234567-a1b2c3",
    checkpoint_b="chk-042-1714234890-d4e5f6"
)

print(f"Tasks completed: {diff.tasks_delta}")
print(f"Files changed: {diff.files_changed}")
print(f"Time elapsed: {diff.time_delta}")
```

### Delete Old Checkpoints

```python
# Keep only last 5 checkpoints per sprint
manager.cleanup(keep_latest=5)

# Delete all checkpoints for a sprint
manager.delete_sprint_checkpoints("042")
```

---

## Integration with FSM

Checkpoints are tied to FSM state transitions:

```
PLANNING → APPROVED
    ↓ checkpoint: sprint-042-approved
    
APPROVED → IMPLEMENTATION  
    ↓ checkpoint: sprint-042-impl-start
    
IMPLEMENTATION → IMPLEMENTATION (task complete)
    ↓ checkpoint: sprint-042-task-001
    ↓ checkpoint: sprint-042-task-002
    
IMPLEMENTATION → COMPLETE
    ↓ checkpoint: sprint-042-impl-done
```

---

## Integration with Sandbox (Phase 3)

Checkpoints include sandbox state:

```python
state = manager.restore_checkpoint(checkpoint_id)

# Restore sandboxes
for sandbox_state in state.active_sandboxes:
    sandbox_manager.restore_sandbox(sandbox_state)
```

---

## Troubleshooting

### "Checkpoint not found"

```python
# List all checkpoints to verify ID
for cp in manager.list_checkpoints():
    print(cp.checkpoint_id)
```

### "Checkpoint corrupted"

```python
# Verify integrity
result = manager.verify_checkpoint(checkpoint_id)
if not result.valid:
    print(f"Corruption detected: {result.error}")
    # Try previous checkpoint
```

### "Cannot restore: incompatible version"

Checkpoint schema may have changed between library versions:

```python
# Check checkpoint version
metadata = manager.get_checkpoint_metadata(checkpoint_id)
print(f"Checkpoint version: {metadata.schema_version}")
print(f"Current version: {CURRENT_SCHEMA_VERSION}")
```

### Database Locked

```bash
# Check for other processes
lsof .agent-state/agent.db

# Force unlock (last resort)
sqlite3 .agent-state/agent.db "PRAGMA wal_checkpoint(TRUNCATE);"
```

---

## Best Practices

### DO

- Create checkpoints at phase boundaries
- Verify checkpoint integrity after creation
- Clean up old checkpoints periodically
- Test restore procedures before relying on them

### DON'T

- Create checkpoints mid-task (inconsistent state)
- Delete checkpoints without verification
- Modify checkpoint files manually
- Share checkpoints between different config versions

---

## Configuration

In `project.config.yml`:

```yaml
checkpoints:
  enabled: true
  directory: ".agent-state/checkpoints"
  compression: true
  retention_count: 10          # Keep last N per sprint
  retention_days: 30           # Delete older than N days
  verify_on_create: true       # Hash verification
  verify_on_restore: true      # Integrity check on load
```

---

## Cross-References

- [DETERMINISM_GUIDE.md](DETERMINISM_GUIDE.md) — How checkpoints integrate with logical time
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) — Migrating checkpoint data
- [tests/test_phase2.py](../tests/test_phase2.py) — Checkpoint test suite
