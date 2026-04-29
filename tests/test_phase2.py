"""
Phase 2 Integration Tests

Tests for durable execution components:
- SQLite database layer
- Migration utilities
- Checkpoint-restart system
- Workflow engine with retries
- Dual-write compatibility

Run with: pytest tests/test_phase2.py -v
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone

# Import Phase 2 components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "phase2_durability"))

from db import Database, LedgerItem, Bug, Sprint, transactional
from migrate import MigrationManager, MarkdownLedgerParser
from checkpoint import CheckpointManager, CheckpointState, ResumeManager
from workflow import WorkflowEngine, Workflow, Task, TaskStatus, RetryPolicy
from dual_write import DualWriteManager


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    shutil.rmtree(tmpdir)


@pytest.fixture
def test_db(temp_dir):
    """Create test database."""
    db_path = temp_dir / "test.db"
    db = Database(str(db_path))
    yield db
    db.close()


@pytest.fixture
def sample_ledger_item():
    """Create sample ledger item."""
    return LedgerItem(
        item_id="ITEM-001",
        type="feature",
        source_id=None,
        age=0,
        def_count=0,
        sprint=None,
        status="open",
        blocked=False,
        draft_path=None,
        notes="Test feature",
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat()
    )


# =============================================================================
# Database Layer Tests
# =============================================================================

class TestDatabaseLayer:
    """Test SQLite database operations."""
    
    def test_database_initialization(self, test_db):
        """Test database creates schema correctly."""
        # Check tables exist
        tables = test_db.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        
        table_names = [t['name'] for t in tables]
        assert 'ledger' in table_names
        assert 'bugs' in table_names
        assert 'sprints' in table_names
        assert 'checkpoints' in table_names
    
    def test_add_ledger_item(self, test_db, sample_ledger_item):
        """Test adding ledger item."""
        with test_db.transaction():
            test_db.add_ledger_item(sample_ledger_item)
        
        # Verify item exists
        item = test_db.get_ledger_item("ITEM-001")
        assert item is not None
        assert item['type'] == 'feature'
        assert item['status'] == 'open'
    
    def test_update_ledger_item(self, test_db, sample_ledger_item):
        """Test updating ledger item."""
        # Add item
        with test_db.transaction():
            test_db.add_ledger_item(sample_ledger_item)
        
        # Update item
        with test_db.transaction():
            test_db.update_ledger_item("ITEM-001", {
                "age": 1,
                "def": 2,
                "notes": "Updated notes"
            })
        
        # Verify updates
        item = test_db.get_ledger_item("ITEM-001")
        assert item['age'] == 1
        assert item['def'] == 2
        assert item['notes'] == "Updated notes"
    
    def test_transaction_rollback(self, test_db, sample_ledger_item):
        """Test transaction rollback on error."""
        try:
            with test_db.transaction():
                test_db.add_ledger_item(sample_ledger_item)
                # Force error
                raise ValueError("Test error")
        except ValueError:
            pass
        
        # Verify item was not added (transaction rolled back)
        item = test_db.get_ledger_item("ITEM-001")
        assert item is None
    
    def test_foreign_key_constraint(self, test_db):
        """Test foreign key enforcement."""
        # Try to add ledger item with non-existent sprint
        invalid_item = LedgerItem(
            item_id="ITEM-999",
            type="feature",
            source_id=None,
            age=0,
            def_count=0,
            sprint="999",  # Non-existent sprint
            status="assigned",
            blocked=False,
            draft_path=None,
            notes="Test",
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat()
        )
        
        with pytest.raises(Exception):  # Should raise foreign key error
            with test_db.transaction():
                test_db.add_ledger_item(invalid_item)
    
    def test_get_open_ledger_items(self, test_db):
        """Test querying open ledger items."""
        # Add multiple items
        for i in range(3):
            item = LedgerItem(
                item_id=f"ITEM-{i:03d}",
                type="feature",
                source_id=None,
                age=i,
                def_count=0,
                sprint=None,
                status="open",
                blocked=False,
                draft_path=None,
                notes=f"Item {i}",
                created_at=datetime.now(timezone.utc).isoformat(),
                updated_at=datetime.now(timezone.utc).isoformat()
            )
            with test_db.transaction():
                test_db.add_ledger_item(item)
        
        # Query open items
        open_items = test_db.get_open_ledger_items()
        assert len(open_items) == 3
        
        # Verify ordering (by age DESC)
        assert open_items[0]['age'] >= open_items[-1]['age']


# =============================================================================
# Migration Tests
# =============================================================================

class TestMigration:
    """Test migration from markdown to SQLite."""
    
    def test_parse_ledger_markdown(self, temp_dir):
        """Test parsing ledger from markdown."""
        # Create test markdown
        ledger_md = temp_dir / "BACKLOG_LEDGER.md"
        ledger_md.write_text("""
# Backlog Ledger

| Item ID | Type | Source | Age | Def | Sprint | Notes |
|---------|------|--------|-----|-----|--------|-------|
| ITEM-001 | feature | | 0 | 0 | | Test item 1 |
| ITEM-002 | bug | BUG-001 | 1 | 2 | 042 | Test bug |
""", encoding='utf-8')
        
        # Parse
        items = MarkdownLedgerParser.parse_ledger_file(ledger_md)
        
        assert len(items) == 2
        assert items[0].item_id == "ITEM-001"
        assert items[0].type == "feature"
        assert items[1].item_id == "ITEM-002"
        assert items[1].source_id == "BUG-001"
    
    def test_import_from_markdown(self, test_db, temp_dir):
        """Test importing markdown to database."""
        # Create test markdown
        ledger_md = temp_dir / "BACKLOG_LEDGER.md"
        ledger_md.write_text("""
| Item ID | Type | Source | Age | Def | Sprint | Notes |
|---------|------|--------|-----|-----|--------|-------|
| ITEM-001 | feature | | 0 | 0 | | Test |
""", encoding='utf-8')
        
        # Import
        migrator = MigrationManager(
            test_db,
            ledger_path=str(ledger_md),
            bug_path=str(temp_dir / "bugs.md"),
            rejection_path=str(temp_dir / "rejections.md")
        )
        
        counts = migrator.import_from_markdown()
        
        assert counts['ledger'] == 1
        
        # Verify in database
        item = test_db.get_ledger_item("ITEM-001")
        assert item is not None


# =============================================================================
# Checkpoint Tests
# =============================================================================

class TestCheckpoint:
    """Test checkpoint-restart system."""
    
    @pytest.fixture(autouse=True)
    def seed_sprint(self, test_db):
        """Create the sprint record that checkpoints reference via FK."""
        with test_db.transaction():
            test_db.add_sprint(Sprint(
                sprint_id="test-sprint",
                sprint_number=1,
                status="in-progress",
                plan_path="sprints/1/PLAN.md",
                retro_path=None,
                kickoff_commit_sha=None,
                completion_commit_sha=None,
                started_at=datetime.now(timezone.utc).isoformat(),
                completed_at=None,
                forecast_complexity=None,
                actual_complexity=None,
            ))

    def test_create_checkpoint(self, test_db, temp_dir):
        """Test checkpoint creation."""
        cm = CheckpointManager(test_db, "test-sprint", str(temp_dir))
        
        state = CheckpointState(
            sprint_id="test-sprint",
            phase="implementation",
            fsm_state="IMPLEMENTATION",
            logical_time=10,
            context={"key": "value"},
            ledger_items=[],
            active_tasks=[],
            completed_tasks=[],
            environment={},
            metadata={}
        )
        
        checkpoint_id = cm.create_checkpoint("implementation", state, [])
        
        assert checkpoint_id is not None
        assert len(checkpoint_id) == 64  # SHA256 hash
    
    def test_restore_checkpoint(self, test_db, temp_dir):
        """Test checkpoint restoration."""
        cm = CheckpointManager(test_db, "test-sprint", str(temp_dir))
        
        # Create checkpoint
        state = CheckpointState(
            sprint_id="test-sprint",
            phase="implementation",
            fsm_state="IMPLEMENTATION",
            logical_time=10,
            context={"task_id": "task-1"},
            ledger_items=[],
            active_tasks=[],
            completed_tasks=[],
            environment={},
            metadata={}
        )
        
        checkpoint_id = cm.create_checkpoint("implementation", state, ["file.md"])
        
        # Restore checkpoint
        restored_state, artifacts = cm.restore_checkpoint(checkpoint_id)
        
        assert restored_state.sprint_id == "test-sprint"
        assert restored_state.phase == "implementation"
        assert restored_state.context['task_id'] == "task-1"
        assert artifacts == ["file.md"]
    
    def test_list_checkpoints(self, test_db, temp_dir):
        """Test listing checkpoints."""
        cm = CheckpointManager(test_db, "test-sprint", str(temp_dir))
        
        # Create multiple checkpoints
        for i in range(3):
            state = CheckpointState(
                sprint_id="test-sprint",
                phase=f"phase-{i}",
                fsm_state="TEST",
                logical_time=i,
                context={},
                ledger_items=[],
                active_tasks=[],
                completed_tasks=[],
                environment={},
                metadata={}
            )
            cm.create_checkpoint(f"phase-{i}", state, [])
        
        # List checkpoints
        checkpoints = cm.list_checkpoints()
        
        assert len(checkpoints) == 3
        # Should be sorted by creation time (newest first)
        assert checkpoints[0].created_at >= checkpoints[-1].created_at


# =============================================================================
# Workflow Engine Tests
# =============================================================================

class TestWorkflowEngine:
    """Test workflow execution with retries."""
    
    def test_simple_workflow(self, test_db):
        """Test basic workflow execution."""
        engine = WorkflowEngine(test_db)
        
        context = {}
        
        def task_action(ctx):
            ctx['executed'] = True
            return "success"
        
        task = Task(
            task_id="task-1",
            name="Test Task",
            action=task_action
        )
        
        workflow = Workflow(
            workflow_id="test-workflow",
            name="Test Workflow",
            tasks=[task],
            context=context,
            checkpoint_enabled=False
        )
        
        success = engine.execute(workflow)
        
        assert success
        assert context['executed']
        assert len(workflow.completed_tasks) == 1
    
    def test_workflow_with_dependencies(self, test_db):
        """Test workflow with task dependencies."""
        engine = WorkflowEngine(test_db)
        context = {}
        
        def task1_action(ctx):
            ctx['task1_done'] = True
        
        def task2_action(ctx):
            # Requires task1 to be done
            assert ctx.get('task1_done'), "Task 1 not executed first"
            ctx['task2_done'] = True
        
        task1 = Task(
            task_id="task-1",
            name="Task 1",
            action=task1_action,
            dependencies=[]
        )
        
        task2 = Task(
            task_id="task-2",
            name="Task 2",
            action=task2_action,
            dependencies=["task-1"]
        )
        
        workflow = Workflow(
            workflow_id="test-workflow",
            name="Test Workflow",
            tasks=[task1, task2],
            context=context,
            checkpoint_enabled=False
        )
        
        success = engine.execute(workflow)
        
        assert success
        assert context['task1_done']
        assert context['task2_done']
    
    def test_workflow_with_retry(self, test_db):
        """Test workflow task retry on failure."""
        engine = WorkflowEngine(test_db)
        
        attempt_count = [0]
        
        def failing_task(ctx):
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise RuntimeError("Simulated failure")
            return "success"
        
        task = Task(
            task_id="task-1",
            name="Failing Task",
            action=failing_task,
            retry_policy=RetryPolicy(max_attempts=3, initial_delay_seconds=0.1)
        )
        
        workflow = Workflow(
            workflow_id="test-workflow",
            name="Test Workflow",
            tasks=[task],
            checkpoint_enabled=False
        )
        
        success = engine.execute(workflow)
        
        assert success
        assert attempt_count[0] == 2  # Failed once, succeeded on retry
    
    def test_workflow_compensation(self, test_db):
        """Test workflow compensation on failure."""
        engine = WorkflowEngine(test_db)
        context = {}
        
        def task1_action(ctx):
            ctx['task1_done'] = True
        
        def task1_compensation(ctx):
            ctx['task1_compensated'] = True
        
        def task2_action(ctx):
            raise RuntimeError("Task 2 always fails")
        
        task1 = Task(
            task_id="task-1",
            name="Task 1",
            action=task1_action,
            compensation=task1_compensation
        )
        
        task2 = Task(
            task_id="task-2",
            name="Task 2",
            action=task2_action,
            dependencies=["task-1"],
            retry_policy=RetryPolicy(max_attempts=1)  # Fail fast
        )
        
        workflow = Workflow(
            workflow_id="test-workflow",
            name="Test Workflow",
            tasks=[task1, task2],
            context=context,
            checkpoint_enabled=False
        )
        
        success = engine.execute(workflow)
        
        assert not success
        assert context['task1_done']
        assert context['task1_compensated']  # Compensation executed


# =============================================================================
# Dual-Write Tests
# =============================================================================

class TestDualWrite:
    """Test dual-write compatibility layer."""
    
    def test_add_item_dual_write(self, test_db, temp_dir, sample_ledger_item):
        """Test adding item writes to both database and markdown."""
        ledger_path = temp_dir / "BACKLOG_LEDGER.md"
        
        dwm = DualWriteManager(
            test_db,
            ledger_path=str(ledger_path),
            bug_path=str(temp_dir / "bugs.md"),
            rejection_path=str(temp_dir / "rejections.md"),
            enabled=True
        )
        
        dwm.add_ledger_item(sample_ledger_item)
        
        # Check database
        db_item = test_db.get_ledger_item("ITEM-001")
        assert db_item is not None
        
        # Check markdown
        assert ledger_path.exists()
        md_content = ledger_path.read_text(encoding='utf-8')
        assert "ITEM-001" in md_content
    
    def test_update_item_dual_write(self, test_db, temp_dir, sample_ledger_item):
        """Test updating item updates both database and markdown."""
        ledger_path = temp_dir / "BACKLOG_LEDGER.md"
        
        dwm = DualWriteManager(
            test_db,
            ledger_path=str(ledger_path),
            enabled=True
        )
        
        # Add item
        dwm.add_ledger_item(sample_ledger_item)
        
        # Update item
        dwm.update_ledger_item("ITEM-001", {"age": 5, "notes": "Updated"})
        
        # Check database
        db_item = test_db.get_ledger_item("ITEM-001")
        assert db_item['age'] == 5
        
        # Check markdown
        md_content = ledger_path.read_text(encoding='utf-8')
        assert "| 5 |" in md_content  # Age column
    
    def test_disable_dual_write(self, test_db, temp_dir, sample_ledger_item):
        """Test disabling dual-write only writes to database."""
        ledger_path = temp_dir / "BACKLOG_LEDGER.md"
        
        dwm = DualWriteManager(
            test_db,
            ledger_path=str(ledger_path),
            enabled=False  # Disabled
        )
        
        dwm.add_ledger_item(sample_ledger_item)
        
        # Check database
        db_item = test_db.get_ledger_item("ITEM-001")
        assert db_item is not None
        
        # Markdown should not be updated
        assert not ledger_path.exists()


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
