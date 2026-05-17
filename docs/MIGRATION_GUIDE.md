# Migration Guide

How to migrate from markdown-based storage to SQLite, with safety guarantees and rollback procedures.

---

## Overview

Phase 2 introduces SQLite persistence as an alternative to markdown files. The migration supports:

- **Dual-write mode**: Write to both formats during transition
- **Bidirectional conversion**: Markdown ↔ SQLite
- **Consistency checking**: Verify data integrity
- **Rollback**: Return to markdown-only if needed

---

## Migration Phases

| Phase | Duration | Behavior |
|-------|----------|----------|
| **1. Preparation** | 1 sprint | Backup, verify prerequisites |
| **2. Dual-write** | 2-3 sprints | Write to both, read from markdown |
| **3. Validation** | 1 sprint | Verify SQLite matches markdown |
| **4. Cutover** | - | Switch to SQLite-only |
| **5. Cleanup** | - | Archive markdown files |

---

## Phase 1: Preparation

### Prerequisites

```bash
# Verify SQLite is available
python -c "import sqlite3; print(sqlite3.sqlite_version)"
# Expected: 3.35.0 or higher

# Backup existing markdown files
cp -r docs/planning docs/planning.backup
cp SPRINTS.md SPRINTS.md.backup
```

### Run Pre-Migration Check

```python
from src.phase2_durability.migrate import MigrationChecker

checker = MigrationChecker()
result = checker.check_prerequisites()

if result.ready:
    print("✓ Ready for migration")
else:
    print("✗ Issues found:")
    for issue in result.issues:
        print(f"  - {issue}")
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "BACKLOG_LEDGER.md has invalid format" | Fix table syntax per backlog-ledger.instructions.md |
| "BUG_BACKLOG.md has unparseable entries" | Ensure entries follow bug-backlog-format.instructions.md |
| "SPRINTS.md missing required fields" | Add Status and Type to each sprint entry |

---

## Phase 2: Dual-Write Mode

### Enable Dual-Write

In `project.config.yml`:

```yaml
storage:
  mode: "dual-write"      # Options: markdown | sqlite | dual-write
  primary: "markdown"     # Source of truth during transition
  sqlite_path: ".agent-state/agent.db"
```

### How Dual-Write Works

```
Write Operation:
    ↓
┌───────────────────┐
│  Write to         │
│  Markdown (sync)  │
└─────────┬─────────┘
          ↓
┌───────────────────┐
│  Write to         │
│  SQLite (sync)    │
└───────────────────┘

Read Operation:
    ↓
┌───────────────────┐
│  Read from        │
│  Markdown         │  ← Primary during transition
└───────────────────┘
```

### Verify Dual-Write

After each sprint, verify both stores match:

```python
from src.phase2_durability.migrate import ConsistencyChecker

checker = ConsistencyChecker()
result = checker.verify_consistency()

if result.consistent:
    print("✓ Markdown and SQLite match")
else:
    print("✗ Inconsistencies found:")
    for diff in result.differences:
        print(f"  - {diff.table}: {diff.description}")
```

---

## Phase 3: Validation

### Full Data Comparison

```python
from src.phase2_durability.migrate import Migrator

migrator = Migrator()

# Compare all data
comparison = migrator.full_comparison()

print(f"Ledger items: {comparison.ledger.markdown_count} md, {comparison.ledger.sqlite_count} db")
print(f"Bug entries: {comparison.bugs.markdown_count} md, {comparison.bugs.sqlite_count} db")
print(f"Sprint records: {comparison.sprints.markdown_count} md, {comparison.sprints.sqlite_count} db")

if comparison.all_match:
    print("✓ All data matches - ready for cutover")
```

### Test Read from SQLite

Temporarily switch reads to SQLite while keeping writes to both:

```yaml
storage:
  mode: "dual-write"
  primary: "sqlite"       # Read from SQLite
```

Run a test sprint and verify behavior is identical.

---

## Phase 4: Cutover

### Switch to SQLite-Only

```yaml
storage:
  mode: "sqlite"
  sqlite_path: ".agent-state/agent.db"
```

### Post-Cutover Verification

```python
from src.phase2_durability.db import Database

db = Database(".agent-state/agent.db")

# Verify tables exist
tables = db.list_tables()
expected = ["ledger", "bugs", "rejections", "sprints", "checkpoints", "validation_records"]
assert all(t in tables for t in expected)

# Verify data counts
print(f"Ledger items: {db.count('ledger')}")
print(f"Bug entries: {db.count('bugs')}")
print(f"Sprint records: {db.count('sprints')}")
```

---

## Phase 5: Cleanup

### Archive Markdown Files

```bash
# Create archive directory
mkdir -p docs/archive/pre-migration

# Move old markdown files
mv docs/planning/BACKLOG_LEDGER.md docs/archive/pre-migration/
mv docs/planning/BUG_BACKLOG.md docs/archive/pre-migration/
mv docs/planning/HANDOFF_REJECTIONS.md docs/archive/pre-migration/

# Keep SPRINTS.md for human reference (optional)
# It can be regenerated from SQLite if needed
```

### Verify Archive

```bash
# Confirm archived files are intact
ls -la docs/archive/pre-migration/

# Confirm system still works
pytest tests/test_phase2.py -v
```

---

## Rollback Procedures

### During Dual-Write (No Data Loss)

```yaml
# Simply switch back to markdown-only
storage:
  mode: "markdown"
```

### After Cutover (Export from SQLite)

```python
from src.phase2_durability.migrate import Migrator

migrator = Migrator()

# Export SQLite to markdown
migrator.export_to_markdown(
    db_path=".agent-state/agent.db",
    output_dir="docs/planning/"
)

# Verify export
assert Path("docs/planning/BACKLOG_LEDGER.md").exists()
assert Path("docs/planning/BUG_BACKLOG.md").exists()

# Switch config
# storage:
#   mode: "markdown"
```

---

## Database Schema

### Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `ledger` | Backlog items | id, type, source, status, age, def_count |
| `bugs` | Bug reproduction | bug_id, severity, description, steps |
| `rejections` | Handoff rejections | rejection_id, reason, original_request |
| `sprints` | Sprint tracking | sprint_id, status, started, completed |
| `checkpoints` | State snapshots | checkpoint_id, phase, state_hash |
| `validation_records` | Quality results | sprint_id, gate, passed, details |

### WAL Mode

SQLite is configured with Write-Ahead Logging for:
- Concurrent reads during writes
- Crash recovery
- Better performance

```sql
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
```

---

## Troubleshooting

### "Migration failed: foreign key constraint"

Data references non-existent parent:

```python
# Find orphaned references
db.execute("""
    SELECT * FROM ledger 
    WHERE source LIKE 'BUG-%' 
    AND source NOT IN (SELECT bug_id FROM bugs)
""")
```

### "Dual-write out of sync"

Reset SQLite and re-import:

```python
migrator = Migrator()

# Clear SQLite
db.execute("DELETE FROM ledger")
db.execute("DELETE FROM bugs")

# Re-import from markdown
migrator.import_from_markdown("docs/planning/")
```

### "SQLite database locked"

```bash
# Check for other processes
lsof .agent-state/agent.db

# Force checkpoint (releases WAL lock)
sqlite3 .agent-state/agent.db "PRAGMA wal_checkpoint(TRUNCATE);"
```

### "Markdown export has wrong format"

Templates may have changed. Regenerate with current templates:

```python
migrator.export_to_markdown(
    db_path=".agent-state/agent.db",
    output_dir="docs/planning/",
    template_version="current"
)
```

---

## Best Practices

### DO

- Complete 2-3 sprints in dual-write before cutover
- Verify consistency after each sprint
- Keep markdown backups for at least 30 days post-cutover
- Test rollback procedure before cutover

### DON'T

- Skip the validation phase
- Delete markdown files immediately after cutover
- Modify SQLite directly without going through the API
- Run migration during an active sprint

---

## Configuration Reference

```yaml
storage:
  # Storage mode
  mode: "dual-write"          # markdown | sqlite | dual-write
  
  # Which store to read from (dual-write only)
  primary: "markdown"         # markdown | sqlite
  
  # SQLite settings
  sqlite_path: ".agent-state/agent.db"
  sqlite_wal_mode: true
  sqlite_foreign_keys: true
  
  # Migration settings
  migration:
    auto_backup: true
    backup_dir: "docs/archive/migration-backups"
    consistency_check_interval: 1  # Check every N sprints
```

---

## Cross-References

- [CHECKPOINT_GUIDE.md](CHECKPOINT_GUIDE.md) — Checkpoints use SQLite
- [tests/test_phase2.py](../tests/test_phase2.py) — Migration tests
- [ARCHITECTURE.md](ARCHITECTURE.md) — Why SQLite was chosen
