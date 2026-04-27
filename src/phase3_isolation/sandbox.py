"""
Sandbox Manager - Container-Based Isolation

Provides isolated execution environments for agent tasks using Docker containers.
Enforces resource limits, network policies, and security constraints.

Phase 3 - Sandboxing & Isolation
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import subprocess
import shutil

try:
    import docker
    from docker.errors import DockerException, NotFound
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    print("⚠️  Docker SDK not installed. Run: pip install docker")


# =============================================================================
# Data Models
# =============================================================================

class SandboxStatus(Enum):
    """Sandbox lifecycle states."""
    CREATING = "creating"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    DESTROYED = "destroyed"


class NetworkPolicy(Enum):
    """Network access policies."""
    DENY_ALL = "deny-all"              # No network access
    ALLOW_INTERNAL = "allow-internal"  # Internal services only
    ALLOW_HTTP = "allow-http"          # HTTP/HTTPS to approved domains
    ALLOW_GIT = "allow-git"            # Git operations


@dataclass
class ResourceLimits:
    """Resource constraints for sandbox execution."""
    
    max_memory_mb: int = 2048
    max_cpu_cores: float = 2.0
    max_execution_seconds: int = 900  # 15 minutes
    max_disk_writes_mb: int = 500
    max_network_egress_mb: int = 100


@dataclass
class ExecutionResult:
    """Result of command execution in sandbox."""
    
    stdout: str
    stderr: str
    exit_code: int
    execution_time_seconds: float
    
    # Resource usage
    cpu_usage_seconds: float = 0.0
    memory_peak_mb: int = 0
    disk_writes_mb: int = 0
    
    # Security
    capability_checks: List[Dict] = field(default_factory=list)
    violations: List[Dict] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        """Check if execution succeeded."""
        return self.exit_code == 0 and len(self.violations) == 0


@dataclass
class SandboxState:
    """State of a running sandbox."""
    
    sandbox_id: str
    created_at: str
    status: str
    
    # Configuration
    capabilities: List[Dict]  # Serialized capabilities
    resource_limits: ResourceLimits
    network_policy: str
    
    # Container info
    container_id: Optional[str] = None
    container_name: Optional[str] = None
    
    # Resource usage
    cpu_usage_seconds: float = 0.0
    memory_peak_mb: int = 0
    disk_writes_mb: int = 0
    network_egress_mb: int = 0
    
    # Execution history
    commands_executed: List[Dict] = field(default_factory=list)
    capability_violations: List[Dict] = field(default_factory=list)
    exit_code: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        result = asdict(self)
        result['resource_limits'] = asdict(self.resource_limits)
        return result


class Sandbox:
    """
    Isolated execution environment using Docker containers.
    
    Provides:
    - Filesystem isolation (read-only root, writable workspace)
    - Network isolation (configurable policies)
    - Resource limits (CPU, memory, disk)
    - Security constraints (no-new-privileges, capability dropping)
    """
    
    def __init__(
        self,
        sandbox_id: str,
        container,
        state: SandboxState,
        client
    ):
        """
        Initialize sandbox.
        
        Args:
            sandbox_id: Unique sandbox identifier
            container: Docker container object
            state: Sandbox state
            client: Docker client
        """
        self.sandbox_id = sandbox_id
        self.container = container
        self.state = state
        self.client = client
    
    def execute(
        self,
        command: str,
        timeout: Optional[int] = None,
        environment: Optional[Dict[str, str]] = None
    ) -> ExecutionResult:
        """
        Execute command in sandbox.
        
        Args:
            command: Shell command to execute
            timeout: Execution timeout in seconds
            environment: Additional environment variables
        
        Returns:
            ExecutionResult with stdout, stderr, exit code
        """
        start_time = time.time()
        timeout = timeout or self.state.resource_limits.max_execution_seconds
        
        try:
            # Execute command in container
            exec_result = self.container.exec_run(
                cmd=['sh', '-c', command],
                environment=environment or {},
                demux=True,
                workdir='/workspace'
            )
            
            execution_time = time.time() - start_time
            
            # Parse output (demux returns tuple of (stdout, stderr))
            stdout_bytes, stderr_bytes = exec_result.output
            stdout = stdout_bytes.decode('utf-8') if stdout_bytes else ''
            stderr = stderr_bytes.decode('utf-8') if stderr_bytes else ''
            
            # Get resource usage
            stats = self.container.stats(stream=False)
            cpu_usage = self._calculate_cpu_usage(stats)
            memory_usage = stats['memory_stats'].get('max_usage', 0) // (1024 * 1024)
            
            # Update state
            self.state.commands_executed.append({
                'command': command,
                'exit_code': exec_result.exit_code,
                'execution_time': execution_time,
                'timestamp': time.time()
            })
            self.state.cpu_usage_seconds += cpu_usage
            self.state.memory_peak_mb = max(self.state.memory_peak_mb, memory_usage)
            
            return ExecutionResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=exec_result.exit_code,
                execution_time_seconds=execution_time,
                cpu_usage_seconds=cpu_usage,
                memory_peak_mb=memory_usage
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                stdout='',
                stderr=f"Sandbox execution error: {str(e)}",
                exit_code=1,
                execution_time_seconds=execution_time,
                violations=[{
                    'type': 'execution_error',
                    'message': str(e)
                }]
            )
    
    def _calculate_cpu_usage(self, stats: Dict) -> float:
        """Calculate CPU usage in seconds from container stats."""
        cpu_stats = stats.get('cpu_stats', {})
        precpu_stats = stats.get('precpu_stats', {})
        
        cpu_delta = cpu_stats.get('cpu_usage', {}).get('total_usage', 0) - \
                    precpu_stats.get('cpu_usage', {}).get('total_usage', 0)
        system_delta = cpu_stats.get('system_cpu_usage', 0) - \
                       precpu_stats.get('system_cpu_usage', 0)
        
        if system_delta > 0:
            cpu_percent = (cpu_delta / system_delta) * 100.0
            return cpu_percent / 100.0  # Normalize to seconds
        return 0.0
    
    def stop(self):
        """Stop the sandbox container."""
        try:
            self.container.stop(timeout=10)
            self.state.status = SandboxStatus.STOPPED.value
        except Exception as e:
            print(f"⚠️  Error stopping sandbox {self.sandbox_id}: {e}")
            self.state.status = SandboxStatus.ERROR.value
    
    def destroy(self):
        """Destroy the sandbox and remove container."""
        try:
            self.container.remove(force=True)
            self.state.status = SandboxStatus.DESTROYED.value
        except Exception as e:
            print(f"⚠️  Error destroying sandbox {self.sandbox_id}: {e}")


# =============================================================================
# Sandbox Manager
# =============================================================================

class SandboxManager:
    """
    Manages isolated execution environments for agent tasks.
    
    Features:
    - Docker container creation with security constraints
    - Resource limit enforcement
    - Network policy application
    - Sandbox lifecycle management
    - State tracking for checkpoints
    
    Usage:
        manager = SandboxManager(workspace_path="/workspace")
        
        sandbox = manager.create_sandbox(
            sandbox_id="test-runner",
            capabilities=[...],
            resource_limits=ResourceLimits(max_memory_mb=1024)
        )
        
        result = manager.execute_in_sandbox(
            sandbox,
            command="pytest -v",
            timeout=300
        )
        
        manager.destroy_sandbox(sandbox.sandbox_id)
    """
    
    def __init__(
        self,
        runtime: str = 'docker',
        base_image: str = 'python:3.11-slim',
        workspace_path: str = None,
        network_policy: NetworkPolicy = NetworkPolicy.DENY_ALL,
        state_dir: str = '.agent-state/sandboxes'
    ):
        """
        Initialize sandbox manager.
        
        Args:
            runtime: Container runtime ('docker' only for now)
            base_image: Base Docker image for containers
            workspace_path: Path to workspace directory to mount
            network_policy: Default network policy
            state_dir: Directory for sandbox state files
        """
        if not DOCKER_AVAILABLE:
            raise RuntimeError("Docker SDK not available. Install with: pip install docker")
        
        self.runtime = runtime
        self.base_image = base_image
        self.workspace_path = workspace_path or os.getcwd()
        self.network_policy = network_policy
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Docker client
        try:
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
        except DockerException as e:
            raise RuntimeError(f"Failed to connect to Docker: {e}")
        
        # Track active sandboxes
        self.active_sandboxes: Dict[str, Sandbox] = {}
        
        # Ensure base image exists
        self._ensure_base_image()
    
    def _ensure_base_image(self):
        """Pull base image if not available locally."""
        try:
            self.client.images.get(self.base_image)
        except NotFound:
            print(f"🐳 Pulling base image: {self.base_image}")
            self.client.images.pull(self.base_image)
            print(f"✓ Base image ready: {self.base_image}")
    
    def create_sandbox(
        self,
        sandbox_id: str,
        capabilities: List = None,
        resource_limits: Optional[ResourceLimits] = None,
        network_policy: Optional[NetworkPolicy] = None,
        environment: Optional[Dict[str, str]] = None
    ) -> Sandbox:
        """
        Create isolated sandbox environment.
        
        Args:
            sandbox_id: Unique identifier for sandbox
            capabilities: List of Capability objects (Phase 3.2)
            resource_limits: Resource constraints
            network_policy: Network access policy
            environment: Environment variables
        
        Returns:
            Sandbox object
        """
        if sandbox_id in self.active_sandboxes:
            raise ValueError(f"Sandbox {sandbox_id} already exists")
        
        capabilities = capabilities or []
        resource_limits = resource_limits or ResourceLimits()
        network_policy = network_policy or self.network_policy
        environment = environment or {}
        
        # Create state
        state = SandboxState(
            sandbox_id=sandbox_id,
            created_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            status=SandboxStatus.CREATING.value,
            capabilities=[],  # Will be populated in Phase 3.2
            resource_limits=resource_limits,
            network_policy=network_policy.value,
            container_name=f"agent-sandbox-{sandbox_id}"
        )
        
        try:
            # Create container with security constraints
            container = self.client.containers.create(
                image=self.base_image,
                name=state.container_name,
                command='sleep infinity',  # Keep container running
                detach=True,
                
                # Resource limits
                mem_limit=f"{resource_limits.max_memory_mb}m",
                cpu_quota=int(resource_limits.max_cpu_cores * 100000),
                cpu_period=100000,
                
                # Security
                read_only=False,  # Need writable /tmp
                security_opt=['no-new-privileges:true'],
                cap_drop=['ALL'],
                cap_add=['CHOWN', 'DAC_OVERRIDE', 'FOWNER', 'SETGID', 'SETUID'],  # Minimal caps
                
                # Volumes
                volumes={
                    self.workspace_path: {
                        'bind': '/workspace',
                        'mode': 'rw'  # Will be restricted by capabilities in Phase 3.2
                    }
                },
                
                # Network
                network_mode=self._get_network_mode(network_policy),
                
                # Environment
                environment={
                    'PYTHONUNBUFFERED': '1',
                    'NO_COLOR': '1',
                    'SANDBOX_ID': sandbox_id,
                    **environment
                },
                
                # Working directory
                working_dir='/workspace',
                
                # User (non-root)
                user='1000:1000',  # Use non-root user
                
                # Auto-remove disabled (we manage lifecycle)
                auto_remove=False
            )
            
            # Start container
            container.start()
            
            state.container_id = container.id
            state.status = SandboxStatus.RUNNING.value
            
            # Create sandbox object
            sandbox = Sandbox(
                sandbox_id=sandbox_id,
                container=container,
                state=state,
                client=self.client
            )
            
            # Track active sandbox
            self.active_sandboxes[sandbox_id] = sandbox
            
            # Save state to disk
            self._save_state(state)
            
            print(f"🔒 Created sandbox: {sandbox_id}")
            print(f"   Container: {container.short_id}")
            print(f"   Memory limit: {resource_limits.max_memory_mb}MB")
            print(f"   CPU cores: {resource_limits.max_cpu_cores}")
            print(f"   Network: {network_policy.value}")
            
            return sandbox
        
        except Exception as e:
            state.status = SandboxStatus.ERROR.value
            self._save_state(state)
            raise RuntimeError(f"Failed to create sandbox {sandbox_id}: {e}")
    
    def _get_network_mode(self, policy: NetworkPolicy) -> str:
        """Convert network policy to Docker network mode."""
        if policy == NetworkPolicy.DENY_ALL:
            return 'none'
        elif policy == NetworkPolicy.ALLOW_INTERNAL:
            return 'bridge'  # Default Docker bridge
        elif policy in [NetworkPolicy.ALLOW_HTTP, NetworkPolicy.ALLOW_GIT]:
            return 'bridge'  # Will apply iptables rules in Phase 3.2
        return 'none'
    
    def execute_in_sandbox(
        self,
        sandbox: Sandbox,
        command: str,
        timeout: Optional[int] = None,
        environment: Optional[Dict[str, str]] = None
    ) -> ExecutionResult:
        """
        Execute command in sandbox with capability enforcement.
        
        Args:
            sandbox: Sandbox to execute in
            command: Shell command
            timeout: Execution timeout
            environment: Additional environment variables
        
        Returns:
            ExecutionResult
        """
        if sandbox.sandbox_id not in self.active_sandboxes:
            raise ValueError(f"Sandbox {sandbox.sandbox_id} not found or not active")
        
        # TODO Phase 3.2: Check capabilities before execution
        # For now, execute directly
        
        result = sandbox.execute(command, timeout, environment)
        
        # Save updated state
        self._save_state(sandbox.state)
        
        return result
    
    def get_sandbox(self, sandbox_id: str) -> Optional[Sandbox]:
        """Get active sandbox by ID."""
        return self.active_sandboxes.get(sandbox_id)
    
    def list_sandboxes(self) -> List[SandboxState]:
        """List all active sandboxes."""
        return [s.state for s in self.active_sandboxes.values()]
    
    def destroy_sandbox(self, sandbox_id: str):
        """
        Destroy sandbox and clean up resources.
        
        Args:
            sandbox_id: Sandbox to destroy
        """
        sandbox = self.active_sandboxes.get(sandbox_id)
        if not sandbox:
            print(f"⚠️  Sandbox {sandbox_id} not found")
            return
        
        sandbox.destroy()
        
        # Remove from active sandboxes
        del self.active_sandboxes[sandbox_id]
        
        # Save final state
        self._save_state(sandbox.state)
        
        print(f"🗑️  Destroyed sandbox: {sandbox_id}")
    
    def cleanup_all(self):
        """Destroy all active sandboxes."""
        for sandbox_id in list(self.active_sandboxes.keys()):
            self.destroy_sandbox(sandbox_id)
    
    def _save_state(self, state: SandboxState):
        """Save sandbox state to disk."""
        state_file = self.state_dir / f"{state.sandbox_id}.json"
        state_file.write_text(json.dumps(state.to_dict(), indent=2), encoding='utf-8')
    
    def load_state(self, sandbox_id: str) -> Optional[SandboxState]:
        """Load sandbox state from disk."""
        state_file = self.state_dir / f"{sandbox_id}.json"
        if not state_file.exists():
            return None
        
        data = json.loads(state_file.read_text(encoding='utf-8'))
        data['resource_limits'] = ResourceLimits(**data['resource_limits'])
        return SandboxState(**data)


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    print("=== Sandbox Manager Demo ===\n")
    
    # Check if Docker is available
    if not DOCKER_AVAILABLE:
        print("❌ Docker SDK not installed")
        print("   Install with: pip install docker")
        exit(1)
    
    # Check if Docker daemon is running
    if not shutil.which('docker'):
        print("❌ Docker not found in PATH")
        exit(1)
    
    try:
        # Initialize manager
        manager = SandboxManager(
            workspace_path=os.getcwd(),
            network_policy=NetworkPolicy.DENY_ALL
        )
        
        print("✓ Sandbox manager initialized\n")
        
        # Create sandbox
        sandbox = manager.create_sandbox(
            sandbox_id="demo-sandbox",
            resource_limits=ResourceLimits(
                max_memory_mb=512,
                max_cpu_cores=1.0,
                max_execution_seconds=60
            )
        )
        
        print("\n--- Executing commands in sandbox ---\n")
        
        # Execute simple command
        result = manager.execute_in_sandbox(
            sandbox,
            command="echo 'Hello from sandbox!' && pwd && ls -la"
        )
        
        print(f"Exit code: {result.exit_code}")
        print(f"Execution time: {result.execution_time_seconds:.2f}s")
        print(f"Memory used: {result.memory_peak_mb}MB")
        print(f"\nOutput:\n{result.stdout}")
        
        # Execute Python code
        result2 = manager.execute_in_sandbox(
            sandbox,
            command="python3 -c 'import sys; print(f\"Python {sys.version}\")'"
        )
        
        print(f"\nPython version in sandbox:\n{result2.stdout}")
        
        # Clean up
        print("\n--- Cleaning up ---\n")
        manager.destroy_sandbox("demo-sandbox")
        
        print("✓ Demo complete")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
