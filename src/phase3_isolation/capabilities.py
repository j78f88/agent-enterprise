"""
Capability-Based Security Framework

Fine-grained permission system for sandbox operations.
Capabilities grant specific access to files, network, commands, and database.

Phase 3 - Sandboxing & Isolation
"""

import re
import fnmatch
from pathlib import Path
from typing import List, Dict, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse
import json


# =============================================================================
# Capability Types
# =============================================================================

class CapabilityType(Enum):
    """Types of capabilities that can be granted."""
    
    # Filesystem
    FILE_READ = "file:read"
    FILE_WRITE = "file:write"
    FILE_DELETE = "file:delete"
    FILE_EXECUTE = "file:execute"
    
    # Network
    NETWORK_HTTP = "network:http"
    NETWORK_HTTPS = "network:https"
    NETWORK_GIT = "network:git"
    NETWORK_INTERNAL = "network:internal"
    
    # Command execution
    EXEC_SHELL = "exec:shell"
    EXEC_TEST = "exec:test"
    EXEC_BUILD = "exec:build"
    EXEC_LINT = "exec:lint"
    
    # Database
    DATABASE_READ = "database:read"
    DATABASE_WRITE = "database:write"
    
    # System
    SYSTEM_ENV = "system:env"  # Read environment variables
    SYSTEM_TIME = "system:time"  # Access system time


# =============================================================================
# Actions
# =============================================================================

@dataclass
class Action:
    """Represents an action requiring capability check."""
    
    type: str  # Matches CapabilityType value
    target: str  # Path, URL, command, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @staticmethod
    def file_read(path: str) -> 'Action':
        """Create file read action."""
        return Action(type=CapabilityType.FILE_READ.value, target=path)
    
    @staticmethod
    def file_write(path: str) -> 'Action':
        """Create file write action."""
        return Action(type=CapabilityType.FILE_WRITE.value, target=path)
    
    @staticmethod
    def file_delete(path: str) -> 'Action':
        """Create file delete action."""
        return Action(type=CapabilityType.FILE_DELETE.value, target=path)
    
    @staticmethod
    def network_http(url: str) -> 'Action':
        """Create HTTP request action."""
        return Action(type=CapabilityType.NETWORK_HTTP.value, target=url)
    
    @staticmethod
    def exec_command(command: str, cmd_type: str = "shell") -> 'Action':
        """Create command execution action."""
        cap_type = f"exec:{cmd_type}"
        return Action(type=cap_type, target=command)
    
    @staticmethod
    def database_query(query: str) -> 'Action':
        """Create database read action."""
        return Action(
            type=CapabilityType.DATABASE_READ.value,
            target=query,
            metadata={'query_type': 'SELECT'}
        )
    
    @staticmethod
    def database_modify(query: str) -> 'Action':
        """Create database write action."""
        return Action(
            type=CapabilityType.DATABASE_WRITE.value,
            target=query,
            metadata={'query_type': 'INSERT/UPDATE/DELETE'}
        )


# =============================================================================
# Capabilities
# =============================================================================

@dataclass
class Capability:
    """
    Fine-grained permission for specific operations.
    
    A capability grants permission to perform actions of a specific type
    on resources matching the scope pattern.
    
    Examples:
        # Read files in tests directory
        Capability(
            type="file:read",
            scope="/workspace/tests/**"
        )
        
        # Execute pytest command
        Capability(
            type="exec:test",
            scope="pytest",
            constraints={"args_pattern": "-v --cov"}
        )
        
        # Make HTTP requests to API
        Capability(
            type="network:https",
            scope="api.example.com",
            constraints={"methods": ["GET", "POST"]}
        )
    """
    
    type: str  # Capability type (matches CapabilityType)
    scope: str  # Resource identifier (path pattern, domain, command)
    constraints: Dict[str, Any] = field(default_factory=dict)
    description: str = ""  # Human-readable description
    
    def grants(self, action: Action) -> bool:
        """
        Check if this capability grants permission for the action.
        
        Args:
            action: Action to check
        
        Returns:
            True if capability grants permission
        """
        # Type must match
        if action.type != self.type:
            return False
        
        # Check scope based on capability type
        if self.type.startswith('file:'):
            return self._matches_path(action.target, self.scope)
        elif self.type.startswith('network:'):
            return self._matches_network(action.target, self.scope)
        elif self.type.startswith('exec:'):
            return self._matches_command(action.target, self.scope)
        elif self.type.startswith('database:'):
            return self._matches_database(action.target, self.scope)
        elif self.type.startswith('system:'):
            return self._matches_system(action.target, self.scope)
        
        return False
    
    def _matches_path(self, path: str, pattern: str) -> bool:
        """
        Check if path matches glob pattern.
        
        Examples:
            /workspace/tests/** matches /workspace/tests/test_foo.py
            /workspace/src/*.py matches /workspace/src/main.py
            /workspace/dist matches /workspace/dist exactly
        """
        # Normalize paths
        path = Path(path).as_posix()
        pattern = Path(pattern).as_posix()
        
        # Exact match
        if path == pattern:
            return True
        
        # Glob pattern match
        if fnmatch.fnmatch(path, pattern):
            return True
        
        # Directory prefix match (pattern ends with /**)
        if pattern.endswith('/**'):
            dir_pattern = pattern[:-3]  # Remove /**
            if path.startswith(dir_pattern):
                return True
        
        return False
    
    def _matches_network(self, url: str, allowed: str) -> bool:
        """
        Check if URL is allowed.
        
        Examples:
            api.example.com matches https://api.example.com/endpoint
            *.github.com matches api.github.com
            localhost:* matches localhost:3000
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path  # Handle both full URLs and bare domains
            
            # Remove port for comparison
            domain = domain.split(':')[0] if ':' in domain else domain
            allowed_domain = allowed.split(':')[0] if ':' in allowed else allowed
            
            # Exact match
            if domain == allowed_domain:
                return True
            
            # Wildcard match
            if fnmatch.fnmatch(domain, allowed_domain):
                return True
            
            # Check constraints (e.g., allowed methods)
            if self.constraints.get('methods'):
                method = parsed.scheme.upper()  # GET, POST, etc.
                if method not in self.constraints['methods']:
                    return False
            
            return False
        except Exception:
            return False
    
    def _matches_command(self, command: str, allowed: str) -> bool:
        """
        Check if command is allowed.
        
        Examples:
            pytest matches "pytest -v"
            npm matches "npm test"
            pytest|npm matches "pytest" or "npm test"
        """
        # Get base command (first word)
        command_base = command.split()[0]
        
        # Handle multiple allowed commands (pytest|npm|cargo)
        if '|' in allowed:
            allowed_commands = [c.strip() for c in allowed.split('|')]
            if command_base in allowed_commands:
                return True
        else:
            # Single allowed command
            if command_base == allowed:
                return True
            
            # Prefix match (e.g., "npm" matches "npm test")
            if command.startswith(allowed + ' '):
                return True
        
        # Check argument constraints
        if self.constraints.get('args_pattern'):
            pattern = self.constraints['args_pattern']
            if not re.search(pattern, command):
                return False
        
        # Check forbidden arguments (e.g., --rm, --privileged for docker)
        if self.constraints.get('forbidden_args'):
            forbidden = self.constraints['forbidden_args']
            for arg in forbidden:
                if arg in command:
                    return False
        
        return False
    
    def _matches_database(self, query: str, scope: str) -> bool:
        """
        Check if database query is allowed.
        
        scope can be:
        - Table name: "ledger", "bugs"
        - Wildcard: "*" (all tables)
        - Pattern: "ledger|bugs|sprints"
        """
        # Extract table name from query (simplified)
        query_upper = query.upper()
        
        # Allow all tables
        if scope == '*':
            return True
        
        # Check if scope (table name) appears in query
        if '|' in scope:
            tables = [t.strip() for t in scope.split('|')]
            return any(table.upper() in query_upper for table in tables)
        else:
            return scope.upper() in query_upper
    
    def _matches_system(self, target: str, scope: str) -> bool:
        """Check if system action is allowed."""
        # For system capabilities, scope is usually '*' or specific resource
        if scope == '*':
            return True
        return target == scope
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize capability to dictionary."""
        return {
            'type': self.type,
            'scope': self.scope,
            'constraints': self.constraints,
            'description': self.description
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Capability':
        """Deserialize capability from dictionary."""
        return Capability(
            type=data['type'],
            scope=data['scope'],
            constraints=data.get('constraints', {}),
            description=data.get('description', '')
        )


# =============================================================================
# Capability Checker
# =============================================================================

@dataclass
class CapabilityCheck:
    """Result of a capability check."""
    
    action: Action
    granted: bool
    capability: Optional[Capability]  # Capability that granted permission
    reason: str


@dataclass
class CapabilityViolation:
    """Record of a capability violation."""
    
    action: Action
    reason: str
    timestamp: float
    sandbox_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize violation to dictionary."""
        return {
            'action_type': self.action.type,
            'action_target': self.action.target,
            'reason': self.reason,
            'timestamp': self.timestamp,
            'sandbox_id': self.sandbox_id
        }


class CapabilityEnforcer:
    """
    Enforces capability-based security policies.
    
    Checks actions against granted capabilities and logs violations.
    
    Usage:
        enforcer = CapabilityEnforcer(capabilities=[...])
        
        action = Action.file_write("/workspace/output.txt")
        check = enforcer.check(action)
        
        if check.granted:
            # Proceed with action
        else:
            # Block action, log violation
    """
    
    def __init__(
        self,
        capabilities: List[Capability],
        strict_mode: bool = True,
        audit_log_path: Optional[str] = None
    ):
        """
        Initialize capability enforcer.
        
        Args:
            capabilities: List of granted capabilities
            strict_mode: If True, deny actions without explicit capability
            audit_log_path: Path to audit log file (optional)
        """
        self.capabilities = capabilities
        self.strict_mode = strict_mode
        self.audit_log_path = audit_log_path
        
        self.checks: List[CapabilityCheck] = []
        self.violations: List[CapabilityViolation] = []
    
    def check(self, action: Action, sandbox_id: str = "") -> CapabilityCheck:
        """
        Check if action is permitted by capabilities.
        
        Args:
            action: Action to check
            sandbox_id: Sandbox ID (for violation tracking)
        
        Returns:
            CapabilityCheck result
        """
        # Check each capability
        for cap in self.capabilities:
            if cap.grants(action):
                check = CapabilityCheck(
                    action=action,
                    granted=True,
                    capability=cap,
                    reason=f"Granted by capability: {cap.type} {cap.scope}"
                )
                self.checks.append(check)
                self._audit_log(check)
                return check
        
        # No capability grants permission
        reason = f"No capability grants permission for {action.type} on {action.target}"
        
        if self.strict_mode:
            # Strict mode: deny by default
            check = CapabilityCheck(
                action=action,
                granted=False,
                capability=None,
                reason=reason
            )
            
            # Record violation
            violation = CapabilityViolation(
                action=action,
                reason=reason,
                timestamp=self._get_timestamp(),
                sandbox_id=sandbox_id
            )
            self.violations.append(violation)
            
            self.checks.append(check)
            self._audit_log(check, violation=violation)
            
            return check
        else:
            # Permissive mode: allow by default (log warning)
            check = CapabilityCheck(
                action=action,
                granted=True,
                capability=None,
                reason="Allowed by permissive mode (no explicit capability)"
            )
            self.checks.append(check)
            self._audit_log(check, warning=True)
            return check
    
    def check_and_enforce(self, action: Action, sandbox_id: str = "") -> bool:
        """
        Check capability and return simple allow/deny.
        
        Args:
            action: Action to check
            sandbox_id: Sandbox ID
        
        Returns:
            True if allowed, False if denied
        """
        check = self.check(action, sandbox_id)
        return check.granted
    
    def get_violations(self) -> List[CapabilityViolation]:
        """Get all recorded violations."""
        return self.violations
    
    def get_violation_count(self) -> int:
        """Get count of violations."""
        return len(self.violations)
    
    def clear_violations(self):
        """Clear violation history."""
        self.violations.clear()
    
    def _audit_log(
        self,
        check: CapabilityCheck,
        violation: Optional[CapabilityViolation] = None,
        warning: bool = False
    ):
        """Write capability check to audit log."""
        if not self.audit_log_path:
            return
        
        log_entry = {
            'timestamp': self._get_timestamp(),
            'action_type': check.action.type,
            'action_target': check.action.target,
            'granted': check.granted,
            'reason': check.reason,
            'capability': check.capability.to_dict() if check.capability else None,
            'violation': violation.to_dict() if violation else None,
            'warning': warning
        }
        
        try:
            with open(self.audit_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"⚠️  Failed to write audit log: {e}")
    
    def _get_timestamp(self) -> float:
        """Get current timestamp."""
        import time
        return time.time()


# =============================================================================
# Capability Presets
# =============================================================================

class CapabilityPresets:
    """Predefined capability sets for common tasks."""
    
    @staticmethod
    def read_only_workspace() -> List[Capability]:
        """Read-only access to workspace."""
        return [
            Capability(
                type=CapabilityType.FILE_READ.value,
                scope="/workspace/**",
                description="Read any file in workspace"
            )
        ]
    
    @staticmethod
    def test_runner() -> List[Capability]:
        """Capabilities for running tests."""
        return [
            Capability(
                type=CapabilityType.FILE_READ.value,
                scope="/workspace/**",
                description="Read source and test files"
            ),
            Capability(
                type=CapabilityType.EXEC_TEST.value,
                scope="pytest|npm|cargo",
                description="Run test commands"
            ),
            Capability(
                type=CapabilityType.FILE_WRITE.value,
                scope="/workspace/.coverage",
                description="Write coverage reports"
            ),
            Capability(
                type=CapabilityType.FILE_WRITE.value,
                scope="/workspace/htmlcov/**",
                description="Write HTML coverage reports"
            )
        ]
    
    @staticmethod
    def build_task() -> List[Capability]:
        """Capabilities for build operations."""
        return [
            Capability(
                type=CapabilityType.FILE_READ.value,
                scope="/workspace/src/**",
                description="Read source files"
            ),
            Capability(
                type=CapabilityType.FILE_WRITE.value,
                scope="/workspace/dist/**",
                description="Write build outputs"
            ),
            Capability(
                type=CapabilityType.FILE_WRITE.value,
                scope="/workspace/build/**",
                description="Write build artifacts"
            ),
            Capability(
                type=CapabilityType.EXEC_BUILD.value,
                scope="npm|webpack|vite|cargo|mvn",
                description="Run build commands"
            )
        ]
    
    @staticmethod
    def linter() -> List[Capability]:
        """Capabilities for linting."""
        return [
            Capability(
                type=CapabilityType.FILE_READ.value,
                scope="/workspace/**",
                description="Read files for linting"
            ),
            Capability(
                type=CapabilityType.EXEC_LINT.value,
                scope="eslint|pylint|clippy|ruff",
                description="Run lint commands"
            )
        ]
    
    @staticmethod
    def database_reader() -> List[Capability]:
        """Read-only database access."""
        return [
            Capability(
                type=CapabilityType.DATABASE_READ.value,
                scope="*",
                description="Read from all database tables"
            )
        ]
    
    @staticmethod
    def database_writer() -> List[Capability]:
        """Read-write database access."""
        return [
            Capability(
                type=CapabilityType.DATABASE_READ.value,
                scope="*",
                description="Read from database"
            ),
            Capability(
                type=CapabilityType.DATABASE_WRITE.value,
                scope="ledger|bugs|sprints",
                description="Write to specific tables"
            )
        ]


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    print("=== Capability-Based Security Demo ===\n")
    
    # Create capabilities for a test runner task
    capabilities = CapabilityPresets.test_runner()
    
    print("Granted capabilities:")
    for cap in capabilities:
        print(f"  - {cap.type}: {cap.scope}")
        if cap.description:
            print(f"    {cap.description}")
    
    print("\n--- Testing capability enforcement ---\n")
    
    # Create enforcer
    enforcer = CapabilityEnforcer(
        capabilities=capabilities,
        strict_mode=True
    )
    
    # Test 1: Allowed - Read test file
    action1 = Action.file_read("/workspace/tests/test_foo.py")
    check1 = enforcer.check(action1)
    print(f"1. Read test file: {'✓ ALLOWED' if check1.granted else '✗ DENIED'}")
    print(f"   Reason: {check1.reason}")
    
    # Test 2: Allowed - Run pytest
    action2 = Action.exec_command("pytest -v", cmd_type="test")
    check2 = enforcer.check(action2)
    print(f"\n2. Run pytest: {'✓ ALLOWED' if check2.granted else '✗ DENIED'}")
    print(f"   Reason: {check2.reason}")
    
    # Test 3: DENIED - Write to source directory
    action3 = Action.file_write("/workspace/src/malicious.py")
    check3 = enforcer.check(action3, sandbox_id="test-sandbox")
    print(f"\n3. Write to src: {'✓ ALLOWED' if check3.granted else '✗ DENIED'}")
    print(f"   Reason: {check3.reason}")
    
    # Test 4: DENIED - Network access
    action4 = Action.network_http("https://evil.com/steal-data")
    check4 = enforcer.check(action4, sandbox_id="test-sandbox")
    print(f"\n4. HTTP request: {'✓ ALLOWED' if check4.granted else '✗ DENIED'}")
    print(f"   Reason: {check4.reason}")
    
    # Show violations
    print(f"\n--- Violations: {enforcer.get_violation_count()} ---\n")
    for violation in enforcer.get_violations():
        print(f"  • {violation.action.type} on {violation.action.target}")
        print(f"    Reason: {violation.reason}")
