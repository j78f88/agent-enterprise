"""
Sandbox Checkpoint Integration

Utilities for tracking sandbox state in checkpoints and resuming sandboxes.
Phase 3 - Sandboxing & Isolation
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

from checkpoint import CheckpointState, CheckpointManager
from sandbox import SandboxManager, SandboxState, Sandbox
from capabilities import Capability


# =============================================================================
# Sandbox Checkpoint Utilities
# =============================================================================

class SandboxCheckpointManager:
    """
    Manages sandbox state tracking in checkpoints.
    
    Responsibilities:
    - Capture active sandbox state for checkpoints
    - Restore sandboxes from checkpoint state
    - Track sandbox history across sprint
    - Handle sandbox cleanup on resume
    
    Usage:
        scm = SandboxCheckpointManager(checkpoint_mgr, sandbox_mgr)
        
        # Capture sandbox state
        checkpoint_state = scm.create_checkpoint_with_sandboxes(
            phase="implementation",
            base_state=state,
            artifacts=["docs/sprint.md"]
        )
        
        # Resume with sandbox restoration
        state, sandboxes = scm.resume_from_checkpoint(checkpoint_id)
    """
    
    def __init__(
        self,
        checkpoint_manager: CheckpointManager,
        sandbox_manager: SandboxManager
    ):
        """
        Initialize sandbox checkpoint manager.
        
        Args:
            checkpoint_manager: CheckpointManager instance
            sandbox_manager: SandboxManager instance
        """
        self.checkpoint_mgr = checkpoint_manager
        self.sandbox_mgr = sandbox_manager
    
    def create_checkpoint_with_sandboxes(
        self,
        phase: str,
        base_state: CheckpointState,
        artifacts: List[str]
    ) -> str:
        """
        Create checkpoint including sandbox state.
        
        Args:
            phase: Current phase
            base_state: Base checkpoint state
            artifacts: List of artifact paths
        
        Returns:
            Checkpoint ID
        """
        # Capture active sandbox state
        active_sandboxes = []
        for sandbox in self.sandbox_mgr.active_sandboxes.values():
            sandbox_dict = sandbox.state.to_dict()
            active_sandboxes.append(sandbox_dict)
        
        # Build sandbox history (append to existing)
        sandbox_history = base_state.sandbox_history.copy()
        
        # Add completed sandboxes to history
        for sandbox_dict in active_sandboxes:
            # Check if already in history
            if not any(s['sandbox_id'] == sandbox_dict['sandbox_id'] 
                      for s in sandbox_history):
                sandbox_history.append(sandbox_dict)
        
        # Update state with sandbox tracking
        base_state.active_sandboxes = active_sandboxes
        base_state.sandbox_history = sandbox_history
        
        # Create checkpoint
        checkpoint_id = self.checkpoint_mgr.create_checkpoint(
            phase=phase,
            state=base_state,
            artifacts=artifacts
        )
        
        print(f"📦 Checkpoint includes {len(active_sandboxes)} active sandboxes")
        print(f"   Sandbox history: {len(sandbox_history)} total sandboxes")
        
        return checkpoint_id
    
    def resume_from_checkpoint(
        self,
        checkpoint_id: str,
        recreate_sandboxes: bool = False
    ) -> Tuple[CheckpointState, Dict[str, Sandbox]]:
        """
        Resume from checkpoint with sandbox restoration.
        
        Args:
            checkpoint_id: Checkpoint to restore
            recreate_sandboxes: If True, recreate active sandboxes
        
        Returns:
            Tuple of (CheckpointState, dict of recreated sandboxes)
        """
        # Restore checkpoint
        state, artifacts = self.checkpoint_mgr.restore_checkpoint(checkpoint_id)
        
        sandboxes = {}
        
        if recreate_sandboxes and state.active_sandboxes:
            print(f"\n🔄 Recreating {len(state.active_sandboxes)} sandboxes...")
            
            for sandbox_dict in state.active_sandboxes:
                try:
                    # Recreate sandbox with same configuration
                    sandbox = self._recreate_sandbox(sandbox_dict)
                    sandboxes[sandbox.sandbox_id] = sandbox
                    print(f"  ✓ Recreated sandbox: {sandbox.sandbox_id}")
                except Exception as e:
                    print(f"  ⚠️  Failed to recreate sandbox {sandbox_dict['sandbox_id']}: {e}")
        
        return state, sandboxes
    
    def _recreate_sandbox(self, sandbox_dict: Dict) -> Sandbox:
        """
        Recreate sandbox from checkpoint state.
        
        Args:
            sandbox_dict: Serialized sandbox state
        
        Returns:
            Recreated Sandbox
        """
        from sandbox import ResourceLimits, NetworkPolicy
        
        # Parse resource limits
        resource_limits = ResourceLimits(**sandbox_dict['resource_limits'])
        
        # Parse network policy
        network_policy = NetworkPolicy(sandbox_dict['network_policy'])
        
        # Parse capabilities (if present)
        capabilities = []
        if sandbox_dict.get('capabilities'):
            capabilities = [
                Capability.from_dict(cap_dict)
                for cap_dict in sandbox_dict['capabilities']
            ]
        
        # Create new sandbox with same configuration
        sandbox = self.sandbox_mgr.create_sandbox(
            sandbox_id=f"{sandbox_dict['sandbox_id']}-resumed",
            capabilities=capabilities,
            resource_limits=resource_limits,
            network_policy=network_policy
        )
        
        return sandbox
    
    def cleanup_old_sandboxes(self):
        """Clean up any orphaned sandbox containers."""
        print("\n🧹 Cleaning up orphaned sandboxes...")
        
        try:
            # List all containers with agent-sandbox prefix
            containers = self.sandbox_mgr.client.containers.list(
                all=True,
                filters={'name': 'agent-sandbox-'}
            )
            
            removed_count = 0
            for container in containers:
                try:
                    container.remove(force=True)
                    removed_count += 1
                except Exception as e:
                    print(f"  ⚠️  Could not remove {container.name}: {e}")
            
            if removed_count > 0:
                print(f"  ✓ Removed {removed_count} orphaned containers")
            else:
                print("  ✓ No orphaned containers found")
        
        except Exception as e:
            print(f"  ⚠️  Cleanup failed: {e}")
    
    def get_sandbox_statistics(self, state: CheckpointState) -> Dict:
        """
        Get statistics about sandbox usage from checkpoint.
        
        Args:
            state: Checkpoint state
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_sandboxes': len(state.sandbox_history),
            'active_sandboxes': len(state.active_sandboxes),
            'total_cpu_seconds': 0.0,
            'total_memory_mb': 0,
            'total_commands': 0,
            'total_violations': 0
        }
        
        for sandbox_dict in state.sandbox_history:
            stats['total_cpu_seconds'] += sandbox_dict.get('cpu_usage_seconds', 0)
            stats['total_memory_mb'] += sandbox_dict.get('memory_peak_mb', 0)
            stats['total_commands'] += len(sandbox_dict.get('commands_executed', []))
            stats['total_violations'] += len(sandbox_dict.get('capability_violations', []))
        
        return stats


# =============================================================================
# Sandbox State Persistence
# =============================================================================

def serialize_sandbox_state(sandbox: Sandbox) -> Dict:
    """
    Serialize sandbox state for checkpoint.
    
    Args:
        sandbox: Sandbox to serialize
    
    Returns:
        Dictionary representation
    """
    return sandbox.state.to_dict()


def serialize_all_sandboxes(sandbox_manager: SandboxManager) -> List[Dict]:
    """
    Serialize all active sandboxes.
    
    Args:
        sandbox_manager: SandboxManager instance
    
    Returns:
        List of serialized sandbox states
    """
    return [
        sandbox.state.to_dict()
        for sandbox in sandbox_manager.active_sandboxes.values()
    ]


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    print("=== Sandbox Checkpoint Integration Demo ===\n")
    
    from db import Database
    from checkpoint import CheckpointManager, CheckpointState
    from sandbox import SandboxManager, ResourceLimits, NetworkPolicy
    from capabilities import CapabilityPresets
    
    # Initialize components
    db = Database()
    checkpoint_mgr = CheckpointManager(db, sprint_id="042")
    sandbox_mgr = SandboxManager()
    
    scm = SandboxCheckpointManager(checkpoint_mgr, sandbox_mgr)
    
    print("✓ Initialized sandbox checkpoint manager\n")
    
    # Create a test sandbox
    print("--- Creating test sandbox ---\n")
    
    sandbox = sandbox_mgr.create_sandbox(
        sandbox_id="test-sandbox-001",
        capabilities=CapabilityPresets.test_runner(),
        resource_limits=ResourceLimits(max_memory_mb=512),
        network_policy=NetworkPolicy.DENY_ALL
    )
    
    # Execute some commands
    result = sandbox_mgr.execute_in_sandbox(
        sandbox,
        command="echo 'Test command' && pwd"
    )
    
    print(f"\n✓ Executed test command (exit code: {result.exit_code})\n")
    
    # Create checkpoint with sandbox state
    print("--- Creating checkpoint with sandbox state ---\n")
    
    base_state = CheckpointState(
        sprint_id="042",
        phase="implementation",
        fsm_state="IMPLEMENTATION",
        logical_time=10,
        context={"current_task": "testing"},
        ledger_items=[],
        active_tasks=[{"task_id": "test-1"}],
        completed_tasks=[],
        environment={"git_branch": "sprint-042"},
        metadata={}
    )
    
    checkpoint_id = scm.create_checkpoint_with_sandboxes(
        phase="implementation",
        base_state=base_state,
        artifacts=["test.md"]
    )
    
    print(f"\n✓ Created checkpoint: {checkpoint_id[:16]}...\n")
    
    # Get sandbox statistics
    stats = scm.get_sandbox_statistics(base_state)
    print("--- Sandbox Statistics ---")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Clean up
    print("\n--- Cleaning up ---\n")
    sandbox_mgr.destroy_sandbox("test-sandbox-001")
    db.close()
    
    print("✓ Demo complete")
