# Contributing Guide

How to contribute to agent-homebase: adding skills, instructions, and extending the library.

---

## Why Contribute?

This library improves when real teams hit real problems. Every contribution—whether a new skill, a bug fix, or better docs—helps hundreds of projects ship cleaner agent workflows.

**What makes a good contribution:**
- 🐛 **Bug fixes** — Found an edge case? Fix it.
- 📝 **Documentation** — Clarify something that confused you.
- 🎯 **New skills** — Built a useful agent pattern? Share it.
- ⚡ **Performance** — Made something faster? PR it.

No contribution is too small. Typo fixes welcome.

---

## Getting Started

```bash
# Clone the repository
git clone https://github.com/j78f88/agent-homebase.git
cd agent-homebase

# One-time: install the commit-message hook (rejects BOM + enforces
# Conventional Commits). Works on Linux, macOS, and Git Bash on Windows.
git config core.hooksPath .githooks

# Run the canonical smoke test (installs deps, builds, runs tests).
#   Linux/macOS:
./scripts/smoke-test.sh
#   Windows (PowerShell):
.\scripts\smoke-test.ps1
```

The same `smoke-test.{sh,ps1}` script is what `.github/workflows/release.yml`
runs in CI on every push, PR, and tag — so a green local smoke test
means a green CI run.

---

## Project Structure

```
agent-homebase/
├── skills/              # Agent skill definitions ({name}.skill.md)
├── instructions/        # Governance rules
│   ├── generic/         # Cross-project standards
│   └── configurable/    # Project-specific (uses {{tokens}})
├── src/                 # Python implementation
│   ├── phase1_verification/
│   ├── phase2_durability/
│   ├── phase3_isolation/
│   └── phase4_determinism/
├── schemas/             # JSON Schema definitions
├── tests/               # Test suites
└── docs/                # Documentation
```

---

## Adding a New Skill

### 1. Create Skill Directory

```bash
mkdir skills/my-skill
```

### 2. Create {name}.skill.md

```bash
# File: skills/my-skill/my-skill.skill.md
```

```markdown
---
name: my-skill
description: One sentence describing what this skill does.
when_to_use: "Keywords that trigger this skill: my task, do thing"
---

# My Skill

You are a [role description]. Your purpose is to [what you do].

## Core Constraints

1. **Constraint 1**: Description
2. **Constraint 2**: Description

## Shared Rules

This agent reads and follows:

- `{{paths.instructions_dir}}/severity-levels.instructions.md`
- `{{paths.instructions_dir}}/commit-conventions.instructions.md`

## Workflow

### Step 1: [Name]

1. Action 1
2. Action 2

### Step 2: [Name]

...

## Output Format

Return a Tier [1/2/3] response:

```json
{
  "tier": 1,
  "agent": "my-skill",
  "status": "complete",
  "summary": "...",
  "findings": []
}
```
```

### 3. Frontmatter Requirements

| Field | Required | Description |
|-------|----------|-------------|
| `name` | ✅ | Skill identifier (lowercase, hyphens) |
| `description` | ✅ | One sentence describing purpose |
| `when_to_use` | ✅ | Keywords/phrases that invoke the skill |
| `agents` | ○ | List of subagents this skill can invoke |
| `applyTo` | ○ | File patterns where skill applies |

### 4. Test Your Skill

```bash
# Run token substitution
python3 init.py --config profiles/react-web-app.config.yml

# Verify resolved skill (output is always SKILL.md per VS Code convention)
cat resolved/skills/my-skill/SKILL.md

# Check for unresolved tokens
grep -r "{{" resolved/skills/my-skill/ && echo "ERROR: Unresolved tokens"
```

---

## Adding a New Instruction

### Generic Instruction (No Configuration)

```bash
# Create in generic/
cat > instructions/generic/my-rule.instructions.md << 'EOF'
---
name: my-rule
description: Enforces [what rule]
when_to_use: "Applied when [condition]"
applyTo: "**/*.md"
---

# My Rule

## Overview

[Description of what this rule enforces]

## Requirements

1. **Requirement 1**: Description
2. **Requirement 2**: Description

## Examples

### Good

```
[Example of compliant content]
```

### Bad

```
[Example of non-compliant content]
```
EOF
```

### Configurable Instruction (Uses Tokens)

```bash
# Create in configurable/
cat > instructions/configurable/my-config.instructions.md << 'EOF'
---
name: my-config
description: Project-specific [what]
when_to_use: "Applied when [condition]"
applyTo: "{{paths.some_path}}/**"
---

# My Config

Threshold is set to {{quality.some_threshold}}.
Command to run: `{{commands.some_command}}`
EOF
```

### Register Tokens in Config

If your instruction uses new tokens, add them to `config/project.config.example.yml`:

```yaml
quality:
  some_threshold: 80  # Add new config key

commands:
  some_command: "npm run something"  # Add new command
```

---

## Adding Tests

### Test File Naming

- `test_<feature>.py` for feature tests
- `test_<phase>.py` for phase tests

### Test Structure

```python
"""
Test for [feature].

Run with: pytest tests/test_myfeature.py -v
"""

import pytest


class TestMyFeature:
    """Tests for MyFeature."""
    
    @pytest.fixture
    def instance(self):
        """Create test instance."""
        return MyFeature()
    
    def test_happy_path(self, instance):
        """Test normal operation."""
        result = instance.do_thing("valid input")
        assert result.success
    
    def test_error_handling(self, instance):
        """Test error case."""
        with pytest.raises(ValueError):
            instance.do_thing("invalid input")
    
    def test_edge_case(self, instance):
        """Test boundary condition."""
        result = instance.do_thing("")
        assert result.empty
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_myfeature.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

---

## Contribution Checklist

Before submitting a PR:

- [ ] **Tests pass**: `pytest tests/ -v`
- [ ] **No unresolved tokens**: `grep -r "{{" resolved/`
- [ ] **Documentation updated**: Update relevant docs in `docs/`
- [ ] **CHANGELOG updated**: Add entry to `CHANGELOG.md`
- [ ] **Code style**: Follow existing patterns
- [ ] **Commit messages**: Follow `commit-conventions.instructions.md`

---

## Commit Message Format

```
<type>: <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `chore`: Maintenance tasks

Examples:
```
feat: add @perf skill for performance audits

docs: update ONBOARDING.md with verification step

fix: resolve token substitution for nested paths
```

---

## Pull Request Process

1. **Fork and branch**: Create feature branch from `main`
2. **Make changes**: Follow guidelines above
3. **Test locally**: Run full test suite
4. **Submit PR**: Describe changes, link related issues
5. **Address review**: Respond to feedback
6. **Merge**: Maintainer merges after approval

### PR Description Template

```markdown
## Summary

[Brief description of changes]

## Changes

- [Change 1]
- [Change 2]

## Testing

- [ ] All tests pass
- [ ] New tests added for [feature]
- [ ] Manual testing performed

## Documentation

- [ ] Docs updated
- [ ] CHANGELOG updated

## Related Issues

Closes #[issue number]
```

---

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Document public functions with docstrings
- Maximum line length: 100 characters

### Markdown

- Use ATX headers (`#`, `##`, `###`)
- Use fenced code blocks with language specifier
- Tables for structured data
- Consistent list formatting

### YAML

- 2-space indentation
- Quote strings containing special characters
- Comment complex configurations

---

## Getting Help

- **Issues**: File bugs and feature requests on GitHub
- **Discussions**: Ask questions in GitHub Discussions
- **Documentation**: Check `docs/` for guides

---

## Cross-References

- [ARCHITECTURE.md](ARCHITECTURE.md) — Design decisions
- [INSTRUCTION_INDEX.md](INSTRUCTION_INDEX.md) — All instruction files
- [SKILL_FLOW.md](SKILL_FLOW.md) — Skill execution patterns
- [tests/README.md](../tests/README.md) — Testing guide
