# Sandbox Guide

How to use the container-based isolation system for secure agent task execution.

---

## Overview

Phase 3 sandboxing provides:

- **Isolation**: Tasks run in Docker containers
- **Resource limits**: CPU, memory, disk, time constraints
- **Network policies**: Control external access
- **Capability framework**: Fine-grained permissions (read file, write dir, network access)
- **Audit trail**: All denied operations logged

**What is a capability?** A capability is a specific permission granted to a task (e.g., "read files in src/", "write to docs/", "access npmjs.com"). Tasks start with zero capabilities; you grant only what's needed.

---

## Prerequisites

```bash
# Install Docker SDK
pip install docker

# Verify Docker is running
docker info
```

---

## Quick Start

```python
from src.phase3_isolation.sandbox import SandboxManager
from src.phase3_isolation.capabilities import Capability, CapabilityPreset

# Create sandbox manager
manager = SandboxManager()

# Create sandbox with test-runner preset
sandbox = manager.create_sandbox(
    task_id="task-001",
    preset=CapabilityPreset.TEST_RUNNER
)

# Execute command
result = sandbox.execute("npm test")

print(f"Exit code: {result.exit_code}")
print(f"stdout: {result.stdout}")
print(f"Violations: {result.violations}")

# Cleanup
manager.destroy_sandbox(sandbox.sandbox_id)
```

---

## Capability Presets

Pre-configured permission sets for common tasks:

| Preset | File Access | Network | Exec | Use Case |
|--------|-------------|---------|------|----------|
| `TEST_RUNNER` | Read all, write test output | Deny | npm, pytest | Running tests |
| `BUILD_TASK` | Read all, write dist/ | Deny | npm, cargo | Building artifacts |
| `LINTER` | Read all | Deny | eslint, prettier | Code analysis |
| `DB_READER` | Read config | Internal only | psql, sqlite3 | Database queries |

### Using Presets

```python
from src.phase3_isolation.capabilities import CapabilityPreset

# Test runner: can read all files, write to test output, no network
sandbox = manager.create_sandbox(
    task_id="task-001",
    preset=CapabilityPreset.TEST_RUNNER
)

# Build task: can write to dist/, no network
sandbox = manager.create_sandbox(
    task_id="task-002", 
    preset=CapabilityPreset.BUILD_TASK
)
```

---

## Custom Capabilities

### Defining Capabilities

```python
from src.phase3_isolation.capabilities import (
    Capability, 
    FileCapability, 
    NetworkCapability,
    ExecCapability
)

capabilities = [
    # Read any file
    FileCapability(action="read", path="**/*"),
    
    # Write only to specific directory
    FileCapability(action="write", path="output/**"),
    
    # Allow HTTP to specific domains
    NetworkCapability(
        policy="allow-http",
        allowed_domains=["api.example.com", "cdn.example.com"]
    ),
    
    # Allow specific executables
    ExecCapability(allowed=["node", "npm", "npx"])
]

sandbox = manager.create_sandbox(
    task_id="task-003",
    capabilities=capabilities
)
```

### Capability Types

| Type | Properties | Example |
|------|------------|---------|
| `FileCapability` | action, path, recursive | Read src/, write dist/ |
| `NetworkCapability` | policy, allowed_domains, ports | HTTP to api.example.com |
| `ExecCapability` | allowed, denied | Allow npm, deny curl |
| `DatabaseCapability` | connection_string, read_only | Read-only SQLite |

---

## Resource Limits

```python
from src.phase3_isolation.sandbox import ResourceLimits

limits = ResourceLimits(
    max_memory_mb=2048,        # 2GB RAM
    max_cpu_cores=2.0,         # 2 CPU cores
    max_execution_seconds=900, # 15 minute timeout
    max_disk_writes_mb=500,    # 500MB disk writes
    max_network_egress_mb=100  # 100MB network output
)

sandbox = manager.create_sandbox(
    task_id="task-004",
    preset=CapabilityPreset.BUILD_TASK,
    limits=limits
)
```

### Default Limits

| Resource | Default | Rationale |
|----------|---------|-----------|
| Memory | 2048 MB | Sufficient for most builds |
| CPU | 2.0 cores | Parallel compilation |
| Time | 900 seconds | 15 min for large test suites |
| Disk | 500 MB | Build artifacts |
| Network | 100 MB | Package downloads |

---

## Network Policies

| Policy | Behavior | Use Case |
|--------|----------|----------|
| `DENY_ALL` | No network access | Pure computation |
| `ALLOW_INTERNAL` | Local services only | Database access |
| `ALLOW_HTTP` | HTTP/HTTPS to allowed domains | API calls |
| `ALLOW_GIT` | Git operations | Clone/fetch |

### Configuring Network

```python
from src.phase3_isolation.sandbox import NetworkPolicy

# Deny all network (default for security)
sandbox = manager.create_sandbox(
    task_id="task-005",
    network_policy=NetworkPolicy.DENY_ALL
)

# Allow HTTP to specific domains
sandbox = manager.create_sandbox(
    task_id="task-006",
    network_policy=NetworkPolicy.ALLOW_HTTP,
    allowed_domains=["registry.npmjs.org", "api.github.com"]
)
```

---

## Security Layers

Sandboxes enforce 5 security layers:

1. **Namespace isolation**: Separate PID, network, mount namespaces
2. **Capability dropping**: Remove dangerous Linux capabilities
3. **Non-root user**: Run as unprivileged user inside container
4. **Read-only root**: Filesystem mounted read-only by default
5. **Resource limits**: cgroups enforce CPU/memory limits

### Verification

```python
result = sandbox.execute("id")
# uid=1000(sandbox) gid=1000(sandbox) groups=1000(sandbox)

result = sandbox.execute("cat /etc/passwd")
# Permission denied (if not granted read capability)
```

---

## Violation Tracking

All denied operations are logged:

```python
result = sandbox.execute("curl https://malicious.com")

if result.violations:
    for v in result.violations:
        print(f"BLOCKED: {v['action']} - {v['target']}")
        # BLOCKED: network_egress - https://malicious.com
```

### Audit Log

Violations are written to security audit:

```json
{
  "timestamp": "2026-04-27T10:30:00Z",
  "sandbox_id": "sbx-042-a1b2c3",
  "task_id": "task-001",
  "violation": {
    "type": "network_egress",
    "target": "https://malicious.com",
    "policy": "DENY_ALL",
    "action": "blocked"
  }
}
```

---

## Integration with Checkpoints

Sandbox state is included in checkpoints:

```python
# Checkpoint includes active sandboxes
checkpoint = manager.create_checkpoint("mid-task", state)

# Restore recreates sandbox state
state = manager.restore_checkpoint(checkpoint_id)
for sandbox_state in state.active_sandboxes:
    sandbox_manager.restore_sandbox(sandbox_state)
```

---

## Extending Capability Presets

### Creating Custom Presets

```python
from src.phase3_isolation.capabilities import CapabilityPreset

# Define custom preset
MY_PRESET = CapabilityPreset(
    name="my-custom-preset",
    capabilities=[
        FileCapability(action="read", path="**/*"),
        FileCapability(action="write", path="reports/**"),
        ExecCapability(allowed=["node", "npm", "jest"]),
        NetworkCapability(policy="deny-all")
    ],
    limits=ResourceLimits(
        max_memory_mb=4096,
        max_execution_seconds=1800
    )
)

# Use custom preset
sandbox = manager.create_sandbox(
    task_id="task-007",
    preset=MY_PRESET
)
```

### Registering Presets

```python
# Register for reuse
CapabilityPreset.register("my-custom-preset", MY_PRESET)

# Use by name
sandbox = manager.create_sandbox(
    task_id="task-008",
    preset="my-custom-preset"
)
```

---

## Troubleshooting

### "Docker not available"

```bash
# Check Docker is running
docker info

# Start Docker Desktop (macOS/Windows)
# Or: sudo systemctl start docker (Linux)
```

### "Permission denied" inside sandbox

```python
# Check which capability is missing
result = sandbox.execute("cat /some/file")
print(result.violations)
# [{"type": "file_read", "path": "/some/file", "action": "blocked"}]

# Add required capability
sandbox.add_capability(FileCapability(action="read", path="/some/file"))
```

### "Container timeout"

```python
# Increase execution limit
limits = ResourceLimits(max_execution_seconds=3600)  # 1 hour
sandbox = manager.create_sandbox(task_id="long-task", limits=limits)
```

### "Out of memory"

```python
# Increase memory limit
limits = ResourceLimits(max_memory_mb=8192)  # 8GB
sandbox = manager.create_sandbox(task_id="memory-heavy", limits=limits)
```

---

## Configuration

In `project.config.yml`:

```yaml
sandbox:
  enabled: true
  default_preset: "test-runner"
  docker_socket: "/var/run/docker.sock"
  image: "node:20-slim"              # Base image
  network_policy: "deny-all"         # Default network
  
  limits:
    max_memory_mb: 2048
    max_cpu_cores: 2.0
    max_execution_seconds: 900
    max_disk_writes_mb: 500
  
  audit:
    enabled: true
    log_path: ".agent-state/security-audit.jsonl"
    log_violations: true
    log_allowed: false               # Only log denials
```

---

## Cross-References

- [CHECKPOINT_GUIDE.md](CHECKPOINT_GUIDE.md) — Sandbox state in checkpoints
- [DETERMINISM_GUIDE.md](DETERMINISM_GUIDE.md) — Deterministic sandbox execution
- [tests/test_phase3.py](../tests/test_phase3.py) — Sandbox test suite
- [POLICIES.md](POLICIES.md) — Security policy definitions
