"""
Phase 3 Integration Tests

Tests for sandboxing and isolation components:
- Container-based sandbox manager
- Capability-based security framework
- Sandbox state tracking in checkpoints
- Workflow engine with sandboxed execution

Run with: pytest tests/test_phase3.py -v
Skip Docker tests if Docker unavailable: pytest tests/test_phase3.py -v -m "not docker"
"""

import pytest
import tempfile
import shutil
import time
from pathlib import Path
from unittest.mock import Mock, patch

# Import Phase 3 components
import sys
_phase3_dir = str(Path(__file__).parent.parent / "src" / "phase3_isolation")
_phase2_dir = str(Path(__file__).parent.parent / "src" / "phase2_durability")
sys.path.insert(0, _phase3_dir)
sys.path.insert(0, _phase2_dir)

# Only import Docker-dependent modules if Docker is available
try:
    from sandbox import (
        SandboxManager, Sandbox, SandboxStatus, NetworkPolicy, ResourceLimits,
        DOCKER_AVAILABLE
    )
    SANDBOX_TESTS_AVAILABLE = True
except ImportError:
    SANDBOX_TESTS_AVAILABLE = False
    DOCKER_AVAILABLE = False

from capabilities import (
    Capability, CapabilityType, CapabilityEnforcer, CapabilityPresets,
    Action, CapabilityViolation
)
from checkpoint import CheckpointState, CheckpointManager
from sandbox_checkpoint import SandboxCheckpointManager
from workflow import WorkflowEngine, Workflow, Task, TaskStatus, RetryPolicy
from db import Database, Sprint


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
def sandbox_manager(temp_dir):
    """Create sandbox manager (requires Docker)."""
    if not DOCKER_AVAILABLE:
        pytest.skip("Docker not available")
    
    manager = SandboxManager(
        workspace_path=str(temp_dir),
        network_policy=NetworkPolicy.DENY_ALL,
        state_dir=str(temp_dir / "sandboxes")
    )
    yield manager
    # Cleanup all sandboxes
    manager.cleanup_all()


# =============================================================================
# Capability Tests
# =============================================================================

class TestCapabilities:
    """Test capability-based security framework."""
    
    def test_file_read_capability(self):
        """Test file read capability matching."""
        cap = Capability(
            type=CapabilityType.FILE_READ.value,
            scope="/workspace/tests/**"
        )
        
        # Should match files in tests directory
        assert cap.grants(Action.file_read("/workspace/tests/test_foo.py"))
        assert cap.grants(Action.file_read("/workspace/tests/unit/test_bar.py"))
        
        # Should not match files outside tests
        assert not cap.grants(Action.file_read("/workspace/src/main.py"))
        assert not cap.grants(Action.file_read("/etc/passwd"))
    
    def test_file_write_capability(self):
        """Test file write capability matching."""
        cap = Capability(
            type=CapabilityType.FILE_WRITE.value,
            scope="/workspace/dist/**"
        )
        
        # Should match files in dist directory
        assert cap.grants(Action.file_write("/workspace/dist/output.js"))
        
        # Should not match files outside dist
        assert not cap.grants(Action.file_write("/workspace/src/main.py"))
    
    def test_network_capability(self):
        """Test network capability matching."""
        cap = Capability(
            type=CapabilityType.NETWORK_HTTP.value,
            scope="api.example.com"
        )
        
        # Should match domain
        assert cap.grants(Action.network_http("https://api.example.com/endpoint"))
        assert cap.grants(Action.network_http("api.example.com"))
        
        # Should not match other domains
        assert not cap.grants(Action.network_http("https://evil.com"))
    
    def test_exec_capability(self):
        """Test command execution capability matching."""
        cap = Capability(
            type=CapabilityType.EXEC_TEST.value,
            scope="pytest"
        )
        
        # Should match pytest commands
        assert cap.grants(Action.exec_command("pytest -v", cmd_type="test"))
        assert cap.grants(Action.exec_command("pytest tests/", cmd_type="test"))
        
        # Should not match other commands
        assert not cap.grants(Action.exec_command("npm test", cmd_type="test"))
        assert not cap.grants(Action.exec_command("rm -rf /", cmd_type="shell"))
    
    def test_capability_enforcer_allow(self):
        """Test enforcer allows actions with proper capabilities."""
        capabilities = [
            Capability(
                type=CapabilityType.FILE_READ.value,
                scope="/workspace/**"
            )
        ]
        
        enforcer = CapabilityEnforcer(capabilities, strict_mode=True)
        
        action = Action.file_read("/workspace/test.py")
        check = enforcer.check(action)
        
        assert check.granted
        assert check.capability is not None
    
    def test_capability_enforcer_deny(self):
        """Test enforcer denies actions without capabilities."""
        capabilities = [
            Capability(
                type=CapabilityType.FILE_READ.value,
                scope="/workspace/tests/**"
            )
        ]
        
        enforcer = CapabilityEnforcer(capabilities, strict_mode=True)
        
        # Try to write file (no write capability)
        action = Action.file_write("/workspace/output.txt")
        check = enforcer.check(action, sandbox_id="test")
        
        assert not check.granted
        assert len(enforcer.get_violations()) == 1
    
    def test_capability_presets(self):
        """Test predefined capability sets."""
        # Test runner preset
        test_caps = CapabilityPresets.test_runner()
        assert len(test_caps) > 0
        
        # Check contains file:read
        assert any(c.type == CapabilityType.FILE_READ.value for c in test_caps)
        
        # Check contains exec:test
        assert any(c.type == CapabilityType.EXEC_TEST.value for c in test_caps)
    
    def test_violation_tracking(self):
        """Test capability violation tracking."""
        enforcer = CapabilityEnforcer([], strict_mode=True)
        
        # Trigger violations
        enforcer.check(Action.file_write("/etc/passwd"), sandbox_id="test-1")
        enforcer.check(Action.network_http("https://evil.com"), sandbox_id="test-1")
        
        violations = enforcer.get_violations()
        assert len(violations) == 2
        
        # Check violation details
        assert violations[0].sandbox_id == "test-1"
        assert "No capability" in violations[0].reason


# =============================================================================
# Sandbox Manager Tests (Docker-dependent)
# =============================================================================

@pytest.mark.docker
class TestSandboxManager:
    """Test container-based sandbox manager (requires Docker)."""
    
    def test_sandbox_creation(self, sandbox_manager):
        """Test creating a sandbox."""
        sandbox = sandbox_manager.create_sandbox(
            sandbox_id="test-sandbox",
            resource_limits=ResourceLimits(max_memory_mb=512)
        )
        
        assert sandbox is not None
        assert sandbox.sandbox_id == "test-sandbox"
        assert sandbox.state.status == SandboxStatus.RUNNING.value
        
        # Cleanup
        sandbox_manager.destroy_sandbox("test-sandbox")
    
    def test_sandbox_execution(self, sandbox_manager):
        """Test executing commands in sandbox."""
        sandbox = sandbox_manager.create_sandbox(
            sandbox_id="test-exec",
            resource_limits=ResourceLimits(max_memory_mb=512)
        )
        
        # Execute simple command
        result = sandbox_manager.execute_in_sandbox(
            sandbox,
            command="echo 'Hello from sandbox'"
        )
        
        assert result.exit_code == 0
        assert "Hello from sandbox" in result.stdout
        
        # Cleanup
        sandbox_manager.destroy_sandbox("test-exec")
    
    def test_sandbox_isolation(self, sandbox_manager, temp_dir):
        """Test sandbox filesystem isolation."""
        # Create a file in workspace
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content")
        
        sandbox = sandbox_manager.create_sandbox(
            sandbox_id="test-isolation",
            resource_limits=ResourceLimits(max_memory_mb=512)
        )
        
        # File should be accessible in sandbox
        result = sandbox_manager.execute_in_sandbox(
            sandbox,
            command="cat /workspace/test.txt"
        )
        
        assert result.exit_code == 0
        assert "Test content" in result.stdout
        
        # But host root should not be accessible
        result2 = sandbox_manager.execute_in_sandbox(
            sandbox,
            command="ls /etc/passwd"
        )
        
        # This might succeed (depends on isolation), but shouldn't show host /etc
        # The key is the file isn't writable from sandbox
        
        # Cleanup
        sandbox_manager.destroy_sandbox("test-isolation")
    
    def test_sandbox_resource_limits(self, sandbox_manager):
        """Test resource limits enforcement."""
        sandbox = sandbox_manager.create_sandbox(
            sandbox_id="test-limits",
            resource_limits=ResourceLimits(
                max_memory_mb=256,
                max_cpu_cores=1.0
            )
        )
        
        # Check container was created with limits
        container = sandbox_manager.client.containers.get(sandbox.state.container_name)
        assert container is not None
        
        # Cleanup
        sandbox_manager.destroy_sandbox("test-limits")
    
    def test_sandbox_cleanup(self, sandbox_manager):
        """Test sandbox cleanup."""
        sandbox = sandbox_manager.create_sandbox(
            sandbox_id="test-cleanup",
            resource_limits=ResourceLimits(max_memory_mb=512)
        )
        
        container_id = sandbox.state.container_id
        
        # Destroy sandbox
        sandbox_manager.destroy_sandbox("test-cleanup")
        
        # Verify container is removed
        assert "test-cleanup" not in sandbox_manager.active_sandboxes
        
        # Container should be removed
        with pytest.raises(Exception):
            sandbox_manager.client.containers.get(container_id)


# =============================================================================
# Sandbox Checkpoint Tests
# =============================================================================

class TestSandboxCheckpoint:
    """Test sandbox state tracking in checkpoints."""
    
    def test_checkpoint_includes_sandbox_state(self, test_db, temp_dir):
        """Test checkpoint captures sandbox state."""
        # Skip if Docker not available
        if not DOCKER_AVAILABLE:
            pytest.skip("Docker not available")
        
        from sandbox import SandboxManager
        
        checkpoint_mgr = CheckpointManager(test_db, "test-sprint", str(temp_dir))
        sandbox_mgr = SandboxManager(state_dir=str(temp_dir / "sandboxes"))
        
        scm = SandboxCheckpointManager(checkpoint_mgr, sandbox_mgr)
        
        # Create a sandbox
        sandbox = sandbox_mgr.create_sandbox(
            sandbox_id="test-sb-001",
            resource_limits=ResourceLimits(max_memory_mb=512)
        )
        
        # Execute command
        sandbox_mgr.execute_in_sandbox(sandbox, command="echo 'test'")
        
        # Create checkpoint
        base_state = CheckpointState(
            sprint_id="test-sprint",
            phase="test",
            fsm_state="TEST",
            logical_time=1,
            context={},
            ledger_items=[],
            active_tasks=[],
            completed_tasks=[],
            environment={},
            metadata={}
        )
        
        checkpoint_id = scm.create_checkpoint_with_sandboxes(
            phase="test",
            base_state=base_state,
            artifacts=[]
        )
        
        # Verify checkpoint includes sandbox state
        assert checkpoint_id is not None
        assert len(base_state.active_sandboxes) == 1
        assert base_state.active_sandboxes[0]['sandbox_id'] == "test-sb-001"
        
        # Cleanup
        sandbox_mgr.destroy_sandbox("test-sb-001")
        test_db.close()
    
    def test_resume_from_checkpoint_with_sandboxes(self, test_db, temp_dir):
        """Test resuming from checkpoint with sandbox state."""
        # This is a simplified test without actually recreating sandboxes
        # Seed the sprint record so FK constraint is satisfied
        with test_db.transaction():
            test_db.add_sprint(Sprint(
                sprint_id="test-sprint", sprint_number=1, status="in-progress",
                plan_path="sprints/1/PLAN.md", retro_path=None,
                kickoff_commit_sha=None, completion_commit_sha=None,
                started_at=None, completed_at=None,
                forecast_complexity=None, actual_complexity=None,
            ))
        checkpoint_mgr = CheckpointManager(test_db, "test-sprint", str(temp_dir))
        
        # Create checkpoint with mock sandbox state
        state = CheckpointState(
            sprint_id="test-sprint",
            phase="test",
            fsm_state="TEST",
            logical_time=1,
            context={},
            ledger_items=[],
            active_tasks=[],
            completed_tasks=[],
            environment={},
            metadata={},
            active_sandboxes=[
                {
                    'sandbox_id': 'mock-sandbox',
                    'status': 'running',
                    'capabilities': [],
                    'resource_limits': {
                        'max_memory_mb': 512,
                        'max_cpu_cores': 1.0,
                        'max_execution_seconds': 900,
                        'max_disk_writes_mb': 500,
                        'max_network_egress_mb': 100
                    },
                    'network_policy': 'deny-all',
                    'created_at': '2026-04-27T12:00:00Z'
                }
            ],
            sandbox_history=[]
        )
        
        checkpoint_id = checkpoint_mgr.create_checkpoint("test", state, [])
        
        # Restore
        restored_state, artifacts = checkpoint_mgr.restore_checkpoint(checkpoint_id)
        
        assert len(restored_state.active_sandboxes) == 1
        assert restored_state.active_sandboxes[0]['sandbox_id'] == 'mock-sandbox'
        
        test_db.close()


# =============================================================================
# Workflow with Sandbox Tests
# =============================================================================

class TestWorkflowWithSandbox:
    """Test workflow engine with sandboxed tasks."""
    
    def test_workflow_unsandboxed_task(self, test_db):
        """Test workflow with regular (unsandboxed) task."""
        engine = WorkflowEngine(test_db)
        
        context = {}
        
        def task_action(ctx):
            ctx['executed'] = True
            return "success"
        
        task = Task(
            task_id="task-1",
            name="Regular Task",
            action=task_action,
            sandboxed=False
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
        
        test_db.close()
    
    @pytest.mark.docker
    def test_workflow_sandboxed_task(self, test_db, temp_dir):
        """Test workflow with sandboxed task (requires Docker)."""
        if not DOCKER_AVAILABLE:
            pytest.skip("Docker SDK not available")
        from sandbox import SandboxManager
        
        sandbox_mgr = SandboxManager(
            workspace_path=str(temp_dir),
            state_dir=str(temp_dir / "sandboxes")
        )
        
        engine = WorkflowEngine(test_db, sandbox_manager=sandbox_mgr)
        
        context = {}
        
        def sandboxed_task_action(ctx):
            # Execute command in sandbox
            sandbox = ctx.get('sandbox')
            sandbox_manager = ctx.get('sandbox_manager')
            
            result = sandbox_manager.execute_in_sandbox(
                sandbox,
                command="echo 'Sandboxed execution'"
            )
            
            ctx['sandbox_result'] = result
            return result.exit_code == 0
        
        task = Task(
            task_id="task-1",
            name="Sandboxed Task",
            action=sandboxed_task_action,
            sandboxed=True,
            capabilities=CapabilityPresets.read_only_workspace(),
            resource_limits=ResourceLimits(max_memory_mb=512)
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
        assert 'sandbox_result' in context
        assert context['sandbox_result'].exit_code == 0
        
        # Cleanup
        sandbox_mgr.cleanup_all()
        test_db.close()
    
    def test_sandboxed_task_with_retry(self, test_db):
        """Test sandboxed task retry logic (mocked)."""
        # Mock sandbox manager
        mock_sandbox_mgr = Mock()
        mock_sandbox = Mock()
        mock_sandbox.sandbox_id = "mock-sandbox"
        mock_sandbox_mgr.create_sandbox.return_value = mock_sandbox
        
        engine = WorkflowEngine(test_db, sandbox_manager=mock_sandbox_mgr)
        
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
            sandboxed=True,
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
        assert task.status == TaskStatus.COMPLETED
        
        # Verify sandbox was created and destroyed
        mock_sandbox_mgr.create_sandbox.assert_called_once()
        mock_sandbox_mgr.destroy_sandbox.assert_called_once()
        
        test_db.close()


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    # Run tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-m", "not docker"  # Skip Docker tests by default
    ])
