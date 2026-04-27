"""
Logical Time - Lamport Timestamps

Provides deterministic event ordering independent of wall-clock time.
Enables reproducible replay of agent executions.

Phase 4 - Determinism & Replay
"""

import threading
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path


# =============================================================================
# Logical Clock (Lamport Timestamps)
# =============================================================================

class LogicalClock:
    """
    Implements Lamport logical clock for deterministic event ordering.
    
    Properties:
    - Monotonically increasing counter
    - Thread-safe increment operations
    - Synchronization with remote events
    - Independent of wall-clock time
    
    Usage:
        clock = LogicalClock()
        
        # Local event
        timestamp = clock.tick()
        
        # Received remote event with timestamp 42
        timestamp = clock.update(42)  # Sets clock to max(local, 42) + 1
    
    References:
        Lamport, L. (1978). "Time, Clocks, and the Ordering of Events in a Distributed System"
        https://lamport.azurewebsites.net/pubs/time-clocks.pdf
    """
    
    def __init__(self, initial_value: int = 0):
        """
        Initialize logical clock.
        
        Args:
            initial_value: Starting counter value (default: 0)
        """
        self._counter = initial_value
        self._lock = threading.Lock()
    
    def tick(self) -> int:
        """
        Increment clock and return new timestamp.
        
        Used for local events (not triggered by remote events).
        
        Returns:
            New logical timestamp
        """
        with self._lock:
            self._counter += 1
            return self._counter
    
    def update(self, remote_timestamp: int) -> int:
        """
        Update clock from remote event (Lamport synchronization rule).
        
        Sets clock to max(local_clock, remote_timestamp) + 1.
        Ensures happened-before relationship is preserved.
        
        Args:
            remote_timestamp: Timestamp from remote event
        
        Returns:
            New local timestamp
        """
        with self._lock:
            self._counter = max(self._counter, remote_timestamp) + 1
            return self._counter
    
    def current(self) -> int:
        """
        Get current clock value without incrementing.
        
        Returns:
            Current logical timestamp
        """
        with self._lock:
            return self._counter
    
    def set(self, value: int):
        """
        Manually set clock value (e.g., for checkpoint restoration).
        
        Args:
            value: New clock value
        """
        with self._lock:
            self._counter = value
    
    def to_dict(self) -> Dict[str, int]:
        """Serialize to dictionary."""
        return {'counter': self.current()}
    
    @staticmethod
    def from_dict(data: Dict[str, int]) -> 'LogicalClock':
        """Deserialize from dictionary."""
        return LogicalClock(initial_value=data['counter'])


# =============================================================================
# Global Logical Clock Instance
# =============================================================================

# Global clock for the agent system
_global_clock: Optional[LogicalClock] = None
_clock_lock = threading.Lock()


def get_global_clock() -> LogicalClock:
    """
    Get or create global logical clock instance.
    
    Returns:
        Global LogicalClock instance
    """
    global _global_clock
    
    with _clock_lock:
        if _global_clock is None:
            _global_clock = LogicalClock()
        return _global_clock


def reset_global_clock(initial_value: int = 0):
    """
    Reset global clock (for testing or checkpoint restoration).
    
    Args:
        initial_value: New clock starting value
    """
    global _global_clock
    
    with _clock_lock:
        _global_clock = LogicalClock(initial_value)


def tick() -> int:
    """Convenience function to tick global clock."""
    return get_global_clock().tick()


def update(remote_timestamp: int) -> int:
    """Convenience function to update global clock from remote event."""
    return get_global_clock().update(remote_timestamp)


def current_logical_time() -> int:
    """Convenience function to get current logical time."""
    return get_global_clock().current()


# =============================================================================
# Logical Event
# =============================================================================

@dataclass
class LogicalEvent:
    """
    Event with both logical and wall-clock timestamps.
    
    Ordering determined by logical_time (not wall_time).
    Wall time is for human reference only.
    """
    
    event_type: str
    logical_time: int
    wall_time: str  # ISO 8601 format
    data: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other: 'LogicalEvent') -> bool:
        """Compare by logical time for sorting."""
        return self.logical_time < other.logical_time
    
    def __le__(self, other: 'LogicalEvent') -> bool:
        return self.logical_time <= other.logical_time
    
    def __gt__(self, other: 'LogicalEvent') -> bool:
        return self.logical_time > other.logical_time
    
    def __ge__(self, other: 'LogicalEvent') -> bool:
        return self.logical_time >= other.logical_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'event_type': self.event_type,
            'logical_time': self.logical_time,
            'wall_time': self.wall_time,
            'data': self.data
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'LogicalEvent':
        """Deserialize from dictionary."""
        return LogicalEvent(
            event_type=data['event_type'],
            logical_time=data['logical_time'],
            wall_time=data['wall_time'],
            data=data.get('data', {})
        )


# =============================================================================
# Event Logger with Logical Time
# =============================================================================

class LogicalEventLogger:
    """
    Event logger that uses logical time for ordering.
    
    Logs events to JSON Lines format with logical timestamps.
    Events can be replayed in deterministic order.
    
    Usage:
        logger = LogicalEventLogger(".agent-state/events.jsonl")
        
        logger.log("phase.started", {"phase": "implementation"})
        logger.log("task.completed", {"task_id": "task-1"})
        
        # Read events in order
        events = logger.read_events()
        for event in sorted(events):  # Sorted by logical_time
            print(event)
    """
    
    def __init__(
        self,
        log_path: str = ".agent-state/events.jsonl",
        clock: Optional[LogicalClock] = None
    ):
        """
        Initialize event logger.
        
        Args:
            log_path: Path to JSON Lines log file
            clock: LogicalClock instance (uses global if None)
        """
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.clock = clock or get_global_clock()
    
    def log(self, event_type: str, data: Optional[Dict[str, Any]] = None):
        """
        Log event with logical timestamp.
        
        Args:
            event_type: Type of event (e.g., "phase.started", "task.completed")
            data: Event data (optional)
        """
        data = data or {}
        
        # Create event with logical time
        event = LogicalEvent(
            event_type=event_type,
            logical_time=self.clock.tick(),
            wall_time=datetime.now(timezone.utc).isoformat(),
            data=data
        )
        
        # Append to log file (JSON Lines format)
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event.to_dict()) + '\n')
    
    def log_with_timestamp(
        self,
        event_type: str,
        logical_time: int,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Log event with explicit logical timestamp (for replay).
        
        Args:
            event_type: Type of event
            logical_time: Explicit logical timestamp
            data: Event data
        """
        data = data or {}
        
        event = LogicalEvent(
            event_type=event_type,
            logical_time=logical_time,
            wall_time=datetime.now(timezone.utc).isoformat(),
            data=data
        )
        
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event.to_dict()) + '\n')
    
    def read_events(self) -> List[LogicalEvent]:
        """
        Read all events from log file.
        
        Returns:
            List of LogicalEvent objects
        """
        if not self.log_path.exists():
            return []
        
        events = []
        with open(self.log_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    event = LogicalEvent.from_dict(data)
                    events.append(event)
                except Exception as e:
                    print(f"⚠️  Failed to parse event: {e}")
        
        return events
    
    def read_events_sorted(self) -> List[LogicalEvent]:
        """
        Read all events sorted by logical time.
        
        Returns:
            Sorted list of LogicalEvent objects
        """
        events = self.read_events()
        return sorted(events)
    
    def clear(self):
        """Clear event log (for testing)."""
        if self.log_path.exists():
            self.log_path.unlink()


# =============================================================================
# Vector Clock (for distributed systems - future)
# =============================================================================

@dataclass
class VectorClock:
    """
    Vector clock for distributed event ordering.
    
    Not yet implemented - placeholder for Phase 5 (event-driven architecture).
    Vector clocks provide partial ordering and detect concurrent events.
    
    Future usage:
        clock = VectorClock(agent_id="agent-1", peers=["agent-2", "agent-3"])
        timestamp = clock.tick()
        clock.update(remote_timestamp)
    """
    
    agent_id: str
    clocks: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize own clock to 0."""
        if self.agent_id not in self.clocks:
            self.clocks[self.agent_id] = 0
    
    def tick(self) -> Dict[str, int]:
        """Increment own clock."""
        self.clocks[self.agent_id] += 1
        return self.clocks.copy()
    
    def update(self, remote_clocks: Dict[str, int]) -> Dict[str, int]:
        """Update from remote vector clock."""
        for agent, timestamp in remote_clocks.items():
            self.clocks[agent] = max(
                self.clocks.get(agent, 0),
                timestamp
            )
        
        # Increment own clock
        self.clocks[self.agent_id] += 1
        return self.clocks.copy()
    
    def happens_before(self, other: 'VectorClock') -> bool:
        """Check if this event happened before other."""
        # this ≤ other for all agents, and this < other for at least one
        all_le = all(
            self.clocks.get(agent, 0) <= other.clocks.get(agent, 0)
            for agent in set(self.clocks.keys()) | set(other.clocks.keys())
        )
        
        some_lt = any(
            self.clocks.get(agent, 0) < other.clocks.get(agent, 0)
            for agent in set(self.clocks.keys()) | set(other.clocks.keys())
        )
        
        return all_le and some_lt
    
    def concurrent_with(self, other: 'VectorClock') -> bool:
        """Check if events are concurrent (neither happened before)."""
        return not self.happens_before(other) and not other.happens_before(self)


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    print("=== Logical Time Demo ===\n")
    
    # Initialize clock
    clock = get_global_clock()
    print(f"Initial clock: {clock.current()}")
    
    # Log some events
    logger = LogicalEventLogger(".agent-state/demo-events.jsonl")
    logger.clear()  # Clear previous logs
    
    print("\n--- Logging events ---\n")
    
    logger.log("sprint.started", {"sprint_id": "042"})
    print(f"Event 1 logged at logical time: {clock.current()}")
    
    logger.log("phase.started", {"phase": "planning"})
    print(f"Event 2 logged at logical time: {clock.current()}")
    
    # Simulate receiving remote event with timestamp 100
    print(f"\n--- Received remote event with timestamp 100 ---\n")
    new_time = clock.update(100)
    print(f"Clock updated to: {new_time}")
    
    logger.log("task.completed", {"task_id": "task-1"})
    print(f"Event 3 logged at logical time: {clock.current()}")
    
    # Read events in order
    print("\n--- Reading events (sorted by logical time) ---\n")
    
    events = logger.read_events_sorted()
    for event in events:
        print(f"[{event.logical_time:3d}] {event.event_type}")
        print(f"      Data: {event.data}")
        print(f"      Wall time: {event.wall_time}")
    
    print(f"\n✓ Total events: {len(events)}")
    print(f"✓ Final clock value: {clock.current()}")
    
    # Cleanup
    logger.clear()
