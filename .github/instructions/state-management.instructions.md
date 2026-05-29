---
id: instruction.state-management
kind: instruction
version: 1.0.0
applies_to: '**'
description: state-management instruction
applyTo: '**'
---

# State Management & Durable Execution

**Phase 2 — ACID Guarantees & Checkpoint-Restart**

This instruction defines the migration from markdown-based state storage to a transactional database with ACID guarantees, enabling reliable checkpoint-restart and zero data loss.

---

## Problem Statement

### Current Issues with Markdown Storage

1. **No ACID Guarantees** — Concurrent writes corrupt data
2. **No Referential Integrity** — Orphaned cross-references
3. **Manual Invariant Checking** — Summary counts drift over time
4. **Brittle Parsing** — Markdown table parsing fragile to formatting
5. **No Query Optimization** — Full file scans for every lookup
6. **No Transactions** — Partial state updates leave inconsistent data

### Design Goals

1. **ACID Transactions** — All state changes atomic, consistent, isolated, durable
2. **Referential Integrity** — Foreign keys enforce cross-reference validity
3. **Automatic Invariants** — DB constraints enforce data integrity
4. **Efficient Queries** — Indexed lookups, no full scans
5. **Backward Compatible** — Dual-write mode during migration
6. **Human-Readable Exports** — Can still generate markdown views

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│          Application Layer                      │
│  (@planner, @sprint-lead, @bug)                 │
└────────────────┬────────────────────────────────┘
                 │ SQL API
                 ↓
┌─────────────────────────────────────────────────┐
│       State Management Layer                    │
│  • BacklogRepository                            │
│  • SprintRepository                             │
│  • ValidationRepository                         │
│  • Transactions & Locks                         │
└────────────────┬────────────────────────────────┘
                 │ SQLite
                 ↓
┌─────────────────────────────────────────────────┐
│       Database (agent-state.db)                 │
│  • ledger                                       │
│  • bugs                                         │
│  • rejections                                   │
│  • sprints                                      │
│  • checkpoints                                  │
└─────────────────────────────────────────────────┘
```

---

## Database Schema

### Core Tables

#### `ledger` — Canonical Backlog Status

```sql
CREATE TABLE ledger (
    item_id TEXT PRIMARY KEY,           -- ITEM-001, BUG-003, etc.
    type TEXT NOT NULL,                 -- feature | bug | debt | rejection | carry-over | migration | chore
    source_id TEXT,                     -- BUG-003, REJ-001, etc. (nullable for features)
    age INTEGER NOT NULL DEFAULT 0,     -- Sprints since created
    def INTEGER NOT NULL DEFAULT 0,     -- Deferral count
    sprint TEXT,                        -- Sprint assignment (nullable if open)
    status TEXT NOT NULL,               -- open | assigned | done | killed
    blocked BOOLEAN DEFAULT 0,          -- 1 = blocked, 0 = not blocked
    draft_path TEXT,                    -- Path to draft file (nullable)
    notes TEXT,                         -- Free-form notes
    created_at TEXT NOT NULL,           -- ISO 8601 timestamp
    updated_at TEXT NOT NULL,           -- ISO 8601 timestamp
    
    -- Constraints
    FOREIGN KEY (sprint) REFERENCES sprints(sprint_id),
    CHECK (type IN ('feature', 'bug', 'debt', 'rejection', 'carry-over', 'migration', 'chore')),
    CHECK (status IN ('open', 'assigned', 'done', 'killed')),
    CHECK (age >= 0),
    CHECK (def >= 0)
);

-- Indexes for common queries
CREATE INDEX idx_ledger_status ON ledger(status);
CREATE INDEX idx_ledger_sprint ON ledger(sprint);
CREATE INDEX idx_ledger_type ON ledger(type);
CREATE INDEX idx_ledger_def ON ledger(def);
CREATE INDEX idx_ledger_age ON ledger(age);
```

#### `bugs` — Bug Detail Store

```sql
CREATE TABLE bugs (
    bug_id TEXT PRIMARY KEY,            -- BUG-001
    ledger_item_id TEXT NOT NULL,       -- ITEM-007 (links to ledger)
    severity TEXT NOT NULL,             -- 🔴 | 🟡 | 🟢 | 🔵
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    reproduction_steps TEXT,
    observed TEXT NOT NULL,
    expected TEXT NOT NULL,
    impact TEXT,
    screenshot_path TEXT,               -- Path to screenshot (nullable)
    reported_by TEXT,
    reported_at TEXT NOT NULL,          -- ISO 8601 timestamp
    fixed_at TEXT,                      -- ISO 8601 timestamp (nullable)
    
    -- Constraints
    FOREIGN KEY (ledger_item_id) REFERENCES ledger(item_id),
    CHECK (severity IN ('🔴', '🟡', '🟢', '🔵'))
);

CREATE INDEX idx_bugs_severity ON bugs(severity);
CREATE INDEX idx_bugs_ledger_item ON bugs(ledger_item_id);
```

#### `rejections` — Handoff Rejection Detail Store

```sql
CREATE TABLE rejections (
    rejection_id TEXT PRIMARY KEY,      -- REJ-001
    ledger_item_id TEXT NOT NULL,       -- ITEM-012 (links to ledger)
    source_agent TEXT NOT NULL,         -- @pm | @architect
    target_agent TEXT NOT NULL,         -- @planner
    reason TEXT NOT NULL,               -- validation | scope | technical | resource
    rationale TEXT NOT NULL,
    original_request TEXT,              -- Brief summary of original request
    rejected_at TEXT NOT NULL,          -- ISO 8601 timestamp
    resolved_at TEXT,                   -- ISO 8601 timestamp (nullable)
    resolution TEXT,                    -- How it was resolved (nullable)
    
    -- Constraints
    FOREIGN KEY (ledger_item_id) REFERENCES ledger(item_id)
);

CREATE INDEX idx_rejections_reason ON rejections(reason);
CREATE INDEX idx_rejections_ledger_item ON rejections(ledger_item_id);
```

#### `sprints` — Sprint Metadata

```sql
CREATE TABLE sprints (
    sprint_id TEXT PRIMARY KEY,         -- 042
    sprint_number INTEGER NOT NULL,     -- 42
    status TEXT NOT NULL,               -- draft | in-progress | completed | archived
    plan_path TEXT NOT NULL,
    retro_path TEXT,                    -- NULL until retro written
    kickoff_commit_sha TEXT,
    completion_commit_sha TEXT,
    started_at TEXT,                    -- ISO 8601 timestamp (nullable)
    completed_at TEXT,                  -- ISO 8601 timestamp (nullable)
    forecast_complexity INTEGER,
    actual_complexity INTEGER,
    
    -- Constraints
    CHECK (status IN ('draft', 'in-progress', 'completed', 'archived')),
    CHECK (sprint_number > 0)
);

CREATE INDEX idx_sprints_status ON sprints(status);
CREATE INDEX idx_sprints_number ON sprints(sprint_number);
```

#### `checkpoints` — State Snapshots for Resume

```sql
CREATE TABLE checkpoints (
    checkpoint_id TEXT PRIMARY KEY,     -- sha256 hash of state
    sprint_id TEXT NOT NULL,
    phase TEXT NOT NULL,                -- planning | implementation | quality-gates | documentation
    state_json TEXT NOT NULL,           -- JSON blob of complete state
    artifact_paths TEXT NOT NULL,       -- JSON array of artifact paths
    created_at TEXT NOT NULL,           -- ISO 8601 timestamp
    
    -- Constraints
    FOREIGN KEY (sprint_id) REFERENCES sprints(sprint_id)
);

CREATE INDEX idx_checkpoints_sprint ON checkpoints(sprint_id);
CREATE INDEX idx_checkpoints_phase ON checkpoints(phase);
```

#### `validation_records` — PM Validation Results

```sql
CREATE TABLE validation_records (
    validation_id TEXT PRIMARY KEY,     -- Generated UUID
    feature_title TEXT NOT NULL,
    verdict TEXT NOT NULL,              -- VALIDATED | REFRAMED | NEW | REJECTED | DEFERRED
    rationale TEXT NOT NULL,
    tests TEXT NOT NULL,                -- JSON array of test results
    validated_by TEXT NOT NULL,         -- @pm
    validated_at TEXT NOT NULL,         -- ISO 8601 timestamp
    validation_path TEXT NOT NULL,      -- Path to markdown record
    
    -- Constraints
    CHECK (verdict IN ('VALIDATED', 'REFRAMED', 'NEW', 'REJECTED', 'DEFERRED'))
);

CREATE INDEX idx_validation_verdict ON validation_records(verdict);
```

---

## Migration Strategy

### Phase 1: Dual-Write Mode

Both markdown and SQLite updated simultaneously:

```python
def append_to_ledger(item: LedgerItem):
    # Write to database
    with db.transaction():
        db.execute("""
            INSERT INTO ledger (item_id, type, source_id, ...)
            VALUES (?, ?, ?, ...)
        """, item)
    
    # Also write to markdown (for backward compat)
    append_to_markdown_ledger(item)
```

### Phase 2: Verification Period

Compare markdown and SQLite outputs:

```python
def verify_consistency():
    md_items = parse_markdown_ledger()
    db_items = fetch_ledger_from_db()
    
    if md_items != db_items:
        raise InconsistencyError("Markdown and DB out of sync!")
```

### Phase 3: Cutover

1. Stop writing to markdown
2. Archive markdown files to `docs/archive/legacy-state/`
3. SQLite becomes source of truth
4. Markdown views generated on-demand for human readability

---

## Transactional Operations

### Example: Atomic Task Assignment

```python
@transaction
def assign_task_to_sprint(item_id: str, sprint_id: str):
    """Atomic assignment — either both succeed or both roll back."""
    
    # Update ledger status
    db.execute("""
        UPDATE ledger
        SET status = 'assigned', sprint = ?, updated_at = ?
        WHERE item_id = ? AND status = 'open'
    """, sprint_id, now(), item_id)
    
    if db.rows_affected == 0:
        raise ValueError(f"Item {item_id} not in 'open' status")
    
    # Increment sprint task count
    db.execute("""
        UPDATE sprints
        SET task_count = task_count + 1
        WHERE sprint_id = ?
    """, sprint_id)
    
    # Log event
    log_event("task.assigned", {"item_id": item_id, "sprint_id": sprint_id})
    
    # Transaction auto-commits on success, auto-rolls back on exception
```

### Example: Atomic Bug Triage + Ledger Append

```python
@transaction
def triage_bug(bug: Bug):
    """Atomic bug creation — bug + ledger entry created together."""
    
    # Generate IDs
    bug_id = generate_bug_id()
    item_id = generate_item_id()
    
    # Insert bug detail
    db.execute("""
        INSERT INTO bugs (bug_id, ledger_item_id, severity, title, ...)
        VALUES (?, ?, ?, ?, ...)
    """, bug_id, item_id, bug.severity, bug.title, ...)
    
    # Insert ledger entry
    db.execute("""
        INSERT INTO ledger (item_id, type, source_id, status, ...)
        VALUES (?, 'bug', ?, 'open', ...)
    """, item_id, bug_id, ...)
    
    # Both succeed or both roll back
```

---

## Checkpoint-Restart Protocol

### Creating Checkpoints

```python
def create_checkpoint(sprint_id: str, phase: str):
    """Create state snapshot for resume capability."""
    
    # Serialize full state
    state = {
        "ledger": fetch_ledger_snapshot(),
        "sprints": fetch_sprint_metadata(sprint_id),
        "phase_data": fetch_phase_specific_state(phase),
        "git_head": get_current_commit_sha(),
    }
    
    # Hash state for content-addressable storage
    state_json = json.dumps(state, sort_keys=True)
    checkpoint_id = hashlib.sha256(state_json.encode()).hexdigest()
    
    # Artifact paths (e.g., generated PLAN.md, brainstorms)
    artifacts = list_artifacts_created_this_phase()
    
    # Store checkpoint
    db.execute("""
        INSERT INTO checkpoints (checkpoint_id, sprint_id, phase, state_json, artifact_paths, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, checkpoint_id, sprint_id, phase, state_json, json.dumps(artifacts), now())
    
    log_event("checkpoint.created", {
        "checkpoint_id": checkpoint_id,
        "sprint_id": sprint_id,
        "phase": phase,
    })
```

### Resuming from Checkpoint

```python
def resume_from_checkpoint(checkpoint_id: str):
    """Resume sprint execution from saved state."""
    
    # Fetch checkpoint
    row = db.fetch_one("""
        SELECT state_json, artifact_paths, phase
        FROM checkpoints
        WHERE checkpoint_id = ?
    """, checkpoint_id)
    
    if not row:
        raise ValueError(f"Checkpoint {checkpoint_id} not found")
    
    # Restore state
    state = json.loads(row['state_json'])
    restore_ledger(state['ledger'])
    restore_sprint_metadata(state['sprints'])
    
    # Verify artifacts exist
    artifacts = json.loads(row['artifact_paths'])
    for path in artifacts:
        if not os.path.exists(path):
            raise ValueError(f"Artifact missing: {path}")
    
    # Resume from this phase
    log_event("checkpoint.resumed", {
        "checkpoint_id": checkpoint_id,
        "phase": row['phase'],
    })
    
    return row['phase']
```

---

## Invariant Enforcement

### Database Constraints

```sql
-- Cannot assign item to sprint if sprint is already completed
CREATE TRIGGER prevent_assign_to_completed_sprint
BEFORE UPDATE ON ledger
WHEN NEW.sprint IS NOT NULL
BEGIN
    SELECT RAISE(ABORT, 'Cannot assign to completed sprint')
    WHERE EXISTS (
        SELECT 1 FROM sprints
        WHERE sprint_id = NEW.sprint AND status = 'completed'
    );
END;

-- Cannot mark sprint complete if it has open tasks
CREATE TRIGGER prevent_complete_with_open_tasks
BEFORE UPDATE ON sprints
WHEN NEW.status = 'completed' AND OLD.status != 'completed'
BEGIN
    SELECT RAISE(ABORT, 'Cannot complete sprint with open tasks')
    WHERE EXISTS (
        SELECT 1 FROM ledger
        WHERE sprint = NEW.sprint_id AND status = 'assigned'
    );
END;

-- Def must increment when item is deferred
CREATE TRIGGER increment_def_on_defer
AFTER UPDATE ON ledger
WHEN OLD.status = 'assigned' AND NEW.status = 'open' AND NEW.sprint IS NULL
BEGIN
    UPDATE ledger
    SET def = def + 1
    WHERE item_id = NEW.item_id;
END;
```

### Application-Level Checks

```python
def validate_ledger_invariants():
    """Run invariant checks (for auditing/testing)."""
    
    errors = []
    
    # Check: No item in 'assigned' status without sprint
    orphans = db.fetch_all("""
        SELECT item_id FROM ledger
        WHERE status = 'assigned' AND sprint IS NULL
    """)
    if orphans:
        errors.append(f"Orphaned assignments: {orphans}")
    
    # Check: All source_ids reference valid bugs or rejections
    invalid_refs = db.fetch_all("""
        SELECT l.item_id, l.source_id
        FROM ledger l
        WHERE l.source_id IS NOT NULL
        AND l.source_id NOT IN (SELECT bug_id FROM bugs)
        AND l.source_id NOT IN (SELECT rejection_id FROM rejections)
    """)
    if invalid_refs:
        errors.append(f"Invalid source references: {invalid_refs}")
    
    # Check: Summary counts match table counts
    counts = db.fetch_one("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open,
            SUM(CASE WHEN status = 'assigned' THEN 1 ELSE 0 END) as assigned
        FROM ledger
    """)
    # Compare with stored summary...
    
    if errors:
        raise InvariantViolation("\n".join(errors))
```

---

## Workflow Integration

### @planner Composition

```python
def compose_sprint(constraints: CompositionConstraints) -> Composition:
    """Compose sprint using transactional database queries."""
    
    with db.transaction():
        # Fetch P0 items (mandatory)
        p0_items = db.fetch_all("""
            SELECT * FROM ledger
            WHERE def >= ? AND status = 'open'
            ORDER BY age DESC
        """, constraints.def_p0_threshold)
        
        # Fetch validated features
        features = db.fetch_all("""
            SELECT l.* FROM ledger l
            JOIN validation_records v ON v.feature_title = l.notes
            WHERE l.type = 'feature' AND l.status = 'open' AND v.verdict = 'VALIDATED'
            ORDER BY (l.age - l.def) DESC
        """)
        
        # Fetch bugs by severity
        bugs = db.fetch_all("""
            SELECT l.*, b.severity FROM ledger l
            JOIN bugs b ON b.ledger_item_id = l.item_id
            WHERE l.type = 'bug' AND l.status = 'open'
            ORDER BY
                CASE b.severity
                    WHEN '🔴' THEN 1
                    WHEN '🟡' THEN 2
                    WHEN '🟢' THEN 3
                    WHEN '🔵' THEN 4
                END,
                l.age DESC
        """)
        
        # Apply composition algorithm...
        composition = apply_composition_rules(p0_items, features, bugs, constraints)
        
        return composition
```

### @sprint-lead Carry-Over

```python
def handle_carry_over(sprint_id: str):
    """Move incomplete tasks to ledger as carry-overs."""
    
    with db.transaction():
        # Fetch incomplete tasks
        incomplete = db.fetch_all("""
            SELECT * FROM ledger
            WHERE sprint = ? AND status = 'assigned'
        """, sprint_id)
        
        for item in incomplete:
            # Create carry-over entry
            carry_id = generate_item_id()
            db.execute("""
                INSERT INTO ledger (item_id, type, source_id, age, def, status, notes, ...)
                VALUES (?, 'carry-over', ?, ?, ?, 'open', ?, ...)
            """, carry_id, item['item_id'], item['age'] + 1, item['def'] + 1, f"Carry-over from Sprint {sprint_id}")
            
            # Mark original as 'done' (virtual completion)
            db.execute("""
                UPDATE ledger
                SET status = 'done', notes = notes || ' [carried over to ' || ? || ']'
                WHERE item_id = ?
            """, carry_id, item['item_id'])
            
            log_event("task.carried_over", {
                "original": item['item_id'],
                "carry_over": carry_id,
                "sprint": sprint_id,
            })
```

---

## Export to Markdown (Human-Readable Views)

Generate markdown on-demand for human review:

```python
def export_ledger_to_markdown() -> str:
    """Generate markdown view of ledger (read-only)."""
    
    items = db.fetch_all("""
        SELECT * FROM ledger
        ORDER BY
            CASE status
                WHEN 'open' THEN 1
                WHEN 'assigned' THEN 2
                WHEN 'done' THEN 3
                WHEN 'killed' THEN 4
            END,
            item_id
    """)
    
    md = "# Backlog Ledger\n\n"
    md += "| ID | Type | Source | Age | Def | Sprint | Status | Blocked | Draft | Notes |\n"
    md += "|----|------|--------|-----|-----|--------|--------|---------|-------|-------|\n"
    
    for item in items:
        md += f"| {item['item_id']} | {item['type']} | {item['source_id'] or '—'} | ..."
    
    return md
```

---

## Configuration

Add to `project.config.yml`:

```yaml
state_management:
  backend: "sqlite"              # sqlite | postgres (future)
  database_path: ".agent-state/agent-state.db"
  enable_dual_write: false       # true during migration
  checkpoint_frequency: "phase"  # phase | task | manual
  auto_vacuum: true
  wal_mode: true                 # Write-Ahead Logging for concurrency
```

---

## References

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [ACID Properties](https://en.wikipedia.org/wiki/ACID)
- [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/durable-execution)
- [Temporal Durable Execution](https://temporal.io/)
