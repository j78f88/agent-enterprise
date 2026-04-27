"""
Deterministic Composition

Content-based hashing for deterministic tie-breaking and replay verification.
Ensures composition produces identical results on replay.

Phase 4 - Determinism & Replay
"""

import hashlib
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path


# =============================================================================
# Content Hashing
# =============================================================================

def content_hash(item: Dict[str, Any], fields: Optional[List[str]] = None) -> str:
    """
    Compute deterministic content hash for an item.
    
    Uses canonical JSON serialization (sorted keys) to ensure
    identical content produces identical hashes.
    
    Args:
        item: Dictionary to hash
        fields: Specific fields to include (None = all fields)
    
    Returns:
        SHA256 hash (first 12 characters)
    """
    # Select fields to hash
    if fields:
        content = {k: item.get(k) for k in fields if k in item}
    else:
        content = item.copy()
    
    # Serialize to canonical JSON (sorted keys)
    json_str = json.dumps(content, sort_keys=True, ensure_ascii=True)
    
    # Compute SHA256 hash
    full_hash = hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    # Return short hash (12 chars)
    return full_hash[:12]


def ledger_item_hash(item: Dict[str, Any]) -> str:
    """
    Compute content hash for ledger item.
    
    Includes: type, source_id, notes, created_at
    Excludes: age, def (change over time), item_id (arbitrary)
    
    Args:
        item: Ledger item dictionary
    
    Returns:
        Content hash
    """
    fields = ['type', 'source_id', 'notes', 'created_at']
    return content_hash(item, fields)


def bug_hash(bug: Dict[str, Any]) -> str:
    """
    Compute content hash for bug.
    
    Includes: title, severity, observed, expected
    
    Args:
        bug: Bug dictionary
    
    Returns:
        Content hash
    """
    fields = ['title', 'severity', 'observed', 'expected']
    return content_hash(bug, fields)


# =============================================================================
# Deterministic Sorting
# =============================================================================

def sort_items_deterministic(
    items: List[Dict[str, Any]],
    score_key: str = 'score',
    hash_fields: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Sort items deterministically using content-based tie-breaking.
    
    Primary sort: by score (descending)
    Tie-breaker: by content hash (lexicographic)
    
    Args:
        items: List of items to sort
        score_key: Key for primary sort score
        hash_fields: Fields to include in content hash
    
    Returns:
        Sorted list of items
    """
    def sort_key(item):
        score = item.get(score_key, 0)
        hash_val = content_hash(item, hash_fields)
        return (-score, hash_val)  # Negative score for descending
    
    return sorted(items, key=sort_key)


def sort_bugs_deterministic(bugs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort bugs deterministically.
    
    Priority order:
    1. Severity (CRITICAL > HIGH > MEDIUM > LOW)
    2. Content hash (tie-breaker)
    
    Args:
        bugs: List of bugs
    
    Returns:
        Sorted list of bugs
    """
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    
    def sort_key(bug):
        severity = bug.get('severity', 'LOW')
        severity_rank = severity_order.get(severity, 999)
        hash_val = bug_hash(bug)
        return (severity_rank, hash_val)
    
    return sorted(bugs, key=sort_key)


# =============================================================================
# Composition Snapshot
# =============================================================================

@dataclass
class CompositionSnapshot:
    """
    Immutable snapshot of composition inputs.
    
    Captures complete state before composition for reproducibility.
    """
    
    snapshot_id: str  # SHA256 hash of entire snapshot
    created_at: str
    logical_time: int
    
    # Input state
    ledger_items: List[Dict[str, Any]]
    bugs: List[Dict[str, Any]]
    constraints: Dict[str, Any]
    config: Dict[str, Any]
    
    # Metadata
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'CompositionSnapshot':
        """Deserialize from dictionary."""
        return CompositionSnapshot(**data)


class CompositionSnapshotter:
    """
    Creates and manages composition snapshots for replay verification.
    
    Usage:
        snapshotter = CompositionSnapshotter()
        
        # Create snapshot before composition
        snapshot = snapshotter.create_snapshot(
            ledger_items=items,
            bugs=bugs,
            constraints=constraints
        )
        
        # Run composition
        result = run_composition(snapshot)
        
        # Later: Replay from snapshot
        snapshot = snapshotter.load_snapshot(snapshot_id)
        result_replay = run_composition(snapshot)
        
        # Verify identical
        assert result == result_replay
    """
    
    def __init__(self, state_dir: str = ".agent-state/snapshots"):
        """
        Initialize composition snapshotter.
        
        Args:
            state_dir: Directory for snapshot storage
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
    
    def create_snapshot(
        self,
        ledger_items: List[Dict[str, Any]],
        bugs: List[Dict[str, Any]],
        constraints: Dict[str, Any],
        config: Dict[str, Any],
        logical_time: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CompositionSnapshot:
        """
        Create composition snapshot.
        
        Args:
            ledger_items: Open ledger items
            bugs: Open bugs
            constraints: Composition constraints
            config: Configuration tokens
            logical_time: Logical timestamp
            metadata: Additional metadata
        
        Returns:
            CompositionSnapshot
        """
        metadata = metadata or {}
        
        # Build snapshot data
        snapshot_data = {
            'ledger_items': ledger_items,
            'bugs': bugs,
            'constraints': constraints,
            'config': config,
            'logical_time': logical_time,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'metadata': metadata
        }
        
        # Compute content-addressable ID
        snapshot_json = json.dumps(snapshot_data, sort_keys=True, ensure_ascii=True)
        snapshot_id = hashlib.sha256(snapshot_json.encode('utf-8')).hexdigest()[:16]
        
        # Create snapshot object
        snapshot = CompositionSnapshot(
            snapshot_id=snapshot_id,
            created_at=snapshot_data['created_at'],
            logical_time=logical_time,
            ledger_items=ledger_items,
            bugs=bugs,
            constraints=constraints,
            config=config,
            metadata=metadata
        )
        
        # Save to disk
        self._save_snapshot(snapshot)
        
        return snapshot
    
    def load_snapshot(self, snapshot_id: str) -> Optional[CompositionSnapshot]:
        """
        Load snapshot by ID.
        
        Args:
            snapshot_id: Snapshot identifier
        
        Returns:
            CompositionSnapshot or None if not found
        """
        snapshot_file = self.state_dir / f"{snapshot_id}.json"
        
        if not snapshot_file.exists():
            return None
        
        try:
            with open(snapshot_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return CompositionSnapshot.from_dict(data)
        except Exception as e:
            print(f"⚠️  Failed to load snapshot {snapshot_id}: {e}")
            return None
    
    def list_snapshots(self) -> List[str]:
        """
        List all snapshot IDs.
        
        Returns:
            List of snapshot IDs
        """
        return [f.stem for f in self.state_dir.glob("*.json")]
    
    def _save_snapshot(self, snapshot: CompositionSnapshot):
        """Save snapshot to disk."""
        snapshot_file = self.state_dir / f"{snapshot.snapshot_id}.json"
        
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot.to_dict(), f, indent=2)


# =============================================================================
# Deterministic File Operations
# =============================================================================

def list_files_deterministic(path: Path, pattern: str = "*") -> List[Path]:
    """
    List files in deterministic order (sorted lexicographically).
    
    os.listdir() and Path.glob() return files in undefined order.
    This function ensures deterministic ordering.
    
    Args:
        path: Directory path
        pattern: Glob pattern (default: "*")
    
    Returns:
        Sorted list of Path objects
    """
    return sorted(path.glob(pattern))


def rglob_deterministic(path: Path, pattern: str) -> List[Path]:
    """
    Recursive glob with deterministic ordering.
    
    Args:
        path: Directory path
        pattern: Glob pattern
    
    Returns:
        Sorted list of Path objects
    """
    return sorted(path.rglob(pattern))


# =============================================================================
# Composition Result
# =============================================================================

@dataclass
class CompositionResult:
    """
    Result of composition with versioning information.
    """
    
    selected_items: List[str]  # Item IDs
    total_complexity: int
    snapshot_id: str
    composition_hash: str  # Hash of result for verification
    logical_time: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'CompositionResult':
        """Deserialize from dictionary."""
        return CompositionResult(**data)
    
    def compute_hash(self) -> str:
        """Compute hash of composition result."""
        content = {
            'selected_items': sorted(self.selected_items),  # Sort for determinism
            'total_complexity': self.total_complexity
        }
        json_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()[:12]


# =============================================================================
# Replay Verification
# =============================================================================

class ReplayVerifier:
    """
    Verifies determinism by comparing original and replayed executions.
    
    Usage:
        verifier = ReplayVerifier()
        
        # Original execution
        result1 = run_composition(snapshot)
        verifier.record_result("composition-1", result1)
        
        # Replay
        result2 = run_composition(snapshot)
        
        # Verify identical
        is_deterministic = verifier.verify("composition-1", result2)
    """
    
    def __init__(self, state_dir: str = ".agent-state"):
        """
        Initialize replay verifier.
        
        Args:
            state_dir: Directory for result storage
        """
        self.state_dir = Path(state_dir)
        self.results_file = self.state_dir / "composition-results.jsonl"
    
    def record_result(self, run_id: str, result: CompositionResult):
        """
        Record composition result for later verification.
        
        Args:
            run_id: Unique run identifier
            result: Composition result
        """
        record = {
            'run_id': run_id,
            'result': result.to_dict(),
            'recorded_at': datetime.now(timezone.utc).isoformat()
        }
        
        with open(self.results_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + '\n')
    
    def verify(self, run_id: str, replay_result: CompositionResult) -> bool:
        """
        Verify replay result matches original.
        
        Args:
            run_id: Original run identifier
            replay_result: Result from replay
        
        Returns:
            True if results match, False otherwise
        """
        # Find original result
        original = self._find_result(run_id)
        
        if not original:
            print(f"⚠️  No original result found for {run_id}")
            return False
        
        # Compare hashes
        original_hash = original.composition_hash
        replay_hash = replay_result.compute_hash()
        
        if original_hash != replay_hash:
            print(f"❌ Determinism violation!")
            print(f"   Original hash: {original_hash}")
            print(f"   Replay hash:   {replay_hash}")
            return False
        
        print(f"✓ Determinism verified: {run_id}")
        return True
    
    def _find_result(self, run_id: str) -> Optional[CompositionResult]:
        """Find result by run ID."""
        if not self.results_file.exists():
            return None
        
        with open(self.results_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    record = json.loads(line)
                    if record['run_id'] == run_id:
                        return CompositionResult.from_dict(record['result'])
                except Exception:
                    continue
        
        return None


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    print("=== Deterministic Composition Demo ===\n")
    
    # Sample ledger items
    items = [
        {'item_id': 'ITEM-001', 'type': 'feature', 'score': 10, 'notes': 'Feature A'},
        {'item_id': 'ITEM-002', 'type': 'bug', 'score': 10, 'notes': 'Bug B'},  # Same score
        {'item_id': 'ITEM-003', 'type': 'feature', 'score': 8, 'notes': 'Feature C'},
    ]
    
    print("--- Original order ---")
    for item in items:
        print(f"  {item['item_id']}: score={item['score']}")
    
    # Sort deterministically
    sorted_items = sort_items_deterministic(items, score_key='score')
    
    print("\n--- Deterministic sort (with content-based tie-breaking) ---")
    for item in sorted_items:
        hash_val = content_hash(item, ['type', 'notes'])
        print(f"  {item['item_id']}: score={item['score']}, hash={hash_val}")
    
    # Create snapshot
    print("\n--- Creating composition snapshot ---\n")
    
    snapshotter = CompositionSnapshotter()
    
    snapshot = snapshotter.create_snapshot(
        ledger_items=items,
        bugs=[],
        constraints={'max_items': 5, 'max_complexity': 13},
        config={'project_type': 'web-app'},
        logical_time=100
    )
    
    print(f"Snapshot ID: {snapshot.snapshot_id}")
    print(f"Logical time: {snapshot.logical_time}")
    print(f"Items: {len(snapshot.ledger_items)}")
    
    # Simulate composition result
    result = CompositionResult(
        selected_items=['ITEM-001', 'ITEM-003'],
        total_complexity=18,
        snapshot_id=snapshot.snapshot_id,
        composition_hash='',  # Will be computed
        logical_time=101,
        metadata={}
    )
    result.composition_hash = result.compute_hash()
    
    print(f"\nComposition result hash: {result.composition_hash}")
    
    # Verify determinism
    print("\n--- Verifying determinism ---\n")
    
    verifier = ReplayVerifier()
    verifier.record_result("run-1", result)
    
    # Simulate replay (same result)
    result_replay = CompositionResult(
        selected_items=['ITEM-001', 'ITEM-003'],
        total_complexity=18,
        snapshot_id=snapshot.snapshot_id,
        composition_hash='',
        logical_time=101,
        metadata={}
    )
    result_replay.composition_hash = result_replay.compute_hash()
    
    is_deterministic = verifier.verify("run-1", result_replay)
    
    print(f"\n✓ Demo complete")
