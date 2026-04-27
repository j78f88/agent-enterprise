# Security Policies - Rego Rules for Command and Config Validation
#
# These policies enforce security rules from security-model.instructions.md
# Run with: opa eval -d policies/ -i config.json data.security

package security

# ==============================================================================
# Command Whitelist
# ==============================================================================

# Allowed command prefixes
allowed_commands := {
    # Package managers
    "npm", "pnpm", "yarn", "pip", "cargo", "go", "dotnet", "mvn", "gradle",
    # Test runners
    "pytest", "jest", "vitest", "mocha", "cargo test",
    # Linters & formatters
    "eslint", "prettier", "ruff", "black", "flake8",
    # Type checkers
    "tsc", "mypy", "pyright",
    # Version control
    "git", "gh",
    # Build tools
    "make", "cmake",
    # Utilities
    "echo", "cat", "ls", "pwd", "date"
}

# Dangerous patterns that should NEVER appear
dangerous_patterns := [
    # Command chaining
    "; rm", "&& rm", "| rm",
    # Command substitution
    "`", "$(", "$(",
    # Device writes
    "> /dev/",
    # Curl/wget pipes
    "curl.*|.*sh", "wget.*|.*sh",
    # Destructive operations
    "rm -rf /", "dd if=", "mkfs",
    # Privilege escalation
    "sudo", "su -",
    # Network backdoors
    "nc -l", "ncat -l",
    # Eval/exec
    "eval", "exec"
]

# Violation: Command not in whitelist
violation[msg] {
    cmd := input.commands[key]
    
    # Extract command prefix (first word)
    parts := split(cmd, " ")
    prefix := parts[0]
    
    # Check if prefix is allowed
    not allowed_commands[prefix]
    
    msg := sprintf(
        "COMMAND_WHITELIST: Command '%s' in '%s' not in whitelist. Prefix '%s' not allowed.",
        [cmd, key, prefix]
    )
}

# Violation: Dangerous pattern detected
violation[msg] {
    cmd := input.commands[key]
    pattern := dangerous_patterns[_]
    
    # Check if pattern appears in command
    regex.match(pattern, cmd)
    
    msg := sprintf(
        "DANGEROUS_PATTERN: Command '%s' in '%s' matches dangerous pattern '%s'",
        [cmd, key, pattern]
    )
}

# ==============================================================================
# Path Validation
# ==============================================================================

# Violation: Path traversal attempt
violation[msg] {
    path := input.paths[key]
    
    # Check for path traversal patterns
    path_traversal_patterns := ["../", "..\\", "/..", "\\..", "/./", "\\.\\"]
    pattern := path_traversal_patterns[_]
    contains(path, pattern)
    
    msg := sprintf(
        "PATH_TRAVERSAL: Path '%s' in '%s' contains traversal pattern '%s'",
        [path, key, pattern]
    )
}

# Violation: Absolute path outside workspace
violation[msg] {
    path := input.paths[key]
    
    # Check for absolute paths
    is_absolute_path(path)
    
    # Ensure it's within allowed roots
    not is_allowed_absolute_path(path)
    
    msg := sprintf(
        "ABSOLUTE_PATH: Path '%s' in '%s' is absolute and outside allowed roots",
        [path, key]
    )
}

# Helper: Check if path is absolute
is_absolute_path(path) {
    # Unix absolute path
    startswith(path, "/")
}

is_absolute_path(path) {
    # Windows absolute path
    regex.match("^[A-Za-z]:\\\\", path)
}

# Helper: Check if absolute path is in allowed roots
is_allowed_absolute_path(path) {
    allowed_roots := ["/tmp", "/var/tmp", "C:\\Temp"]
    root := allowed_roots[_]
    startswith(path, root)
}

# ==============================================================================
# Secret Detection
# ==============================================================================

secret_patterns := [
    # API keys
    "AKIA[0-9A-Z]{16}",                    # AWS Access Key
    "api[_-]?key[\"'\\s]*[:=][\"'\\s]*[A-Za-z0-9_\\-]{20,}",
    # Tokens
    "ghp_[A-Za-z0-9_]{36}",                # GitHub Personal Access Token
    "gho_[A-Za-z0-9_]{36}",                # GitHub OAuth Token
    "[\"'][A-Za-z0-9_\\-]{32,}[\"']",      # Generic token
    # Passwords
    "password[\"'\\s]*[:=][\"'\\s]*[A-Za-z0-9!@#$%^&*()_+\\-=\\[\\]{};':\"\\\\|,.<>\\/?]{8,}",
    # Private keys
    "-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----"
]

# Violation: Secret detected in config
violation[msg] {
    # Check all string values in config
    value := object.get(input, key, "")
    is_string(value)
    
    pattern := secret_patterns[_]
    regex.match(pattern, value)
    
    msg := sprintf(
        "SECRET_DETECTED: Potential secret in '%s' matches pattern '%s'. Use environment variables.",
        [key, pattern]
    )
}

# ==============================================================================
# Escalation Thresholds
# ==============================================================================

# Warning: High escalation thresholds
warning[msg] {
    threshold := input.escalation.def_kill_threshold
    threshold > 10
    
    msg := sprintf(
        "ESCALATION_THRESHOLD: def_kill_threshold is %d (> 10). High threshold may hide systemic issues.",
        [threshold]
    )
}

# ==============================================================================
# Validation Summary
# ==============================================================================

# Policy passes if no violations
allow {
    count(violation) == 0
}

# Detailed result
result = {
    "allow": allow,
    "violations": violation,
    "warnings": warning,
    "summary": {
        "violation_count": count(violation),
        "warning_count": count(warning)
    }
}
