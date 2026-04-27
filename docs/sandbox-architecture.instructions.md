# Sandbox Architecture & Capability-Based Security

**Phase 3: Sandboxing & Isolation**  
**Status:** In Progress  
**Updated:** 2026-04-27

---

## Overview

Phase 3 implements container-based sandboxing with capability-based security to isolate agent task execution. This prevents agents from accessing unauthorized resources and limits blast radius of failures or malicious behavior.

**Key Principles:**
- **Least Privilege:** Tasks only get capabilities they need
- **Defense in Depth:** Multiple isolation layers (containers, capabilities, network)
- **Fail-Secure:** Sandbox failures block execution rather than bypass security
- **Auditable:** All capability grants and violations logged

---

## Architecture Layers

### Layer 1: Container Isolation

**Technology Options:**
- **Docker** - Easiest integration, mature ecosystem
- **gVisor** - Stronger isolation, syscall filtering
- **Firecracker** - Minimal overhead, VM-level isolation

**Phase 3 Implementation:** Docker with gVisor runtime (balance of ease and security)

**Isolation Guarantees:**
- Separate filesystem namespace
- Network isolation (no egress by default)
- PID namespace (can't see host processes)
- Resource limits (CPU, memory, disk)
- Read-only root filesystem

### Layer 2: Capability-Based Security

**Capabilities** are fine-grained permissions granted to specific tasks.

**Core Capabilities:**
- `file:read` - Read files from workspace
- `file:write` - Write files to workspace
- `file:delete` - Delete files (restricted)
- `network:http` - HTTP/HTTPS requests
- `network:git` - Git operations (clone, push, pull)
- `exec:shell` - Execute shell commands (whitelist)
- `exec:test` - Run tests
- `exec:build` - Build operations
- `database:read` - Query database
- `database:write` - Modify database

**Capability Grant:**
```python
task = Task(
    task_id="test-runner",
    name="Run Unit Tests",
    action=run_tests,
    capabilities=[
        Capability("file:read", scope="/workspace/tests/**"),
        Capability("file:read", scope="/workspace/src/**"),
        Capability("exec:test", commands=["pytest", "npm test"]),
    ]
)
```

### Layer 3: Resource Limits

**Per-Task Limits:**
- Max execution time: 15 minutes (configurable)
- Max memory: 2GB (configurable)
- Max CPU: 2 cores (configurable)
- Max disk writes: 500MB (configurable)
- Max network egress: 100MB (configurable)

**Enforcement:**
- Docker resource constraints (`--memory`, `--cpus`)
- Timeout wrappers
- Disk quota monitoring
- Network traffic accounting

### Layer 4: Network Policy

**Default:** No network access

**Network Policies:**
- `deny-all` - No network (default)
- `allow-internal` - Only internal services (database, Redis)
- `allow-http` - HTTP/HTTPS to approved domains
- `allow-git` - Git operations to approved repos

**Implementation:**
- Docker network isolation
- iptables rules for egress filtering
- DNS filtering for domain whitelisting

---

## Sandbox Manager Design

### SandboxManager Class

```python
class SandboxManager:
    """
    Manages isolated execution environments for agent tasks.
    
    Responsibilities:
    - Create/destroy containers
    - Enforce capabilities
    - Monitor resource usage
    - Collect execution logs
    """
    
    def __init__(
        self,
        runtime: str = 'docker',  # 'docker', 'gvisor', 'firecracker'
        base_image: str = 'python:3.11-slim',
        workspace_path: str = '/workspace',
        network_policy: str = 'deny-all'
    ):
        pass
    
    def create_sandbox(
        self,
        sandbox_id: str,
        capabilities: List[Capability],
        resource_limits: ResourceLimits
    ) -> Sandbox:
        """Create isolated sandbox environment."""
        pass
    
    def execute_in_sandbox(
        self,
        sandbox: Sandbox,
        command: str,
        timeout: int = 300
    ) -> ExecutionResult:
        """Execute command in sandbox with capability enforcement."""
        pass
    
    def destroy_sandbox(self, sandbox_id: str):
        """Clean up sandbox resources."""
        pass
```

### Capability Model

```python
@dataclass
class Capability:
    """Fine-grained permission for task execution."""
    
    type: str  # file:read, file:write, network:http, etc.
    scope: str  # Path pattern or resource identifier
    constraints: Dict[str, Any] = field(default_factory=dict)
    
    def grants(self, action: Action) -> bool:
        """Check if capability grants permission for action."""
        if action.type != self.type:
            return False
        
        # Scope matching
        if self.type.startswith('file:'):
            return self._matches_path(action.target, self.scope)
        elif self.type.startswith('network:'):
            return self._matches_domain(action.target, self.scope)
        elif self.type.startswith('exec:'):
            return self._matches_command(action.target, self.scope)
        
        return False
    
    def _matches_path(self, path: str, pattern: str) -> bool:
        """Check if path matches glob pattern."""
        # Implementation with pathlib.Path.match()
        pass
    
    def _matches_domain(self, url: str, allowed: str) -> bool:
        """Check if URL domain is allowed."""
        # Implementation with urllib.parse
        pass
    
    def _matches_command(self, cmd: str, allowed: str) -> bool:
        """Check if command is in whitelist."""
        # Implementation with exact or prefix matching
        pass


@dataclass
class ResourceLimits:
    """Resource constraints for sandbox."""
    
    max_memory_mb: int = 2048
    max_cpu_cores: float = 2.0
    max_execution_seconds: int = 900  # 15 minutes
    max_disk_writes_mb: int = 500
    max_network_egress_mb: int = 100
```

### Sandbox State

```python
@dataclass
class SandboxState:
    """State of a running sandbox (stored in checkpoints)."""
    
    sandbox_id: str
    created_at: str
    capabilities: List[Capability]
    resource_limits: ResourceLimits
    network_policy: str
    container_id: str  # Docker container ID
    status: str  # running, stopped, error
    
    # Resource usage
    cpu_usage_seconds: float
    memory_peak_mb: int
    disk_writes_mb: int
    network_egress_mb: int
    
    # Execution history
    commands_executed: List[Dict]
    capability_violations: List[Dict]
    exit_code: Optional[int]


@dataclass
class ExecutionResult:
    """Result of command execution in sandbox."""
    
    stdout: str
    stderr: str
    exit_code: int
    execution_time_seconds: float
    
    # Resource usage
    cpu_usage_seconds: float
    memory_peak_mb: int
    disk_writes_mb: int
    
    # Security
    capability_checks: List[CapabilityCheck]
    violations: List[CapabilityViolation]
```

---

## Integration with Workflow Engine

### Sandboxed Task Execution

```python
# Before Phase 3 (unsandboxed)
def run_tests(context):
    result = subprocess.run(['pytest'], capture_output=True)
    return result.returncode == 0

# After Phase 3 (sandboxed)
from sandbox import SandboxManager, Capability

sandbox_mgr = SandboxManager()

def run_tests_sandboxed(context):
    sandbox = sandbox_mgr.create_sandbox(
        sandbox_id=f"test-{context['task_id']}",
        capabilities=[
            Capability("file:read", scope="/workspace/tests/**"),
            Capability("file:read", scope="/workspace/src/**"),
            Capability("exec:test", scope="pytest"),
        ],
        resource_limits=ResourceLimits(
            max_memory_mb=1024,
            max_execution_seconds=300
        )
    )
    
    try:
        result = sandbox_mgr.execute_in_sandbox(
            sandbox,
            command='pytest -v',
            timeout=300
        )
        return result.exit_code == 0
    finally:
        sandbox_mgr.destroy_sandbox(sandbox.sandbox_id)
```

### Workflow Engine Changes

```python
class WorkflowEngine:
    """Enhanced with sandbox support."""
    
    def __init__(
        self,
        db: Database,
        checkpoint_manager: CheckpointManager,
        sandbox_manager: Optional[SandboxManager] = None  # NEW
    ):
        self.db = db
        self.checkpoint_manager = checkpoint_manager
        self.sandbox_manager = sandbox_manager or SandboxManager()
    
    def _execute_task(
        self,
        task: Task,
        workflow: Workflow
    ) -> bool:
        """Execute task with sandbox isolation."""
        
        # Create sandbox if task requires isolation
        if task.sandboxed:
            sandbox = self.sandbox_manager.create_sandbox(
                sandbox_id=f"{workflow.workflow_id}-{task.task_id}",
                capabilities=task.capabilities,
                resource_limits=task.resource_limits
            )
            
            try:
                # Execute in sandbox
                result = self._execute_in_sandbox(task, workflow, sandbox)
            finally:
                # Always clean up
                self.sandbox_manager.destroy_sandbox(sandbox.sandbox_id)
        else:
            # Legacy unsandboxed execution
            result = task.action(workflow.context)
        
        return result
```

---

## Checkpoint Integration

### Enhanced Checkpoint State

```python
@dataclass
class CheckpointState:
    """Extended with sandbox state."""
    
    sprint_id: str
    phase: str
    fsm_state: str
    logical_time: int
    context: Dict
    ledger_items: List
    active_tasks: List
    completed_tasks: List
    environment: Dict
    metadata: Dict
    
    # NEW: Sandbox state
    active_sandboxes: List[SandboxState]  # Currently running sandboxes
    sandbox_history: List[SandboxState]   # All sandboxes used in sprint
```

**Why Track Sandbox State?**
- Resume requires recreating sandboxes with same capabilities
- Audit trail for security review
- Resource usage tracking for billing/optimization
- Debug capability violations

---

## Security Policies

### Capability Assignment Rules

**Default Policy:** Least privilege

```yaml
# Default capabilities (minimal)
defaults:
  file:read: ["/workspace/src/**", "/workspace/tests/**"]
  file:write: []  # No write by default
  network: deny-all
  exec: []  # No exec by default

# Task-specific overrides
task_policies:
  test:
    exec:test: ["pytest", "npm test", "cargo test"]
  
  build:
    file:write: ["/workspace/dist/**", "/workspace/build/**"]
    exec:build: ["npm run build", "cargo build"]
  
  deploy:
    network:http: ["api.production.com"]
    file:read: ["/workspace/dist/**"]
```

### Violation Response

**On Capability Violation:**
1. Block the action (deny execution)
2. Log violation to audit log
3. Increment violation counter
4. If violations > threshold: terminate sandbox
5. Report to security monitoring

**Example Violation:**
```json
{
  "timestamp": "2026-04-27T15:30:45Z",
  "event": "capability_violation",
  "sandbox_id": "sprint-042-test-runner",
  "task_id": "run-integration-tests",
  "violation": {
    "type": "file:write",
    "attempted_path": "/etc/passwd",
    "reason": "No write capability granted for /etc/**"
  },
  "action": "blocked"
}
```

---

## Docker Integration

### Container Configuration

**Dockerfile for Sandbox:**
```dockerfile
FROM python:3.11-slim

# Install minimal dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 agent
USER agent

# Set working directory
WORKDIR /workspace

# Entrypoint for command execution
ENTRYPOINT ["/bin/sh", "-c"]
```

**Container Creation:**
```python
import docker

client = docker.from_env()

container = client.containers.run(
    image='agent-sandbox:latest',
    command=command,
    detach=True,
    remove=True,  # Auto-remove after exit
    
    # Resource limits
    mem_limit='2g',
    cpu_quota=200000,  # 2 CPUs
    
    # Security
    read_only=True,  # Read-only root filesystem
    security_opt=['no-new-privileges'],
    cap_drop=['ALL'],  # Drop all capabilities
    
    # Volumes
    volumes={
        workspace_path: {
            'bind': '/workspace',
            'mode': 'ro'  # Read-only by default
        }
    },
    
    # Network
    network_mode='none',  # No network by default
    
    # Environment
    environment={
        'PYTHONUNBUFFERED': '1',
        'NO_COLOR': '1'
    }
)
```

---

## Testing Strategy

### Unit Tests
- Capability matching logic
- Resource limit enforcement
- Sandbox creation/destruction
- Network policy application

### Integration Tests
- Execute commands in sandbox
- Verify isolation (can't access host files)
- Test capability violations (blocked correctly)
- Resource limit enforcement (OOM, timeout)

### Security Tests
- Container escape attempts (should fail)
- Path traversal (blocked by capabilities)
- Network access (blocked by policy)
- Privilege escalation (blocked by cap_drop)

---

## Performance Considerations

### Container Overhead
- **Docker:** ~100-200ms startup per container
- **gVisor:** ~50-100ms startup (lighter weight)
- **Firecracker:** ~125ms startup (VM overhead)

### Optimization Strategies
- **Container pooling:** Pre-create containers, reuse for multiple tasks
- **Layered caching:** Cache base images with common dependencies
- **Resource tuning:** Adjust CPU/memory limits based on task type
- **Parallel execution:** Run independent sandboxes concurrently

### Monitoring
- Track sandbox creation/destruction times
- Monitor resource usage per sandbox
- Alert on repeated capability violations
- Dashboard for sandbox utilization

---

## Roadmap

### Phase 3.1 (Current Sprint) ✅
- [x] Design sandbox architecture
- [ ] Implement Docker-based sandbox manager
- [ ] Build capability framework
- [ ] Integrate with workflow engine
- [ ] Add checkpoint support for sandbox state

### Phase 3.2 (Next Sprint)
- [ ] Add gVisor runtime support
- [ ] Container pooling for performance
- [ ] Advanced network policies (domain whitelisting)
- [ ] Resource usage analytics

### Phase 3.3 (Future)
- [ ] Firecracker microVM support
- [ ] Distributed sandbox orchestration (Kubernetes)
- [ ] Hardware isolation (confidential computing)
- [ ] Real-time security monitoring

---

## References

**Container Security:**
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [gVisor Documentation](https://gvisor.dev/docs/)
- [Firecracker MicroVMs](https://firecracker-microvm.github.io/)

**Capability-Based Security:**
- [Capability-Based Security (Wikipedia)](https://en.wikipedia.org/wiki/Capability-based_security)
- [POSIX Capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html)

**Container Isolation:**
- [Linux Namespaces](https://man7.org/linux/man-pages/man7/namespaces.7.html)
- [cgroups v2](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)
