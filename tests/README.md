# Testing Guide

How to run tests, understand results, and maintain test quality for agent-homebase.

---

## Test Structure

| File | Phase | Tests | Focus |
|------|-------|-------|-------|
| `test_contracts.py` | Phase 1 | 27 | JSON Schema validation, Rego policies, FSM transitions |
| `test_phase2.py` | Phase 2 | 15+ | SQLite persistence, checkpoints, migrations, workflows |
| `test_phase3.py` | Phase 3 | 15+ | Sandbox isolation, capabilities, security layers |
| `test_phase4.py` | Phase 4 | 27 | Determinism, Lamport timestamps, replay verification |

---

## Quick Start

### Run all tests

```bash
cd /path/to/agent-homebase
pytest tests/ -v
```

### Run specific phase

```bash
pytest tests/test_contracts.py -v      # Phase 1
pytest tests/test_phase2.py -v         # Phase 2
pytest tests/test_phase3.py -v         # Phase 3
pytest tests/test_phase4.py -v         # Phase 4
```

### Run with coverage

```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

---

## Prerequisites

```bash
pip install pytest pytest-cov
```

For Phase 3 sandbox tests (optional):
```bash
pip install docker
# Docker Desktop must be running
```

---

## Test Categories

### Phase 1: Contract Validation (`test_contracts.py`)

Tests for formal verification of agent contracts:

- **Tier 1 validation** — Analysis-only returns (no artifacts)
- **Tier 2 validation** — Returns with single artifact
- **Tier 3 validation** — Composition returns with metadata
- **Write permit enforcement** — Correct paths per artifact type
- **Rego policy evaluation** — Priority ordering, capacity, feature/bug balance
- **FSM transitions** — Valid/invalid state changes

```python
# Example: Test Tier 1 valid return
def test_tier1_valid(validator):
    data = {
        "tier": 1,
        "agent": "planner",
        "status": "complete",
        "summary": "Analysis complete.",
        "findings": []
    }
    result = validator.validate(json.dumps(data), expected_tier=1)
    assert result.valid
```

### Phase 2: Durability (`test_phase2.py`)

Tests for data persistence and recovery:

- **SQLite operations** — CRUD for ledger, bugs, sprints, checkpoints
- **Checkpoint creation** — State serialization, compression, hashing
- **Checkpoint restore** — Resume from snapshot, verify integrity
- **Migration utilities** — Markdown ↔ SQLite conversion
- **Dual-write mode** — Parallel writes to both formats
- **Workflow engine** — Task orchestration, retries, compensation

### Phase 3: Isolation (`test_phase3.py`)

Tests for sandboxed execution:

- **Container lifecycle** — Create, run, stop, destroy
- **Capability enforcement** — File, network, exec permissions
- **Resource limits** — Memory, CPU, disk, timeout
- **Network policies** — Deny-all, allow-internal, allow-http
- **Violation tracking** — Audit trail for denied operations
- **Checkpoint integration** — Sandbox state in checkpoints

**Note:** Requires Docker. Tests skip gracefully if unavailable.

### Phase 4: Determinism (`test_phase4.py`)

Tests for reproducible execution:

- **Lamport timestamps** — Clock operations, synchronization
- **Prompt versioning** — SHA256 hashing, change detection
- **Deterministic composition** — Content-based tie-breaking
- **LLM config enforcement** — Temperature=0 validation
- **Replay verification** — Trace comparison, divergence detection

```python
# Example: Test Lamport clock synchronization
def test_lamport_sync():
    clock = LogicalClock()
    clock.tick()  # 1
    clock.tick()  # 2
    clock.update(10)  # max(2, 10) + 1 = 11
    assert clock.current() == 11
```

---

## Expected Results

### Passing run

```
============================= test session starts ==============================
collected 84 items

tests/test_contracts.py::TestSubagentReturnValidation::test_tier1_valid PASSED
tests/test_contracts.py::TestSubagentReturnValidation::test_tier1_missing_summary PASSED
...
tests/test_phase4.py::TestReplayVerification::test_trace_comparison PASSED

============================= 84 passed in 2.34s ===============================
```

### Common failures

| Failure | Cause | Solution |
|---------|-------|----------|
| `ModuleNotFoundError: yaml` | PyYAML not installed | `pip install pyyaml` |
| `ModuleNotFoundError: docker` | Docker SDK not installed | `pip install docker` (or skip Phase 3) |
| `docker.errors.DockerException` | Docker not running | Start Docker Desktop |

---

## Writing New Tests

### Test file naming

- `test_<phase>.py` for phase-specific tests
- `test_<feature>.py` for feature-specific tests

### Test function naming

```python
def test_<what>_<condition>_<expected>():
    """Test <what> when <condition> returns <expected>."""
```

### Required assertions

1. **Happy path** — Valid input produces valid output
2. **Error handling** — Invalid input produces clear error
3. **Edge cases** — Boundary conditions, empty inputs

### Example test

```python
def test_checkpoint_restore_preserves_state():
    """Test that restoring a checkpoint recovers exact state."""
    # Arrange
    manager = CheckpointManager(db, sprint_id="042")
    original_state = create_test_state()
    
    # Act
    checkpoint_id = manager.create_checkpoint("test", original_state)
    restored_state = manager.restore_checkpoint(checkpoint_id)
    
    # Assert
    assert restored_state.sprint_id == original_state.sprint_id
    assert restored_state.fsm_state == original_state.fsm_state
    assert restored_state.logical_time == original_state.logical_time
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pytest pytest-cov pyyaml
      - run: pytest tests/ -v --cov=src
```

### Pre-commit hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest tests/test_contracts.py -q || exit 1
```

---

## Coverage Requirements

| Component | Target | Current |
|-----------|--------|---------|
| `src/phase1_verification/` | 90% | ✓ |
| `src/phase2_durability/` | 85% | ✓ |
| `src/phase3_isolation/` | 80% | ✓ |
| `src/phase4_determinism/` | 90% | ✓ |
| `init.py` | 70% | ✓ |

---

## Troubleshooting Tests

### Tests hang or timeout

- Check for infinite loops in fixtures
- Reduce Docker container timeouts in Phase 3 tests
- Use `pytest --timeout=30` to enforce limits

### Flaky tests

- Avoid wall-clock time in assertions
- Use deterministic seeds for random data
- Mock external dependencies (network, filesystem)

### Import errors

```bash
# Run from project root, not tests/ directory
cd /path/to/agent-homebase
pytest tests/ -v
```

---

## Cross-References

- [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md) — General troubleshooting
- [DETERMINISM_GUIDE.md](../docs/DETERMINISM_GUIDE.md) — Writing deterministic tests
- [CONTRIBUTING.md](../docs/CONTRIBUTING.md) — Test requirements for contributions
