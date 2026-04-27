"""
Phase 4 Integration Tests

Tests for Determinism & Replay components:
- Logical time (Lamport timestamps)
- Prompt versioning
- Deterministic composition
- LLM configuration enforcement
- Replay verification

Run with: python tests/test_phase4.py
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime, timezone
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import Phase 4 modules
from phase4_determinism.logical_time import (
    LogicalClock, LogicalEvent, LogicalEventLogger,
    get_global_clock, reset_global_clock, tick, update, current_logical_time
)
from phase4_determinism.prompt_versioning import PromptVersioner, SkillTemplateHasher
from phase4_determinism.deterministic_composition import (
    content_hash, sort_items_deterministic, sort_bugs_deterministic,
    CompositionSnapshotter, CompositionResult, ReplayVerifier as CompReplayVerifier
)
from phase4_determinism.llm_config import (
    LLMConfig, LLMConfigValidator, DeterminismViolation,
    LLMConfigPresets, LLMConfigManager
)
from phase4_determinism.replay_verification import (
    TraceRecorder, TraceEventType, ReplayVerifier,
    DeterministicExecutionContext
)


class TestLogicalTime(unittest.TestCase):
    """Tests for logical time (Lamport timestamps)."""
    
    def setUp(self):
        """Reset global clock before each test."""
        reset_global_clock()
    
    def test_logical_clock_monotonic(self):
        """Test logical clock is monotonically increasing."""
        clock = LogicalClock()
        
        t1 = clock.tick()
        t2 = clock.tick()
        t3 = clock.tick()
        
        self.assertEqual(t1, 1)
        self.assertEqual(t2, 2)
        self.assertEqual(t3, 3)
    
    def test_logical_clock_update(self):
        """Test Lamport synchronization rule."""
        clock = LogicalClock()
        
        # Local time: 5
        for _ in range(5):
            clock.tick()
        
        # Receive event with timestamp 10
        new_time = clock.update(10)
        
        # Should be max(5, 10) + 1 = 11
        self.assertEqual(new_time, 11)
    
    def test_global_clock(self):
        """Test global clock singleton."""
        t1 = tick()
        t2 = tick()
        
        self.assertEqual(t1, 1)
        self.assertEqual(t2, 2)
        
        # Update from remote
        t3 = update(10)
        self.assertEqual(t3, 11)
    
    def test_logical_event_ordering(self):
        """Test events ordered by logical time, not wall time."""
        event1 = LogicalEvent("task1", 5, datetime.now(timezone.utc).isoformat())
        event2 = LogicalEvent("task2", 3, datetime.now(timezone.utc).isoformat())
        event3 = LogicalEvent("task3", 7, datetime.now(timezone.utc).isoformat())
        
        events = sorted([event1, event2, event3])
        
        self.assertEqual(events[0].logical_time, 3)
        self.assertEqual(events[1].logical_time, 5)
        self.assertEqual(events[2].logical_time, 7)
    
    def test_logical_event_logger(self):
        """Test event logging with logical timestamps."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "events.jsonl"
            logger = LogicalEventLogger(str(log_file))
            
            # Log events out of order (by wall time)
            logger.log_with_timestamp("task1", 5, {'status': 'complete'})
            logger.log_with_timestamp("task2", 3, {'status': 'start'})
            logger.log_with_timestamp("task3", 7, {'status': 'end'})
            
            # Read sorted by logical time
            events = logger.read_events_sorted()
            
            self.assertEqual(len(events), 3)
            self.assertEqual(events[0].logical_time, 3)
            self.assertEqual(events[1].logical_time, 5)
            self.assertEqual(events[2].logical_time, 7)


class TestPromptVersioning(unittest.TestCase):
    """Tests for prompt versioning."""
    
    def setUp(self):
        """Create temporary state directory."""
        self.tmpdir = tempfile.mkdtemp()
        self.versioner = PromptVersioner(state_dir=self.tmpdir)
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.tmpdir)
    
    def test_hash_prompt(self):
        """Test prompt hashing."""
        prompt = "You are a sprint planner."
        version = self.versioner.hash_prompt(prompt, "planner")
        
        self.assertEqual(len(version.prompt_hash), 12)
        self.assertEqual(len(version.full_hash), 64)
        self.assertEqual(version.skill_name, "planner")
    
    def test_identical_prompts_same_hash(self):
        """Test identical prompts produce same hash."""
        prompt = "You are a sprint planner."
        
        v1 = self.versioner.hash_prompt(prompt, "planner")
        v2 = self.versioner.hash_prompt(prompt, "planner")
        
        self.assertEqual(v1.full_hash, v2.full_hash)
    
    def test_different_prompts_different_hash(self):
        """Test different prompts produce different hashes."""
        prompt1 = "You are a sprint planner."
        prompt2 = "You are a reviewer."
        
        v1 = self.versioner.hash_prompt(prompt1, "planner")
        v2 = self.versioner.hash_prompt(prompt2, "reviewer")
        
        self.assertNotEqual(v1.full_hash, v2.full_hash)
    
    def test_has_changed(self):
        """Test change detection."""
        prompt1 = "You are a sprint planner."
        
        # First hash
        self.versioner.hash_prompt(prompt1, "planner")
        
        # Same prompt - no change
        self.assertFalse(self.versioner.has_changed("planner", prompt1))
        
        # Different prompt - changed
        prompt2 = "You are a different planner."
        self.assertTrue(self.versioner.has_changed("planner", prompt2))
    
    def test_version_history(self):
        """Test version history tracking."""
        prompt1 = "Version 1"
        prompt2 = "Version 2"
        
        self.versioner.hash_prompt(prompt1, "planner")
        self.versioner.hash_prompt(prompt2, "planner")
        
        history = self.versioner.get_history("planner")
        self.assertEqual(len(history), 2)


class TestDeterministicComposition(unittest.TestCase):
    """Tests for deterministic composition."""
    
    def test_content_hash_deterministic(self):
        """Test content hashing is deterministic."""
        item = {'type': 'feature', 'score': 10, 'notes': 'Feature A'}
        
        hash1 = content_hash(item)
        hash2 = content_hash(item)
        
        self.assertEqual(hash1, hash2)
    
    def test_sort_items_deterministic(self):
        """Test deterministic sorting with tie-breaking."""
        items = [
            {'item_id': 'A', 'score': 10, 'notes': 'First'},
            {'item_id': 'B', 'score': 10, 'notes': 'Second'},  # Same score
            {'item_id': 'C', 'score': 8, 'notes': 'Third'}
        ]
        
        # Sort multiple times
        sorted1 = sort_items_deterministic(items)
        sorted2 = sort_items_deterministic(items)
        
        # Results should be identical
        self.assertEqual(
            [item['item_id'] for item in sorted1],
            [item['item_id'] for item in sorted2]
        )
    
    def test_sort_bugs_deterministic(self):
        """Test deterministic bug sorting."""
        bugs = [
            {'bug_id': 'B1', 'severity': 'MEDIUM', 'title': 'Bug 1'},
            {'bug_id': 'B2', 'severity': 'CRITICAL', 'title': 'Bug 2'},
            {'bug_id': 'B3', 'severity': 'MEDIUM', 'title': 'Bug 3'},  # Same severity
            {'bug_id': 'B4', 'severity': 'HIGH', 'title': 'Bug 4'}
        ]
        
        sorted1 = sort_bugs_deterministic(bugs)
        sorted2 = sort_bugs_deterministic(bugs)
        
        # Verify order
        self.assertEqual(sorted1[0]['severity'], 'CRITICAL')
        
        # Verify determinism
        self.assertEqual(
            [bug['bug_id'] for bug in sorted1],
            [bug['bug_id'] for bug in sorted2]
        )
    
    def test_composition_snapshot(self):
        """Test composition snapshot creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshotter = CompositionSnapshotter(state_dir=tmpdir)
            
            snapshot = snapshotter.create_snapshot(
                ledger_items=[{'item_id': 'ITEM-001'}],
                bugs=[{'bug_id': 'BUG-001'}],
                constraints={'max_items': 5},
                config={'project': 'test'},
                logical_time=100
            )
            
            self.assertIsNotNone(snapshot.snapshot_id)
            self.assertEqual(snapshot.logical_time, 100)
            
            # Load snapshot
            loaded = snapshotter.load_snapshot(snapshot.snapshot_id)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.snapshot_id, snapshot.snapshot_id)
    
    def test_composition_result_hash(self):
        """Test composition result hashing."""
        result = CompositionResult(
            selected_items=['ITEM-001', 'ITEM-002'],
            total_complexity=15,
            snapshot_id='snap123',
            composition_hash='',
            logical_time=101,
            metadata={}
        )
        
        hash1 = result.compute_hash()
        hash2 = result.compute_hash()
        
        self.assertEqual(hash1, hash2)


class TestLLMConfiguration(unittest.TestCase):
    """Tests for LLM configuration enforcement."""
    
    def test_deterministic_config_valid(self):
        """Test deterministic config is accepted."""
        config = LLMConfig(
            model="gpt-4",
            temperature=0.0
        )
        
        self.assertEqual(config.temperature, 0.0)
    
    def test_non_deterministic_config_rejected(self):
        """Test non-deterministic config is rejected."""
        with self.assertRaises(DeterminismViolation):
            LLMConfig(
                model="gpt-4",
                temperature=0.7  # Non-zero!
            )
    
    def test_config_validator_strict(self):
        """Test strict validator rejects non-deterministic params."""
        validator = LLMConfigValidator(strict=True)
        
        # Valid params
        validator.validate_params({'temperature': 0.0})
        
        # Invalid params
        with self.assertRaises(DeterminismViolation):
            validator.validate_params({'temperature': 0.8})
    
    def test_config_validator_non_strict(self):
        """Test non-strict validator logs violations."""
        validator = LLMConfigValidator(strict=False, log_violations=False)
        
        # Should not raise, but return False
        is_valid = validator.validate_params({'temperature': 0.8})
        self.assertFalse(is_valid)
        
        # Should record violation
        self.assertEqual(len(validator.get_violations()), 1)
    
    def test_config_presets(self):
        """Test config presets are deterministic."""
        configs = [
            LLMConfigPresets.gpt4_deterministic(),
            LLMConfigPresets.gpt4o_deterministic(),
            LLMConfigPresets.claude_deterministic()
        ]
        
        for config in configs:
            self.assertEqual(config.temperature, 0.0)
    
    def test_config_manager(self):
        """Test configuration manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "llm-config.json"
            manager = LLMConfigManager(config_path=str(config_path))
            
            # Set config
            config = LLMConfigPresets.gpt4_deterministic()
            manager.set_config("planner", config)
            
            # Get config
            retrieved = manager.get_config("planner")
            self.assertEqual(retrieved.temperature, 0.0)
            
            # Config file should exist
            self.assertTrue(config_path.exists())


class TestReplayVerification(unittest.TestCase):
    """Tests for replay verification."""
    
    def setUp(self):
        """Create temporary state directory."""
        self.tmpdir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.tmpdir)
        reset_global_clock()
    
    def test_trace_recording(self):
        """Test execution trace recording."""
        recorder = TraceRecorder("test-trace", state_dir=self.tmpdir)
        
        recorder.record_task_start("TASK-001", "planner")
        recorder.record_task_complete("TASK-001", "result123")
        
        trace = recorder.get_trace()
        self.assertEqual(len(trace.events), 2)
        self.assertEqual(trace.events[0].event_type, TraceEventType.TASK_START)
    
    def test_deterministic_execution_context(self):
        """Test deterministic execution context."""
        with DeterministicExecutionContext("test-run", state_dir=self.tmpdir) as ctx:
            ctx.record_task_start("TASK-001", "planner")
            
            prompt_version = ctx.hash_prompt("Test prompt", "planner")
            self.assertIsNotNone(prompt_version.prompt_hash)
            
            config = LLMConfigPresets.gpt4_deterministic()
            ctx.record_llm_call("TASK-001", prompt_version.prompt_hash, config)
            
            ctx.record_task_complete("TASK-001", "result123")
        
        trace = ctx.get_trace()
        self.assertGreater(len(trace.events), 0)
    
    def test_replay_verification_success(self):
        """Test successful replay verification."""
        # Original execution
        with DeterministicExecutionContext("run-1", state_dir=self.tmpdir) as ctx1:
            ctx1.record_task_start("TASK-001", "planner")
            ctx1.record_task_complete("TASK-001", "result123")
        
        reset_global_clock()
        
        # Replay (identical)
        with DeterministicExecutionContext("run-2", state_dir=self.tmpdir) as ctx2:
            ctx2.record_task_start("TASK-001", "planner")
            ctx2.record_task_complete("TASK-001", "result123")
        
        # Verify
        verifier = ReplayVerifier(state_dir=f"{self.tmpdir}/traces")
        result = verifier.verify_by_id("run-1", "run-2")
        
        self.assertTrue(result['deterministic'])
    
    def test_replay_verification_failure(self):
        """Test replay verification detects divergence."""
        # Original execution
        with DeterministicExecutionContext("run-3", state_dir=self.tmpdir) as ctx1:
            ctx1.record_task_start("TASK-001", "planner")
            ctx1.record_task_complete("TASK-001", "result123")
        
        reset_global_clock()
        
        # Replay (different result)
        with DeterministicExecutionContext("run-4", state_dir=self.tmpdir) as ctx2:
            ctx2.record_task_start("TASK-001", "planner")
            ctx2.record_task_complete("TASK-001", "result456")  # Different!
        
        # Verify
        verifier = ReplayVerifier(state_dir=f"{self.tmpdir}/traces")
        result = verifier.verify_by_id("run-3", "run-4")
        
        self.assertFalse(result['deterministic'])
        self.assertIsNotNone(result['divergence_index'])


class TestEndToEndDeterminism(unittest.TestCase):
    """End-to-end determinism tests."""
    
    def setUp(self):
        """Setup for end-to-end tests."""
        self.tmpdir = tempfile.mkdtemp()
        reset_global_clock()
    
    def tearDown(self):
        """Cleanup."""
        shutil.rmtree(self.tmpdir)
    
    def test_complete_workflow(self):
        """Test complete deterministic workflow."""
        # Simulate planning workflow
        def run_planning_workflow(run_id: str) -> str:
            with DeterministicExecutionContext(run_id, state_dir=self.tmpdir) as ctx:
                # Start planning task
                ctx.record_task_start("PLAN-001", "planner")
                
                # Hash prompt
                prompt = "Create a sprint plan with max 5 items and complexity <= 13"
                prompt_version = ctx.hash_prompt(prompt, "planner")
                
                # LLM call with deterministic config
                config = LLMConfigPresets.gpt4_deterministic()
                ctx.record_llm_call("PLAN-001", prompt_version.prompt_hash, config)
                
                # Simulate deterministic composition
                items = [
                    {'item_id': 'ITEM-001', 'score': 10, 'notes': 'Feature A'},
                    {'item_id': 'ITEM-002', 'score': 8, 'notes': 'Feature B'}
                ]
                sorted_items = sort_items_deterministic(items)
                
                # Create result hash
                result = CompositionResult(
                    selected_items=[item['item_id'] for item in sorted_items],
                    total_complexity=18,
                    snapshot_id='snap-001',
                    composition_hash='',
                    logical_time=current_logical_time(),
                    metadata={}
                )
                result_hash = result.compute_hash()
                
                # Record result
                ctx.record_llm_response("PLAN-001", result_hash)
                ctx.record_task_complete("PLAN-001", result_hash)
                
                return result_hash
        
        # Run workflow twice
        result1 = run_planning_workflow("workflow-1")
        
        reset_global_clock()  # Reset for second run
        
        result2 = run_planning_workflow("workflow-2")
        
        # Results should be identical
        self.assertEqual(result1, result2)
        
        # Verify traces
        verifier = ReplayVerifier(state_dir=f"{self.tmpdir}/traces")
        verification = verifier.verify_by_id("workflow-1", "workflow-2")
        
        self.assertTrue(verification['deterministic'])


def run_tests():
    """Run all Phase 4 tests."""
    print("=" * 70)
    print("Phase 4: Determinism & Replay - Integration Tests")
    print("=" * 70)
    print()
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogicalTime))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPromptVersioning))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDeterministicComposition))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLLMConfiguration))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestReplayVerification))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEndToEndDeterminism))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
