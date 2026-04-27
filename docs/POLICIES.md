# Policies Guide

How Rego policies enforce business rules in agent-homebase.

---

## Overview

agent-homebase uses [Open Policy Agent (OPA)](https://www.openpolicyagent.org/) Rego policies to enforce:

- **Composition rules**: Sprint planning constraints
- **Security rules**: Command and path validation

---

## Policy Files

| File | Package | Purpose |
|------|---------|---------|
| `policies/composition.rego` | `composition` | Sprint composition constraints |
| `policies/security.rego` | `security` | Command whitelist, path validation |

---

## Composition Policy

### Priority Ordering

Items must be ordered by priority tier (P0 before P1 before P2...):

```rego
violation[msg] {
    i := input.composition[_]
    j := input.composition[_]
    i.index < j.index
    priority_value(i.tier) > priority_value(j.tier)
    
    msg := sprintf(
        "PRIORITY_ORDER: %s (tier %s) appears before %s (tier %s)",
        [i.itemId, i.tier, j.itemId, j.tier]
    )
}
```

**Example violation**:
```json
{
  "composition": [
    {"index": 0, "itemId": "ITEM-002", "tier": "P1"},
    {"index": 1, "itemId": "ITEM-001", "tier": "P0"}  // P0 should come first!
  ]
}
```

### Score Ordering Within Tier

Within the same tier, higher scores come first:

```rego
violation[msg] {
    i := input.composition[_]
    j := input.composition[_]
    i.index < j.index
    i.tier == j.tier
    i.score < j.score  // Lower score before higher = violation
    
    msg := sprintf(
        "SCORE_ORDER: Within tier %s, %s (score %v) appears before %s (score %v)",
        [i.tier, i.itemId, i.score, j.itemId, j.score]
    )
}
```

### Feature/Bug Balance

Sprint must maintain 50-80% feature allocation:

```rego
violation[msg] {
    input.constraints.featurePercent < 50
    msg := sprintf("FEATURE_BALANCE: %v%% features, must be >= 50%%", [input.constraints.featurePercent])
}

violation[msg] {
    input.constraints.featurePercent > 80
    msg := sprintf("FEATURE_BALANCE: %v%% features, must be <= 80%%", [input.constraints.featurePercent])
}
```

### Capacity Constraints

Sprint cannot exceed 100% capacity:

```rego
violation[msg] {
    input.constraints.capacityUsed > 100
    msg := sprintf("CAPACITY_EXCEEDED: %v%% used (max 100%%)", [input.constraints.capacityUsed])
}
```

---

## Security Policy

### Command Whitelist

Only approved command prefixes are allowed:

```rego
allowed_commands := {
    "npm", "pnpm", "yarn", "pip", "pytest", "cargo", "go", "dotnet",
    "mvn", "gradle", "git", "gh", "make", "eslint", "prettier", "tsc", "mypy"
}

violation[msg] {
    cmd := input.commands[key]
    parts := split(cmd, " ")
    prefix := parts[0]
    not allowed_commands[prefix]
    
    msg := sprintf("COMMAND_WHITELIST: '%s' not allowed", [prefix])
}
```

### Dangerous Patterns

Commands containing dangerous patterns are blocked:

```rego
dangerous_patterns := [
    "; rm", "&& rm", "| rm",  // Command chaining with rm
    "`", "$(", "$(",          // Command substitution
    "curl.*|.*sh",            // Curl pipe to shell
    "rm -rf /",               // Recursive delete root
    "sudo", "su -"            // Privilege escalation
]

violation[msg] {
    cmd := input.commands[key]
    pattern := dangerous_patterns[_]
    regex.match(pattern, cmd)
    
    msg := sprintf("DANGEROUS_PATTERN: '%s' matches '%s'", [cmd, pattern])
}
```

### Path Validation

Paths cannot contain traversal patterns:

```rego
violation[msg] {
    path := input.paths[key]
    traversal_patterns := ["../", "..\\", "/..", "\\.."]
    pattern := traversal_patterns[_]
    contains(path, pattern)
    
    msg := sprintf("PATH_TRAVERSAL: '%s' contains '%s'", [path, pattern])
}
```

---

## Running Policies

### With OPA CLI

```bash
# Install OPA
brew install opa  # macOS
# or download from https://www.openpolicyagent.org/docs/latest/#running-opa

# Evaluate composition policy
opa eval -d policies/composition.rego -i input.json data.composition.violation

# Evaluate security policy
opa eval -d policies/security.rego -i config.json data.security.violation
```

### With Python

```python
from src.phase1_verification.policy_engine import PolicyEngine

engine = PolicyEngine()

# Check composition
result = engine.evaluate("composition", {
    "composition": [...],
    "constraints": {"featurePercent": 75, "capacityUsed": 90}
})

if result.violations:
    for v in result.violations:
        print(f"VIOLATION: {v}")
```

---

## Input Formats

### Composition Input

```json
{
  "composition": [
    {
      "index": 0,
      "itemId": "ITEM-001",
      "tier": "P0",
      "score": 8.5,
      "type": "feature"
    },
    {
      "index": 1,
      "itemId": "ITEM-002",
      "tier": "P1",
      "score": 7.0,
      "type": "bug"
    }
  ],
  "constraints": {
    "featurePercent": 60,
    "bugPercent": 40,
    "capacityUsed": 85,
    "sprintSize": 6
  }
}
```

### Security Input

```json
{
  "commands": {
    "test": "pnpm test",
    "build": "pnpm build",
    "lint": "eslint src/"
  },
  "paths": {
    "sprints": "sprints/",
    "backlog": "docs/planning/BACKLOG_LEDGER.md",
    "output": "dist/"
  }
}
```

---

## Extending Policies

### Adding a New Rule

1. Edit the policy file (`policies/composition.rego` or `policies/security.rego`)
2. Add a new `violation[msg]` or `warning[msg]` rule
3. Test with sample input
4. Update this documentation

### Example: Max Sprint Size

```rego
# Add to composition.rego

violation[msg] {
    input.constraints.sprintSize > 10
    
    msg := sprintf(
        "SPRINT_SIZE: %v items exceeds maximum of 10",
        [input.constraints.sprintSize]
    )
}
```

### Example: Required Prefix

```rego
# Add to security.rego

violation[msg] {
    path := input.paths[key]
    not startswith(path, "docs/")
    not startswith(path, "src/")
    key == "user_facing"  # Only apply to user_facing paths
    
    msg := sprintf(
        "PATH_PREFIX: %s '%s' must start with docs/ or src/",
        [key, path]
    )
}
```

---

## Testing Policies

### Unit Tests

```rego
# policies/composition_test.rego

package composition

test_priority_order_valid {
    not violation with input as {
        "composition": [
            {"index": 0, "itemId": "A", "tier": "P0", "score": 5},
            {"index": 1, "itemId": "B", "tier": "P1", "score": 5}
        ],
        "constraints": {"featurePercent": 60, "capacityUsed": 80}
    }
}

test_priority_order_invalid {
    violation with input as {
        "composition": [
            {"index": 0, "itemId": "A", "tier": "P1", "score": 5},
            {"index": 1, "itemId": "B", "tier": "P0", "score": 5}
        ],
        "constraints": {"featurePercent": 60, "capacityUsed": 80}
    }
}
```

### Running Tests

```bash
opa test policies/ -v
```

---

## Troubleshooting

### "undefined function"

```
1 error occurred: policies/composition.rego:15: rego_type_error: undefined function data.common.helper
```

**Solution**: Check imports and ensure referenced packages exist.

### "no match found"

Policy returns empty result when violations exist.

**Solution**: Verify input matches expected schema. Use `opa eval --explain=full` for debugging.

### Performance Issues

Complex policies on large inputs can be slow.

**Solution**: 
- Add early termination conditions
- Index frequently accessed data
- Profile with `opa eval --profile`

---

## Cross-References

- [ARCHITECTURE.md](ARCHITECTURE.md) — Why Rego was chosen
- [INSTRUCTION_INDEX.md](INSTRUCTION_INDEX.md) — `composition-rules.instructions.md`
- [tests/test_contracts.py](../tests/test_contracts.py) — Policy integration tests
