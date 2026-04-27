"""
Workflow Engine with Retries

Durable execution engine with automatic retries, compensation, and error recovery.
Phase 2 - Durable Execution

Features:
- Task orchestration with dependencies
- Automatic retry with exponential backoff
- Compensation (rollback) on failure
- Saga pattern for distributed transactions
- Progress tracking and observability
"""

import time
import traceback
from enum import Enum
from dataclasses import dataclass, field
from typing import Callable, List, Dict, Any, Optional
from datetime import datetime, timezone

from db import Database
from checkpoint import CheckpointManager, CheckpointState


# =============================================================================
# Task Status and Configuration
# =============================================================================

class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


@dataclass
class RetryPolicy:
    """Retry configuration."""
    max_attempts: int = 3
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number."""
        delay = min(
            self.initial_delay_seconds * (self.exponential_base ** attempt),
            self.max_delay_seconds
        )
        
        if self.jitter:
            import random
            delay *= (0.5 + random.random())  # Add 0-50% jitter
        
        return delay


@dataclass
class Task:
    """
    Executable task with retry and compensation logic.
    
    A task represents a unit of work that can be executed, retried on failure,
    and compensated (rolled back) if needed.
    """
    task_id: str
    name: str
    action: Callable[[Dict[str, Any]], Any]  # Execute function
    compensation: Optional[Callable[[Dict[str, Any]], Any]] = None  # Rollback function
    dependencies: List[str] = field(default_factory=list)  # Task IDs this depends on
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    timeout_seconds: Optional[float] = None
    idempotent: bool = True  # Safe to retry without side effects
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Phase 3: Sandbox isolation
    sandboxed: bool = False  # Execute in isolated sandbox
    capabilities: List = field(default_factory=list)  # Required capabilities
    resource_limits: Optional[Any] = None  # ResourceLimits from sandbox module
    
    # Runtime state
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = 0
    last_error: Optional[str] = None
    result: Any = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    sandbox_id: Optional[str] = None  # Sandbox used for execution


# =============================================================================
# Workflow Definition
# =============================================================================

@dataclass
class Workflow:
    """
    Workflow composed of tasks with dependencies.
    
    Executes tasks in dependency order with retries and compensation.
    """
    workflow_id: str
    name: str
    tasks: List[Task]
    context: Dict[str, Any] = field(default_factory=dict)
    checkpoint_enabled: bool = True
    
    # Runtime state
    completed_tasks: List[str] = field(default_factory=list)
    failed_tasks: List[str] = field(default_factory=list)
    compensated_tasks: List[str] = field(default_factory=list)


# =============================================================================
# Workflow Engine
# =============================================================================

class WorkflowEngine:
    """
    Durable workflow execution engine.
    
    Usage:
        engine = WorkflowEngine(db, checkpoint_manager)
        
        # Define workflow
        workflow = Workflow(
            workflow_id="sprint-042-impl",
            name="Sprint 042 Implementation",
            tasks=[task1, task2, task3]
        )
        
        # Execute
        result = engine.execute(workflow)
    """
    
    def __init__(
        self,
        db: Database,
        checkpoint_manager: Optional[CheckpointManager] = None,
        sandbox_manager: Optional[Any] = None  # Phase 3: SandboxManager
    ):
        """
        Initialize workflow engine.
        
        Args:
            db: Database instance
            checkpoint_manager: Optional checkpoint manager for state snapshots
            sandbox_manager: Optional sandbox manager for isolated execution (Phase 3)
        """
        self.db = db
        self.checkpoint_manager = checkpoint_manager
        self.sandbox_manager = sandbox_manager
    
    def execute(self, workflow: Workflow) -> bool:
        """
        Execute workflow to completion.
        
        Args:
            workflow: Workflow to execute
        
        Returns:
            True if workflow completed successfully, False otherwise
        """
        print(f"🔧 Starting workflow: {workflow.name}")
        print(f"   Tasks: {len(workflow.tasks)}")
        
        try:
            # Execute tasks in dependency order
            while not self._all_tasks_complete(workflow):
                # Find next executable task
                next_task = self._get_next_task(workflow)
                
                if next_task is None:
                    # No more tasks to execute
                    if not self._all_tasks_complete(workflow):
                        # Some tasks are blocked or failed
                        print(f"❌ Workflow blocked or failed")
                        self._compensate_workflow(workflow)
                        return False
                    break
                
                # Execute task
                success = self._execute_task(next_task, workflow.context)
                
                if success:
                    workflow.completed_tasks.append(next_task.task_id)
                    print(f"✓ Task completed: {next_task.name}")
                    
                    # Checkpoint after each task
                    if workflow.checkpoint_enabled and self.checkpoint_manager:
                        self._create_workflow_checkpoint(workflow)
                else:
                    workflow.failed_tasks.append(next_task.task_id)
                    print(f"❌ Task failed: {next_task.name}")
                    
                    # Trigger compensation
                    print(f"🔄 Starting compensation...")
                    self._compensate_workflow(workflow)
                    return False
            
            print(f"✓ Workflow completed: {workflow.name}")
            return True
        
        except Exception as e:
            print(f"❌ Workflow error: {e}")
            traceback.print_exc()
            self._compensate_workflow(workflow)
            return False
    
    def _get_next_task(self, workflow: Workflow) -> Optional[Task]:
        """
        Get the next task ready to execute.
        
        Returns None if no task is ready (all complete or blocked).
        """
        for task in workflow.tasks:
            # Skip if already completed or failed
            if task.task_id in workflow.completed_tasks:
                continue
            if task.task_id in workflow.failed_tasks:
                continue
            
            # Skip if currently running
            if task.status == TaskStatus.RUNNING:
                continue
            
            # Check dependencies
            deps_satisfied = all(
                dep_id in workflow.completed_tasks
                for dep_id in task.dependencies
            )
            
            if deps_satisfied:
                return task
        
        return None
    
    def _all_tasks_complete(self, workflow: Workflow) -> bool:
        """Check if all tasks are complete."""
        return len(workflow.completed_tasks) == len(workflow.tasks)
    
    def _execute_task(self, task: Task, context: Dict[str, Any]) -> bool:
        """
        Execute a single task with retries.
        
        Args:
            task: Task to execute
            context: Workflow context
        
        Returns:
            True if task succeeded, False if it failed after all retries
        """
        # Phase 3: Check if task requires sandboxed execution
        if task.sandboxed and self.sandbox_manager:
            return self._execute_task_sandboxed(task, context)
        
        # Standard (unsandboxed) execution
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now(timezone.utc).isoformat()
        
        for attempt in range(task.retry_policy.max_attempts):
            task.attempts = attempt + 1
            
            try:
                print(f"  Executing {task.name} (attempt {attempt + 1}/{task.retry_policy.max_attempts})...")
                
                # Execute task action
                result = task.action(context)
                
                # Success
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now(timezone.utc).isoformat()
                task.result = result
                task.last_error = None
                
                return True
            
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                task.last_error = error_msg
                
                print(f"  ⚠ Attempt {attempt + 1} failed: {error_msg}")
                
                # Check if we should retry
                if attempt < task.retry_policy.max_attempts - 1:
                    task.status = TaskStatus.RETRYING
                    
                    # Calculate retry delay
                    delay = task.retry_policy.get_delay(attempt)
                    print(f"  Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                else:
                    # All retries exhausted
                    task.status = TaskStatus.FAILED
                    task.completed_at = datetime.now(timezone.utc).isoformat()
                    
                    print(f"  ❌ Task failed after {task.retry_policy.max_attempts} attempts")
                    return False
        
        return False
    
    def _execute_task_sandboxed(self, task: Task, context: Dict[str, Any]) -> bool:
        """
        Execute task in isolated sandbox.
        
        Args:
            task: Task to execute (must have sandboxed=True)
            context: Workflow context
        
        Returns:
            True if task succeeded, False otherwise
        """
        print(f"  🔒 Executing {task.name} in sandbox...")
        
        # Generate sandbox ID
        sandbox_id = f"workflow-{task.task_id}-{int(time.time())}"
        task.sandbox_id = sandbox_id
        
        sandbox = None
        
        try:
            # Create sandbox with capabilities
            sandbox = self.sandbox_manager.create_sandbox(
                sandbox_id=sandbox_id,
                capabilities=task.capabilities,
                resource_limits=task.resource_limits
            )
            
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now(timezone.utc).isoformat()
            
            # Execute with retries
            for attempt in range(task.retry_policy.max_attempts):
                task.attempts = attempt + 1
                
                try:
                    print(f"    Sandboxed execution (attempt {attempt + 1}/{task.retry_policy.max_attempts})...")
                    
                    # Execute task action with sandbox context
                    context['sandbox'] = sandbox
                    context['sandbox_manager'] = self.sandbox_manager
                    result = task.action(context)
                    
                    # Success
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.now(timezone.utc).isoformat()
                    task.result = result
                    task.last_error = None
                    
                    print(f"    ✓ Sandboxed execution succeeded")
                    return True
                
                except Exception as e:
                    error_msg = f"{type(e).__name__}: {str(e)}"
                    task.last_error = error_msg
                    
                    print(f"    ⚠ Sandboxed attempt {attempt + 1} failed: {error_msg}")
                    
                    # Check if we should retry
                    if attempt < task.retry_policy.max_attempts - 1:
                        task.status = TaskStatus.RETRYING
                        delay = task.retry_policy.get_delay(attempt)
                        print(f"    Retrying in {delay:.1f}s...")
                        time.sleep(delay)
                    else:
                        # All retries exhausted
                        task.status = TaskStatus.FAILED
                        task.completed_at = datetime.now(timezone.utc).isoformat()
                        print(f"    ❌ Sandboxed task failed after {task.retry_policy.max_attempts} attempts")
                        return False
        
        finally:
            # Always clean up sandbox
            if sandbox:
                try:
                    self.sandbox_manager.destroy_sandbox(sandbox_id)
                    print(f"    🗑️  Sandbox cleaned up: {sandbox_id}")
                except Exception as e:
                    print(f"    ⚠️  Failed to cleanup sandbox: {e}")
        
        return False
        
        return False
    
    def _compensate_workflow(self, workflow: Workflow):
        """
        Compensate (rollback) completed tasks in reverse order.
        
        This implements the Saga pattern for distributed transactions.
        """
        print(f"🔄 Compensating workflow: {workflow.name}")
        
        # Compensate in reverse order
        for task_id in reversed(workflow.completed_tasks):
            task = self._get_task_by_id(workflow, task_id)
            
            if task and task.compensation:
                try:
                    print(f"  Compensating {task.name}...")
                    task.status = TaskStatus.COMPENSATING
                    
                    # Execute compensation
                    task.compensation(workflow.context)
                    
                    task.status = TaskStatus.COMPENSATED
                    workflow.compensated_tasks.append(task_id)
                    
                    print(f"  ✓ Compensated {task.name}")
                
                except Exception as e:
                    print(f"  ⚠ Compensation failed for {task.name}: {e}")
                    # Continue compensating other tasks
    
    def _get_task_by_id(self, workflow: Workflow, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        for task in workflow.tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def _create_workflow_checkpoint(self, workflow: Workflow):
        """Create checkpoint after task completion."""
        if not self.checkpoint_manager:
            return
        
        state = CheckpointState(
            sprint_id=workflow.workflow_id,
            phase="workflow_execution",
            fsm_state="RUNNING",
            logical_time=len(workflow.completed_tasks),
            context=workflow.context,
            ledger_items=[],
            active_tasks=[
                {"task_id": t.task_id, "status": t.status.value}
                for t in workflow.tasks
                if t.status in [TaskStatus.RUNNING, TaskStatus.RETRYING]
            ],
            completed_tasks=[
                {"task_id": t.task_id, "result": str(t.result)}
                for t in workflow.tasks
                if t.task_id in workflow.completed_tasks
            ],
            environment={},
            metadata={
                "workflow_id": workflow.workflow_id,
                "workflow_name": workflow.name,
                "completed_count": len(workflow.completed_tasks),
                "failed_count": len(workflow.failed_tasks)
            }
        )
        
        checkpoint_id = self.checkpoint_manager.create_checkpoint(
            phase="workflow_execution",
            state=state,
            artifacts=[]
        )
        
        print(f"  📍 Checkpoint created: {checkpoint_id[:8]}...")


# =============================================================================
# Example Workflow
# =============================================================================

def example_workflow():
    """Example workflow with tasks and retries."""
    
    # Define tasks
    def task1_action(context):
        print("    Task 1: Load configuration")
        context['config_loaded'] = True
        return {'status': 'ok'}
    
    def task2_action(context):
        print("    Task 2: Validate inputs")
        if not context.get('config_loaded'):
            raise ValueError("Config not loaded")
        context['validation_passed'] = True
        return {'status': 'ok'}
    
    def task3_action(context):
        print("    Task 3: Process data")
        # Simulate occasional failure
        import random
        if random.random() < 0.3:
            raise RuntimeError("Simulated processing error")
        context['data_processed'] = True
        return {'status': 'ok', 'records': 100}
    
    def task3_compensation(context):
        print("    Task 3 compensation: Clean up processed data")
        context['data_processed'] = False
    
    task1 = Task(
        task_id="task-1",
        name="Load Configuration",
        action=task1_action,
        dependencies=[]
    )
    
    task2 = Task(
        task_id="task-2",
        name="Validate Inputs",
        action=task2_action,
        dependencies=["task-1"]
    )
    
    task3 = Task(
        task_id="task-3",
        name="Process Data",
        action=task3_action,
        compensation=task3_compensation,
        dependencies=["task-2"],
        retry_policy=RetryPolicy(max_attempts=5, initial_delay_seconds=0.5)
    )
    
    workflow = Workflow(
        workflow_id="example-workflow",
        name="Example Data Processing",
        tasks=[task1, task2, task3],
        checkpoint_enabled=False  # Disable for example
    )
    
    return workflow


if __name__ == "__main__":
    from db import Database
    
    # Initialize
    db = Database()
    engine = WorkflowEngine(db)
    
    # Create and execute example workflow
    workflow = example_workflow()
    
    success = engine.execute(workflow)
    
    if success:
        print("\n✓ Workflow completed successfully")
        print(f"  Completed tasks: {len(workflow.completed_tasks)}")
        print(f"  Context: {workflow.context}")
    else:
        print("\n❌ Workflow failed")
        print(f"  Completed tasks: {workflow.completed_tasks}")
        print(f"  Failed tasks: {workflow.failed_tasks}")
        print(f"  Compensated tasks: {workflow.compensated_tasks}")
    
    db.close()
