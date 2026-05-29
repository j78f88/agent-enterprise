"""
SQLite Database Layer

Provides ACID-compliant state management for agent-enterprise.
Phase 2 - Durable Execution

Features:
- Automatic schema creation and versioning
- Transaction management with decorators
- Foreign key enforcement
- Checkpoint creation and restoration
- Query builders for common operations
"""

import sqlite3
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any, Tuple
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from functools import wraps


# =============================================================================
# Schema Version
# =============================================================================

SCHEMA_VERSION = 1


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class LedgerItem:
    """Ledger item representation."""
    item_id: str
    type: str
    source_id: Optional[str]
    age: int
    def_count: int  # 'def' is Python keyword, use 'def_count'
    sprint: Optional[str]
    status: str
    blocked: bool
    draft_path: Optional[str]
    notes: Optional[str]
    created_at: str
    updated_at: str


@dataclass
class Bug:
    """Bug detail representation."""
    bug_id: str
    ledger_item_id: str
    severity: str
    title: str
    description: str
    reproduction_steps: Optional[str]
    observed: str
    expected: str
    impact: Optional[str]
    screenshot_path: Optional[str]
    reported_by: Optional[str]
    reported_at: str
    fixed_at: Optional[str]


@dataclass
class Rejection:
    """Handoff rejection representation."""
    rejection_id: str
    ledger_item_id: str
    source_agent: str
    target_agent: str
    reason: str
    rationale: str
    original_request: Optional[str]
    rejected_at: str
    resolved_at: Optional[str]
    resolution: Optional[str]


@dataclass
class Sprint:
    """Sprint metadata representation."""
    sprint_id: str
    sprint_number: int
    status: str
    plan_path: str
    retro_path: Optional[str]
    kickoff_commit_sha: Optional[str]
    completion_commit_sha: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    forecast_complexity: Optional[int]
    actual_complexity: Optional[int]


@dataclass
class Checkpoint:
    """State checkpoint representation."""
    checkpoint_id: str
    sprint_id: str
    phase: str
    state_json: str
    artifact_paths: str  # JSON array
    created_at: str


# =============================================================================
# Database Connection and Schema
# =============================================================================

class Database:
    """
    SQLite database manager with ACID guarantees.
    
    Usage:
        db = Database("agent-state.db")
        
        # Automatic transaction
        with db.transaction():
            db.add_ledger_item(item)
            db.update_sprint_status(sprint_id, "in-progress")
    """
    
    def __init__(self, db_path: str = ".agent-state/agent-state.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create connection
        self.conn = self._create_connection()
        
        # Initialize schema
        self._init_schema()
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create SQLite connection with optimal settings."""
        conn = sqlite3.Connection(
            str(self.db_path),
            check_same_thread=False,  # Allow multi-threaded access
            timeout=30.0  # 30 second timeout for locks
        )
        
        # Enable WAL mode for concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys=ON")
        
        # Set row factory for dict-like access
        conn.row_factory = sqlite3.Row
        
        return conn
    
    def _init_schema(self):
        """Initialize database schema if not exists."""
        # Check schema version
        try:
            result = self.conn.execute(
                "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
            ).fetchone()
            
            if result and result[0] >= SCHEMA_VERSION:
                return  # Schema up to date
        except sqlite3.OperationalError:
            # Table doesn't exist, need to create schema
            pass
        
        # Create schema
        with self.transaction():
            self._create_tables()
            
            # Record schema version
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                )
            """)
            
            self.conn.execute(
                "INSERT OR REPLACE INTO schema_version (version, applied_at) VALUES (?, ?)",
                (SCHEMA_VERSION, datetime.now(timezone.utc).isoformat())
            )
    
    def _create_tables(self):
        """Create all database tables."""
        
        # Ledger table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS ledger (
                item_id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                source_id TEXT,
                age INTEGER NOT NULL DEFAULT 0,
                def INTEGER NOT NULL DEFAULT 0,
                sprint TEXT,
                status TEXT NOT NULL,
                blocked BOOLEAN DEFAULT 0,
                draft_path TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                
                FOREIGN KEY (sprint) REFERENCES sprints(sprint_id),
                CHECK (type IN ('feature', 'bug', 'debt', 'rejection', 'carry-over', 'migration', 'chore')),
                CHECK (status IN ('open', 'assigned', 'done', 'killed')),
                CHECK (age >= 0),
                CHECK (def >= 0)
            )
        """)
        
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_ledger_status ON ledger(status)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_ledger_sprint ON ledger(sprint)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_ledger_type ON ledger(type)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_ledger_def ON ledger(def)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_ledger_age ON ledger(age)")
        
        # Bugs table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS bugs (
                bug_id TEXT PRIMARY KEY,
                ledger_item_id TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                reproduction_steps TEXT,
                observed TEXT NOT NULL,
                expected TEXT NOT NULL,
                impact TEXT,
                screenshot_path TEXT,
                reported_by TEXT,
                reported_at TEXT NOT NULL,
                fixed_at TEXT,
                
                FOREIGN KEY (ledger_item_id) REFERENCES ledger(item_id),
                CHECK (severity IN ('🔴', '🟡', '🟢', '🔵'))
            )
        """)
        
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_bugs_severity ON bugs(severity)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_bugs_ledger_item ON bugs(ledger_item_id)")
        
        # Rejections table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS rejections (
                rejection_id TEXT PRIMARY KEY,
                ledger_item_id TEXT NOT NULL,
                source_agent TEXT NOT NULL,
                target_agent TEXT NOT NULL,
                reason TEXT NOT NULL,
                rationale TEXT NOT NULL,
                original_request TEXT,
                rejected_at TEXT NOT NULL,
                resolved_at TEXT,
                resolution TEXT,
                
                FOREIGN KEY (ledger_item_id) REFERENCES ledger(item_id)
            )
        """)
        
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_rejections_reason ON rejections(reason)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_rejections_ledger_item ON rejections(ledger_item_id)")
        
        # Sprints table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sprints (
                sprint_id TEXT PRIMARY KEY,
                sprint_number INTEGER NOT NULL,
                status TEXT NOT NULL,
                plan_path TEXT NOT NULL,
                retro_path TEXT,
                kickoff_commit_sha TEXT,
                completion_commit_sha TEXT,
                started_at TEXT,
                completed_at TEXT,
                forecast_complexity INTEGER,
                actual_complexity INTEGER,
                
                CHECK (status IN ('draft', 'in-progress', 'completed', 'archived')),
                CHECK (sprint_number > 0)
            )
        """)
        
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_sprints_status ON sprints(status)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_sprints_number ON sprints(sprint_number)")
        
        # Checkpoints table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                checkpoint_id TEXT PRIMARY KEY,
                sprint_id TEXT NOT NULL,
                phase TEXT NOT NULL,
                state_json TEXT NOT NULL,
                artifact_paths TEXT NOT NULL,
                created_at TEXT NOT NULL,
                
                FOREIGN KEY (sprint_id) REFERENCES sprints(sprint_id)
            )
        """)
        
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_checkpoints_sprint ON checkpoints(sprint_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_checkpoints_phase ON checkpoints(phase)")
        
        # Validation records table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS validation_records (
                validation_id TEXT PRIMARY KEY,
                feature_title TEXT NOT NULL,
                verdict TEXT NOT NULL,
                rationale TEXT NOT NULL,
                tests TEXT NOT NULL,
                validated_by TEXT NOT NULL,
                validated_at TEXT NOT NULL,
                validation_path TEXT NOT NULL,
                
                CHECK (verdict IN ('VALIDATED', 'REFRAMED', 'NEW', 'REJECTED', 'DEFERRED'))
            )
        """)
        
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_validation_verdict ON validation_records(verdict)")
    
    @contextmanager
    def transaction(self):
        """
        Context manager for transactions.
        
        Usage:
            with db.transaction():
                db.add_ledger_item(item)
                db.update_sprint(sprint_id, data)
            # Automatically commits on success, rolls back on error
        """
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
    
    def close(self):
        """Close database connection."""
        self.conn.close()
    
    # =========================================================================
    # Ledger Operations
    # =========================================================================
    
    def add_ledger_item(self, item: LedgerItem):
        """Add a new ledger item."""
        self.conn.execute("""
            INSERT INTO ledger (
                item_id, type, source_id, age, def, sprint, status, blocked,
                draft_path, notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.item_id, item.type, item.source_id, item.age, item.def_count,
            item.sprint, item.status, item.blocked, item.draft_path, item.notes,
            item.created_at, item.updated_at
        ))
    
    def update_ledger_item(self, item_id: str, updates: Dict[str, Any]):
        """Update ledger item fields."""
        # Add updated_at
        updates['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [item_id]
        
        self.conn.execute(
            f"UPDATE ledger SET {set_clause} WHERE item_id = ?",
            values
        )
    
    def get_ledger_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get ledger item by ID."""
        row = self.conn.execute(
            "SELECT * FROM ledger WHERE item_id = ?",
            (item_id,)
        ).fetchone()
        
        return dict(row) if row else None
    
    def get_ledger_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all ledger items with given status."""
        rows = self.conn.execute(
            "SELECT * FROM ledger WHERE status = ? ORDER BY age DESC, def DESC",
            (status,)
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def get_open_ledger_items(self) -> List[Dict[str, Any]]:
        """Get all open ledger items."""
        return self.get_ledger_by_status('open')
    
    def increment_age_and_def(self):
        """
        Increment age for all open items at sprint boundary.
        Increment def for items not selected.
        """
        # Increment age for all open items
        self.conn.execute("""
            UPDATE ledger
            SET age = age + 1, updated_at = ?
            WHERE status = 'open'
        """, (datetime.now(timezone.utc).isoformat(),))
    
    # =========================================================================
    # Bug Operations
    # =========================================================================
    
    def add_bug(self, bug: Bug):
        """Add a new bug."""
        self.conn.execute("""
            INSERT INTO bugs (
                bug_id, ledger_item_id, severity, title, description,
                reproduction_steps, observed, expected, impact, screenshot_path,
                reported_by, reported_at, fixed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bug.bug_id, bug.ledger_item_id, bug.severity, bug.title, bug.description,
            bug.reproduction_steps, bug.observed, bug.expected, bug.impact,
            bug.screenshot_path, bug.reported_by, bug.reported_at, bug.fixed_at
        ))
    
    def get_bug(self, bug_id: str) -> Optional[Dict[str, Any]]:
        """Get bug by ID."""
        row = self.conn.execute(
            "SELECT * FROM bugs WHERE bug_id = ?",
            (bug_id,)
        ).fetchone()
        
        return dict(row) if row else None
    
    def get_bugs_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """Get bugs by severity."""
        rows = self.conn.execute(
            "SELECT * FROM bugs WHERE severity = ? ORDER BY reported_at DESC",
            (severity,)
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    # =========================================================================
    # Sprint Operations
    # =========================================================================
    
    def add_sprint(self, sprint: Sprint):
        """Add a new sprint."""
        self.conn.execute("""
            INSERT INTO sprints (
                sprint_id, sprint_number, status, plan_path, retro_path,
                kickoff_commit_sha, completion_commit_sha, started_at, completed_at,
                forecast_complexity, actual_complexity
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sprint.sprint_id, sprint.sprint_number, sprint.status, sprint.plan_path,
            sprint.retro_path, sprint.kickoff_commit_sha, sprint.completion_commit_sha,
            sprint.started_at, sprint.completed_at, sprint.forecast_complexity,
            sprint.actual_complexity
        ))
    
    def update_sprint_status(self, sprint_id: str, status: str):
        """Update sprint status."""
        self.conn.execute(
            "UPDATE sprints SET status = ? WHERE sprint_id = ?",
            (status, sprint_id)
        )
    
    def get_sprint(self, sprint_id: str) -> Optional[Dict[str, Any]]:
        """Get sprint by ID."""
        row = self.conn.execute(
            "SELECT * FROM sprints WHERE sprint_id = ?",
            (sprint_id,)
        ).fetchone()
        
        return dict(row) if row else None
    
    def get_active_sprint(self) -> Optional[Dict[str, Any]]:
        """Get the currently active sprint."""
        row = self.conn.execute(
            "SELECT * FROM sprints WHERE status = 'in-progress' ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
        
        return dict(row) if row else None
    
    # =========================================================================
    # Checkpoint Operations
    # =========================================================================
    
    def create_checkpoint(
        self,
        sprint_id: str,
        phase: str,
        state: Dict[str, Any],
        artifact_paths: List[str]
    ) -> str:
        """
        Create a checkpoint snapshot.
        
        Args:
            sprint_id: Sprint identifier
            phase: Current phase
            state: Complete state dictionary
            artifact_paths: List of artifact file paths
        
        Returns:
            checkpoint_id (SHA256 hash of state)
        """
        # Serialize state
        state_json = json.dumps(state, sort_keys=True)
        
        # Compute checkpoint ID
        checkpoint_id = hashlib.sha256(state_json.encode()).hexdigest()
        
        # Store checkpoint
        self.conn.execute("""
            INSERT OR REPLACE INTO checkpoints (
                checkpoint_id, sprint_id, phase, state_json, artifact_paths, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            checkpoint_id,
            sprint_id,
            phase,
            state_json,
            json.dumps(artifact_paths),
            datetime.now(timezone.utc).isoformat()
        ))
        
        return checkpoint_id
    
    def restore_checkpoint(self, checkpoint_id: str) -> Tuple[Dict[str, Any], List[str]]:
        """
        Restore state from checkpoint.
        
        Args:
            checkpoint_id: Checkpoint ID to restore
        
        Returns:
            (state_dict, artifact_paths)
        """
        row = self.conn.execute(
            "SELECT state_json, artifact_paths FROM checkpoints WHERE checkpoint_id = ?",
            (checkpoint_id,)
        ).fetchone()
        
        if not row:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")
        
        state = json.loads(row[0])
        artifact_paths = json.loads(row[1])
        
        return state, artifact_paths
    
    def get_latest_checkpoint(self, sprint_id: str) -> Optional[Dict[str, Any]]:
        """Get latest checkpoint for a sprint."""
        row = self.conn.execute("""
            SELECT * FROM checkpoints
            WHERE sprint_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (sprint_id,)).fetchone()
        
        return dict(row) if row else None
    
    # =========================================================================
    # Utility Operations
    # =========================================================================
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute arbitrary query and return results."""
        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    
    def get_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        stats = {}
        
        for table in ['ledger', 'bugs', 'rejections', 'sprints', 'checkpoints']:
            count = self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            stats[table] = count
        
        return stats


# =============================================================================
# Transaction Decorator
# =============================================================================

def transactional(func):
    """
    Decorator to wrap function in a database transaction.
    
    Usage:
        @transactional
        def update_multiple_items(db: Database, items: List):
            for item in items:
                db.update_ledger_item(item.id, item.data)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Find Database instance in args
        db = None
        for arg in args:
            if isinstance(arg, Database):
                db = arg
                break
        
        if db is None:
            raise ValueError("@transactional requires Database instance as first argument")
        
        with db.transaction():
            return func(*args, **kwargs)
    
    return wrapper


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Initialize database
    db = Database(".agent-state/agent-state.db")
    
    print("✓ Database initialized")
    print(f"  Schema version: {SCHEMA_VERSION}")
    print(f"  Database path: {db.db_path}")
    
    # Show stats
    stats = db.get_stats()
    print("\n📊 Database Statistics:")
    for table, count in stats.items():
        print(f"  {table}: {count} rows")
    
    # Example: Add a ledger item
    with db.transaction():
        item = LedgerItem(
            item_id="ITEM-001",
            type="feature",
            source_id=None,
            age=0,
            def_count=0,
            sprint=None,
            status="open",
            blocked=False,
            draft_path=None,
            notes="Example feature item",
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat()
        )
        
        db.add_ledger_item(item)
        print("\n✓ Added example ledger item: ITEM-001")
    
    # Query open items
    open_items = db.get_open_ledger_items()
    print(f"\n📋 Open ledger items: {len(open_items)}")
    
    db.close()
    print("\n✓ Database connection closed")
