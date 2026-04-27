"""
Checkpoint-Restart System

Enables resume-safe execution with state snapshots and recovery.
Phase 2 - Durable Execution

Features:
- Automatic checkpoint creation at phase boundaries
- State serialization with compression
- Resume from any checkpoint
- Rollback to previous checkpoint
- Checkpoint history and diff
"""

import json
import gzip
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

from db import Database


# =============================================================================
# Checkpoint Data Structures
# =============================================================================

@dataclass
class CheckpointMetadata:
    """Metadata for a checkpoint."""
    checkpoint_id: str
    sprint_id: str
    phase: str
    created_at: str
    state_hash: str
    artifact_count: int
    size_bytes: int


@dataclass
class CheckpointState:
    """Complete state snapshot."""
    sprint_id: str
    phase: str
    fsm_state: str
    logical_time: int
    context: Dict[str, Any]
    ledger_items: List[Dict[str, Any]]
    active_tasks: List[Dict[str, Any]]
    completed_tasks: List[Dict[str, Any]]
    environment: Dict[str, str]
    metadata: Dict[str, Any]
    
    # Phase 3: Sandbox state tracking
    active_sandboxes: List[Dict[str, Any]] = None  # Currently running sandboxes
    sandbox_history: List[Dict[str, Any]] = None   # All sandboxes used in sprint
    
    def __post_init__(self):
        """Initialize sandbox state if not provided."""
        if self.active_sandboxes is None:
            self.active_sandboxes = []
        if self.sandbox_history is None:
            self.sandbox_history = []


# =============================================================================
# Checkpoint Manager
# =============================================================================

class CheckpointManager:
    """
    Manages checkpoint creation, restoration, and history.
    
    Usage:
        cm = CheckpointManager(db, sprint_id="042")
        
        # Create checkpoint
        checkpoint_id = cm.create_checkpoint(
            phase="implementation",
            state=current_state,
            artifacts=["docs/sprint-042.md"]
        )
        
        # Resume from checkpoint
        state, artifacts = cm.restore_checkpoint(checkpoint_id)
    """
    
    def __init__(
        self,
        db: Database,
        sprint_id: str,
        checkpoint_dir: str = ".agent-state/checkpoints"
    ):
        """
        Initialize checkpoint manager.
        
        Args:
            db: Database instance
            sprint_id: Sprint identifier
            checkpoint_dir: Directory for checkpoint artifacts
        """
        self.db = db
        self.sprint_id = sprint_id
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def create_checkpoint(
        self,
        phase: str,
        state: CheckpointState,
        artifacts: Optional[List[str]] = None
    ) -> str:
        """
        Create a checkpoint snapshot.
        
        Args:
            phase: Current phase (planning, implementation, etc.)
            state: Complete state object
            artifacts: List of artifact file paths
        
        Returns:
            checkpoint_id
        """
        artifacts = artifacts or []
        
        # Serialize state
        state_dict = asdict(state)
        state_json = json.dumps(state_dict, sort_keys=True)
        
        # Compute hash
        checkpoint_id = hashlib.sha256(state_json.encode()).hexdigest()
        
        # Compress state for storage
        compressed_state = gzip.compress(state_json.encode())
        
        # Save to database
        with self.db.transaction():
            self.db.create_checkpoint(
                sprint_id=self.sprint_id,
                phase=phase,
                state=state_dict,
                artifact_paths=artifacts
            )
        
        # Save compressed state to file
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json.gz"
        checkpoint_file.write_bytes(compressed_state)
        
        # Save metadata
        metadata = CheckpointMetadata(
            checkpoint_id=checkpoint_id,
            sprint_id=self.sprint_id,
            phase=phase,
            created_at=datetime.now(timezone.utc).isoformat(),
            state_hash=checkpoint_id,
            artifact_count=len(artifacts),
            size_bytes=len(compressed_state)
        )
        
        metadata_file = self.checkpoint_dir / f"{checkpoint_id}.meta.json"
        metadata_file.write_text(json.dumps(asdict(metadata), indent=2), encoding='utf-8')
        
        return checkpoint_id
    
    def restore_checkpoint(self, checkpoint_id: str) -> Tuple[CheckpointState, List[str]]:
        """
        Restore state from checkpoint.
        
        Args:
            checkpoint_id: Checkpoint ID to restore
        
        Returns:
            (CheckpointState, artifact_paths)
        """
        # Load from database
        state_dict, artifact_paths = self.db.restore_checkpoint(checkpoint_id)
        
        # Reconstruct CheckpointState
        state = CheckpointState(**state_dict)
        
        return state, artifact_paths
    
    def get_checkpoint_metadata(self, checkpoint_id: str) -> Optional[CheckpointMetadata]:
        """Get checkpoint metadata."""
        metadata_file = self.checkpoint_dir / f"{checkpoint_id}.meta.json"
        
        if not metadata_file.exists():
            return None
        
        metadata_dict = json.loads(metadata_file.read_text(encoding='utf-8'))
        return CheckpointMetadata(**metadata_dict)
    
    def list_checkpoints(self) -> List[CheckpointMetadata]:
        """List all checkpoints for the sprint."""
        checkpoints = []
        
        for meta_file in self.checkpoint_dir.glob(f"*.meta.json"):
            try:
                metadata_dict = json.loads(meta_file.read_text(encoding='utf-8'))
                if metadata_dict['sprint_id'] == self.sprint_id:
                    checkpoints.append(CheckpointMetadata(**metadata_dict))
            except Exception:
                pass  # Skip invalid metadata files
        
        # Sort by creation time
        checkpoints.sort(key=lambda cp: cp.created_at, reverse=True)
        
        return checkpoints
    
    def get_latest_checkpoint(self) -> Optional[CheckpointMetadata]:
        """Get the most recent checkpoint for this sprint."""
        checkpoints = self.list_checkpoints()
        return checkpoints[0] if checkpoints else None
    
    def delete_checkpoint(self, checkpoint_id: str):
        """Delete a checkpoint."""
        # Delete from database
        self.db.conn.execute(
            "DELETE FROM checkpoints WHERE checkpoint_id = ?",
            (checkpoint_id,)
        )
        self.db.conn.commit()
        
        # Delete files
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json.gz"
        metadata_file = self.checkpoint_dir / f"{checkpoint_id}.meta.json"
        
        if checkpoint_file.exists():
            checkpoint_file.unlink()
        
        if metadata_file.exists():
            metadata_file.unlink()
    
    def diff_checkpoints(
        self,
        checkpoint_id_1: str,
        checkpoint_id_2: str
    ) -> Dict[str, Any]:
        """
        Compare two checkpoints and return differences.
        
        Args:
            checkpoint_id_1: First checkpoint (older)
            checkpoint_id_2: Second checkpoint (newer)
        
        Returns:
            Dictionary of differences
        """
        state1, _ = self.restore_checkpoint(checkpoint_id_1)
        state2, _ = self.restore_checkpoint(checkpoint_id_2)
        
        diffs = {
            'phase_change': state1.phase != state2.phase,
            'fsm_state_change': state1.fsm_state != state2.fsm_state,
            'logical_time_delta': state2.logical_time - state1.logical_time,
            'completed_tasks_delta': len(state2.completed_tasks) - len(state1.completed_tasks),
            'active_tasks_delta': len(state2.active_tasks) - len(state1.active_tasks),
            'ledger_changes': self._diff_ledger(state1.ledger_items, state2.ledger_items)
        }
        
        return diffs
    
    def _diff_ledger(
        self,
        ledger1: List[Dict[str, Any]],
        ledger2: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare two ledger snapshots."""
        items1 = {item['item_id']: item for item in ledger1}
        items2 = {item['item_id']: item for item in ledger2}
        
        added = set(items2.keys()) - set(items1.keys())
        removed = set(items1.keys()) - set(items2.keys())
        
        changed = []
        for item_id in set(items1.keys()) & set(items2.keys()):
            if items1[item_id] != items2[item_id]:
                changed.append(item_id)
        
        return {
            'added': list(added),
            'removed': list(removed),
            'changed': changed
        }
    
    def cleanup_old_checkpoints(self, keep_count: int = 10):
        """
        Delete old checkpoints, keeping only the most recent N.
        
        Args:
            keep_count: Number of recent checkpoints to keep
        """
        checkpoints = self.list_checkpoints()
        
        if len(checkpoints) <= keep_count:
            return  # Nothing to clean up
        
        # Delete oldest checkpoints
        to_delete = checkpoints[keep_count:]
        
        for checkpoint in to_delete:
            self.delete_checkpoint(checkpoint.checkpoint_id)
            print(f"🗑️  Deleted old checkpoint: {checkpoint.checkpoint_id} ({checkpoint.phase})")


# =============================================================================
# Resume Protocol
# =============================================================================

class ResumeManager:
    """
    Manages sprint resume logic.
    
    Coordinates checkpoint restoration with FSM state recovery.
    """
    
    def __init__(self, db: Database, checkpoint_manager: CheckpointManager):
        """
        Initialize resume manager.
        
        Args:
            db: Database instance
            checkpoint_manager: Checkpoint manager instance
        """
        self.db = db
        self.checkpoint_manager = checkpoint_manager
    
    def can_resume(self, sprint_id: str) -> bool:
        """Check if sprint can be resumed."""
        latest = self.checkpoint_manager.get_latest_checkpoint()
        return latest is not None
    
    def resume_sprint(self, sprint_id: str) -> Tuple[CheckpointState, List[str]]:
        """
        Resume sprint from latest checkpoint.
        
        Args:
            sprint_id: Sprint to resume
        
        Returns:
            (restored_state, artifact_paths)
        """
        latest = self.checkpoint_manager.get_latest_checkpoint()
        
        if not latest:
            raise ValueError(f"No checkpoint found for sprint {sprint_id}")
        
        print(f"📍 Resuming from checkpoint: {latest.checkpoint_id}")
        print(f"   Phase: {latest.phase}")
        print(f"   Created: {latest.created_at}")
        
        # Restore checkpoint
        state, artifacts = self.checkpoint_manager.restore_checkpoint(latest.checkpoint_id)
        
        # Verify artifacts exist
        missing_artifacts = []
        for artifact_path in artifacts:
            if not Path(artifact_path).exists():
                missing_artifacts.append(artifact_path)
        
        if missing_artifacts:
            print(f"⚠️  Warning: {len(missing_artifacts)} artifacts missing:")
            for artifact in missing_artifacts:
                print(f"   • {artifact}")
        
        # Restore database state
        self._restore_database_state(state)
        
        print(f"✓ Sprint {sprint_id} resumed from {state.phase}")
        
        return state, artifacts
    
    def _restore_database_state(self, state: CheckpointState):
        """Restore database to checkpoint state."""
        with self.db.transaction():
            # Restore ledger items
            for item_dict in state.ledger_items:
                # Update or insert
                existing = self.db.get_ledger_item(item_dict['item_id'])
                if existing:
                    self.db.update_ledger_item(item_dict['item_id'], item_dict)
                else:
                    # Would need to convert dict to LedgerItem
                    pass
    
    def rollback_to_phase(self, sprint_id: str, phase: str) -> CheckpointState:
        """
        Rollback to the last checkpoint in a specific phase.
        
        Args:
            sprint_id: Sprint ID
            phase: Phase to rollback to
        
        Returns:
            Restored state
        """
        checkpoints = self.checkpoint_manager.list_checkpoints()
        
        # Find most recent checkpoint in the target phase
        target_checkpoint = None
        for checkpoint in checkpoints:
            if checkpoint.phase == phase:
                target_checkpoint = checkpoint
                break
        
        if not target_checkpoint:
            raise ValueError(f"No checkpoint found for phase: {phase}")
        
        print(f"⏮️  Rolling back to {phase} (checkpoint: {target_checkpoint.checkpoint_id})")
        
        state, artifacts = self.checkpoint_manager.restore_checkpoint(target_checkpoint.checkpoint_id)
        self._restore_database_state(state)
        
        return state


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    from db import Database
    
    # Initialize
    db = Database()
    cm = CheckpointManager(db, sprint_id="042")
    
    # Create example checkpoint
    state = CheckpointState(
        sprint_id="042",
        phase="implementation",
        fsm_state="IMPLEMENTATION",
        logical_time=15,
        context={"task_count": 8, "completed": 3},
        ledger_items=[],
        active_tasks=[{"task_id": "task-1", "status": "in-progress"}],
        completed_tasks=[{"task_id": "task-0", "status": "complete"}],
        environment={"git_branch": "sprint-042"},
        metadata={"notes": "Checkpoint after task completion"}
    )
    
    checkpoint_id = cm.create_checkpoint(
        phase="implementation",
        state=state,
        artifacts=["docs/sprint-042.md"]
    )
    
    print(f"✓ Created checkpoint: {checkpoint_id}")
    
    # List checkpoints
    checkpoints = cm.list_checkpoints()
    print(f"\n📋 Found {len(checkpoints)} checkpoints:")
    for cp in checkpoints:
        print(f"   • {cp.phase} - {cp.created_at} ({cp.size_bytes} bytes)")
    
    # Restore checkpoint
    restored_state, artifacts = cm.restore_checkpoint(checkpoint_id)
    print(f"\n✓ Restored checkpoint:")
    print(f"   Phase: {restored_state.phase}")
    print(f"   FSM State: {restored_state.fsm_state}")
    print(f"   Logical Time: {restored_state.logical_time}")
    print(f"   Active Tasks: {len(restored_state.active_tasks)}")
    print(f"   Completed Tasks: {len(restored_state.completed_tasks)}")
    
    db.close()
