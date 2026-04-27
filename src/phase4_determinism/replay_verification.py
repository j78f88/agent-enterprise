"""
Replay Verification System

Captures execution traces and verifies deterministic replay.
Integrates logical time, prompt versioning, and composition snapshots.

Phase 4 - Determinism & Replay
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum

# Import Phase 4 modules
from .logical_time import LogicalClock, LogicalEvent, current_logical_time, tick
from .prompt_versioning import PromptVersioner, PromptVersion
from .deterministic_composition import CompositionSnapshot, CompositionResult
from .llm_config import LLMConfig, LLMConfigValidator


# =============================================================================
# Execution Trace
# =============================================================================

class TraceEventType(Enum):
    """Types of trace events."""
    TASK_START = "task_start"
    TASK_COMPLETE = "task_complete"
    LLM_CALL = "llm_call"
    LLM_RESPONSE = "llm_response"
    COMPOSITION = "composition"
    CHECKPOINT = "checkpoint"
    SKILL_LOAD = "skill_load"
    FILE_WRITE = "file_write"


@dataclass
class TraceEvent:
    """
    Single event in execution trace.
    
    Captures all information needed for deterministic replay.
    """
    
    event_type: TraceEventType
    logical_time: int
    wall_time: str
    
    # Event-specific data
    task_id: Optional[str] = None
    skill_name: Optional[str] = None
    prompt_hash: Optional[str] = None
    llm_config: Optional[Dict[str, Any]] = None
    result_hash: Optional[str] = None
    
    # Additional context
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        return data
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TraceEvent':
        """Deserialize from dictionary."""
        data = data.copy()
        data['event_type'] = TraceEventType(data['event_type'])
        return TraceEvent(**data)


@dataclass
class ExecutionTrace:
    """
    Complete trace of agent execution.
    
    Contains all events in logical time order.
    """
    
    trace_id: str
    started_at: str
    events: List[TraceEvent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_event(self, event: TraceEvent):
        """Add event to trace."""
        self.events.append(event)
    
    def get_events_by_type(self, event_type: TraceEventType) -> List[TraceEvent]:
        """Get all events of specific type."""
        return [e for e in self.events if e.event_type == event_type]
    
    def get_event_sequence(self) -> List[int]:
        """Get logical time sequence."""
        return [e.logical_time for e in self.events]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'trace_id': self.trace_id,
            'started_at': self.started_at,
            'events': [e.to_dict() for e in self.events],
            'metadata': self.metadata
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ExecutionTrace':
        """Deserialize from dictionary."""
        events = [TraceEvent.from_dict(e) for e in data['events']]
        return ExecutionTrace(
            trace_id=data['trace_id'],
            started_at=data['started_at'],
            events=events,
            metadata=data.get('metadata', {})
        )


# =============================================================================
# Trace Recorder
# =============================================================================

class TraceRecorder:
    """
    Records execution trace for replay verification.
    
    Usage:
        recorder = TraceRecorder(trace_id="run-1")
        
        # Record task start
        recorder.record_task_start(task_id="TASK-001", skill="planner")
        
        # Record LLM call
        recorder.record_llm_call(
            task_id="TASK-001",
            prompt_hash="abc123",
            config=config
        )
        
        # Save trace
        recorder.save()
    """
    
    def __init__(
        self,
        trace_id: str,
        state_dir: str = ".agent-state/traces"
    ):
        """
        Initialize trace recorder.
        
        Args:
            trace_id: Unique trace identifier
            state_dir: Directory for trace storage
        """
        self.trace_id = trace_id
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.trace = ExecutionTrace(
            trace_id=trace_id,
            started_at=datetime.now(timezone.utc).isoformat()
        )
    
    def record_task_start(
        self,
        task_id: str,
        skill_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record task start event."""
        event = TraceEvent(
            event_type=TraceEventType.TASK_START,
            logical_time=tick(),
            wall_time=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            skill_name=skill_name,
            metadata=metadata or {}
        )
        self.trace.add_event(event)
    
    def record_task_complete(
        self,
        task_id: str,
        result_hash: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record task completion event."""
        event = TraceEvent(
            event_type=TraceEventType.TASK_COMPLETE,
            logical_time=tick(),
            wall_time=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            result_hash=result_hash,
            metadata=metadata or {}
        )
        self.trace.add_event(event)
    
    def record_llm_call(
        self,
        task_id: str,
        prompt_hash: str,
        config: LLMConfig,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record LLM call event."""
        event = TraceEvent(
            event_type=TraceEventType.LLM_CALL,
            logical_time=tick(),
            wall_time=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            prompt_hash=prompt_hash,
            llm_config=config.to_dict(),
            metadata=metadata or {}
        )
        self.trace.add_event(event)
    
    def record_llm_response(
        self,
        task_id: str,
        result_hash: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record LLM response event."""
        event = TraceEvent(
            event_type=TraceEventType.LLM_RESPONSE,
            logical_time=tick(),
            wall_time=datetime.now(timezone.utc).isoformat(),
            task_id=task_id,
            result_hash=result_hash,
            metadata=metadata or {}
        )
        self.trace.add_event(event)
    
    def record_composition(
        self,
        snapshot_id: str,
        result_hash: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record composition event."""
        event = TraceEvent(
            event_type=TraceEventType.COMPOSITION,
            logical_time=tick(),
            wall_time=datetime.now(timezone.utc).isoformat(),
            result_hash=result_hash,
            metadata={'snapshot_id': snapshot_id, **(metadata or {})}
        )
        self.trace.add_event(event)
    
    def record_skill_load(
        self,
        skill_name: str,
        skill_hash: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record skill load event."""
        event = TraceEvent(
            event_type=TraceEventType.SKILL_LOAD,
            logical_time=tick(),
            wall_time=datetime.now(timezone.utc).isoformat(),
            skill_name=skill_name,
            result_hash=skill_hash,
            metadata=metadata or {}
        )
        self.trace.add_event(event)
    
    def save(self):
        """Save trace to disk."""
        trace_file = self.state_dir / f"{self.trace_id}.json"
        
        with open(trace_file, 'w', encoding='utf-8') as f:
            json.dump(self.trace.to_dict(), f, indent=2)
    
    def get_trace(self) -> ExecutionTrace:
        """Get current trace."""
        return self.trace


# =============================================================================
# Replay Verifier
# =============================================================================

class ReplayVerifier:
    """
    Verifies deterministic replay by comparing execution traces.
    
    Usage:
        verifier = ReplayVerifier()
        
        # Original execution
        trace1 = run_with_recording("run-1")
        
        # Replay
        trace2 = run_with_recording("run-2")
        
        # Verify
        result = verifier.verify(trace1, trace2)
        if result['deterministic']:
            print("✓ Replay successful!")
        else:
            print(f"❌ Divergence at event {result['divergence_index']}")
    """
    
    def __init__(self, state_dir: str = ".agent-state/traces"):
        """
        Initialize replay verifier.
        
        Args:
            state_dir: Directory for trace storage
        """
        self.state_dir = Path(state_dir)
    
    def verify(
        self,
        trace1: ExecutionTrace,
        trace2: ExecutionTrace
    ) -> Dict[str, Any]:
        """
        Verify two traces are deterministically equivalent.
        
        Compares:
        - Event sequence (logical time order)
        - Event types
        - Prompt hashes
        - LLM configurations
        - Result hashes
        
        Args:
            trace1: Original execution trace
            trace2: Replay execution trace
        
        Returns:
            Verification result dictionary
        """
        result = {
            'deterministic': True,
            'trace1_id': trace1.trace_id,
            'trace2_id': trace2.trace_id,
            'divergence_index': None,
            'divergence_details': None,
            'statistics': {}
        }
        
        # Compare event counts
        if len(trace1.events) != len(trace2.events):
            result['deterministic'] = False
            result['divergence_details'] = {
                'type': 'event_count_mismatch',
                'trace1_events': len(trace1.events),
                'trace2_events': len(trace2.events)
            }
            return result
        
        # Compare events sequentially
        for i, (event1, event2) in enumerate(zip(trace1.events, trace2.events)):
            divergence = self._compare_events(event1, event2)
            
            if divergence:
                result['deterministic'] = False
                result['divergence_index'] = i
                result['divergence_details'] = divergence
                break
        
        # Compute statistics
        result['statistics'] = {
            'total_events': len(trace1.events),
            'task_starts': len(trace1.get_events_by_type(TraceEventType.TASK_START)),
            'llm_calls': len(trace1.get_events_by_type(TraceEventType.LLM_CALL)),
            'compositions': len(trace1.get_events_by_type(TraceEventType.COMPOSITION))
        }
        
        return result
    
    def verify_by_id(self, trace1_id: str, trace2_id: str) -> Dict[str, Any]:
        """
        Verify traces by ID (load from disk).
        
        Args:
            trace1_id: First trace ID
            trace2_id: Second trace ID
        
        Returns:
            Verification result dictionary
        """
        trace1 = self._load_trace(trace1_id)
        trace2 = self._load_trace(trace2_id)
        
        if not trace1 or not trace2:
            return {
                'deterministic': False,
                'error': 'Trace not found'
            }
        
        return self.verify(trace1, trace2)
    
    def _compare_events(
        self,
        event1: TraceEvent,
        event2: TraceEvent
    ) -> Optional[Dict[str, Any]]:
        """
        Compare two events for equivalence.
        
        Returns:
            Divergence details if events differ, None if equivalent
        """
        # Compare event types
        if event1.event_type != event2.event_type:
            return {
                'type': 'event_type_mismatch',
                'event1_type': event1.event_type.value,
                'event2_type': event2.event_type.value,
                'logical_time': event1.logical_time
            }
        
        # Compare logical time (should be identical)
        if event1.logical_time != event2.logical_time:
            return {
                'type': 'logical_time_mismatch',
                'event1_time': event1.logical_time,
                'event2_time': event2.logical_time
            }
        
        # Compare task IDs
        if event1.task_id != event2.task_id:
            return {
                'type': 'task_id_mismatch',
                'event1_task': event1.task_id,
                'event2_task': event2.task_id,
                'logical_time': event1.logical_time
            }
        
        # Compare prompt hashes (for LLM calls)
        if event1.prompt_hash != event2.prompt_hash:
            return {
                'type': 'prompt_hash_mismatch',
                'event1_hash': event1.prompt_hash,
                'event2_hash': event2.prompt_hash,
                'logical_time': event1.logical_time
            }
        
        # Compare LLM configs
        if event1.llm_config != event2.llm_config:
            return {
                'type': 'llm_config_mismatch',
                'event1_config': event1.llm_config,
                'event2_config': event2.llm_config,
                'logical_time': event1.logical_time
            }
        
        # Compare result hashes
        if event1.result_hash != event2.result_hash:
            return {
                'type': 'result_hash_mismatch',
                'event1_hash': event1.result_hash,
                'event2_hash': event2.result_hash,
                'logical_time': event1.logical_time
            }
        
        return None
    
    def _load_trace(self, trace_id: str) -> Optional[ExecutionTrace]:
        """Load trace from disk."""
        trace_file = self.state_dir / f"{trace_id}.json"
        
        if not trace_file.exists():
            return None
        
        try:
            with open(trace_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ExecutionTrace.from_dict(data)
        except Exception as e:
            print(f"⚠️  Failed to load trace {trace_id}: {e}")
            return None


# =============================================================================
# Deterministic Execution Context
# =============================================================================

class DeterministicExecutionContext:
    """
    Context manager for deterministic execution.
    
    Integrates all Phase 4 components:
    - Logical time
    - Prompt versioning
    - LLM configuration enforcement
    - Trace recording
    
    Usage:
        with DeterministicExecutionContext(trace_id="run-1") as ctx:
            # All operations are traced
            ctx.record_task_start("TASK-001", "planner")
            
            # LLM calls are validated
            config = ctx.get_llm_config()
            
            # Prompts are versioned
            prompt_version = ctx.hash_prompt(prompt_text, "planner")
            
            # Complete task
            ctx.record_task_complete("TASK-001", result_hash)
    """
    
    def __init__(
        self,
        trace_id: str,
        state_dir: str = ".agent-state",
        strict_llm_validation: bool = True
    ):
        """
        Initialize deterministic execution context.
        
        Args:
            trace_id: Unique trace identifier
            state_dir: State directory
            strict_llm_validation: If True, raise on non-deterministic LLM params
        """
        self.trace_id = trace_id
        self.state_dir = Path(state_dir)
        
        # Initialize components
        self.recorder = TraceRecorder(trace_id, state_dir=f"{state_dir}/traces")
        self.versioner = PromptVersioner(state_dir=state_dir)
        self.llm_validator = LLMConfigValidator(strict=strict_llm_validation)
        
        # Logical clock
        self.clock = LogicalClock()
    
    def __enter__(self):
        """Enter context."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and save trace."""
        self.recorder.save()
    
    def record_task_start(self, task_id: str, skill_name: str):
        """Record task start."""
        self.recorder.record_task_start(task_id, skill_name)
    
    def record_task_complete(self, task_id: str, result_hash: str):
        """Record task completion."""
        self.recorder.record_task_complete(task_id, result_hash)
    
    def hash_prompt(self, prompt: str, skill_name: str) -> PromptVersion:
        """Hash prompt and record version."""
        version = self.versioner.hash_prompt(prompt, skill_name)
        self.recorder.record_skill_load(skill_name, version.prompt_hash)
        return version
    
    def validate_llm_config(self, config: LLMConfig):
        """Validate LLM configuration."""
        self.llm_validator.validate_config(config)
    
    def record_llm_call(
        self,
        task_id: str,
        prompt_hash: str,
        config: LLMConfig
    ):
        """Record LLM call."""
        self.validate_llm_config(config)
        self.recorder.record_llm_call(task_id, prompt_hash, config)
    
    def record_llm_response(self, task_id: str, result_hash: str):
        """Record LLM response."""
        self.recorder.record_llm_response(task_id, result_hash)
    
    def get_trace(self) -> ExecutionTrace:
        """Get current trace."""
        return self.recorder.get_trace()


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    print("=== Replay Verification Demo ===\n")
    
    # Simulate original execution
    print("--- Original execution ---\n")
    
    with DeterministicExecutionContext(trace_id="run-1") as ctx:
        # Start task
        ctx.record_task_start("TASK-001", "planner")
        
        # Hash prompt
        prompt = "Create a sprint plan with max 5 items"
        prompt_version = ctx.hash_prompt(prompt, "planner")
        print(f"Prompt hash: {prompt_version.prompt_hash}")
        
        # Simulate LLM call
        from .llm_config import LLMConfigPresets
        config = LLMConfigPresets.gpt4_deterministic()
        ctx.record_llm_call("TASK-001", prompt_version.prompt_hash, config)
        
        # Simulate response
        result_hash = "result123"
        ctx.record_llm_response("TASK-001", result_hash)
        
        # Complete task
        ctx.record_task_complete("TASK-001", result_hash)
    
    print(f"✓ Recorded {len(ctx.get_trace().events)} events\n")
    
    # Simulate replay
    print("--- Replay execution ---\n")
    
    with DeterministicExecutionContext(trace_id="run-2") as ctx2:
        # Same operations
        ctx2.record_task_start("TASK-001", "planner")
        
        prompt_version2 = ctx2.hash_prompt(prompt, "planner")
        print(f"Prompt hash: {prompt_version2.prompt_hash}")
        
        ctx2.record_llm_call("TASK-001", prompt_version2.prompt_hash, config)
        ctx2.record_llm_response("TASK-001", result_hash)
        ctx2.record_task_complete("TASK-001", result_hash)
    
    print(f"✓ Recorded {len(ctx2.get_trace().events)} events\n")
    
    # Verify determinism
    print("--- Verifying determinism ---\n")
    
    verifier = ReplayVerifier()
    result = verifier.verify_by_id("run-1", "run-2")
    
    if result['deterministic']:
        print("✓ Replay verification successful!")
        print(f"  Total events: {result['statistics']['total_events']}")
        print(f"  LLM calls: {result['statistics']['llm_calls']}")
    else:
        print("❌ Replay verification failed!")
        print(f"  Divergence at event {result['divergence_index']}")
        print(f"  Details: {result['divergence_details']}")
    
    print("\n✓ Demo complete")
