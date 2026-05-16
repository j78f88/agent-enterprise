# Customization Guide

How to customize agent-homebase for your project: tuning skills, overriding defaults, and extending capabilities.

---

## Quick Reference: What Do You Want to Do?

| Scenario | Section |
|:---------|:--------|
| "Tests keep failing the coverage gate" | [Tuning Quality Thresholds](#tuning-quality-thresholds) |
| "Backlog items never escalate" | [Customizing Escalation Rules](#customizing-escalation-rules) |
| "Need different settings per sprint" | [Sprint Overrides](#gate-behavior) |
| "Want to add my own commands" | [Custom Commands](#custom-commands) |
| "Starting a new project type" | [Using Profiles](#using-profiles) |
| "VS Code vs Claude Code setup" | [Platform Selection](#platform-selection) |

---

## Configuration Hierarchy

Settings cascade from defaults to project-specific:

```
Library defaults (hardcoded)
    ↓
Profile defaults (profiles/*.config.yml)
    ↓
Project config (project.config.yml)  ← You edit this
    ↓
Sprint overrides (PLAN.md)
```

> **Documenting tokens in skill or instruction prose.** When source text
> needs to reference a `{{token}}` literally (in a checklist item,
> example, or troubleshooting note), wrap it in Markdown backticks:
> `` `{{paths.bug_backlog}}` ``. The `init.py` detector treats backticked
> tokens as documentation — they are not substituted, not warned about,
> and pass through to the resolved output unchanged. GitHub Actions
> `${{ secrets.* }}` is also recognised as non-template syntax (the
> leading `$` is the signal) and skipped on the same basis.

---

## Project Identity

These tokens customize how agents identify themselves:

```yaml
project:
  name: "My Awesome App"      # Used in all agent prompts (e.g., "You are the QA specialist for My Awesome App")
  language: "TypeScript"      # Primary language
  framework: "React + Vite"   # Framework stack
  namespace: "@myorg"         # Monorepo package namespace

git:
  repo: "owner/my-repo"       # GitHub repository for CI checks (e.g., gh run list --repo owner/my-repo)
  main_branch: "main"         # Production branch
  develop_branch: "develop"   # Integration branch
```

Run `python3 init.py --quick-setup` for an interactive prompt that sets these values.

---

## Platform Selection

Control what `init.py` generates with `editor.target`:

```yaml
editor:
  target: "both"   # "vscode" | "claude-code" | "both"
```

| Value | Skills | Agent Wrappers | Instructions |
|:------|:-------|:---------------|:-------------|
| `"both"` (default) | ✅ Generated | ✅ Generated | ✅ Generated |
| `"vscode"` | ✅ Generated (non-invocable) | ✅ Generated | ✅ Generated |
| `"claude-code"` | ✅ Generated | ❌ Skipped | ✅ Generated |

**VS Code agent wrappers** are thin `.agent.md` files with:
- **Tool restrictions** — `reviewer` gets `[read, search]` only, enforced via frontmatter
- **Subagent delegation** — `sprint-lead` declares `agents: [qa, a11y, perf, reviewer, docs]`
- **Handoff hints** — `planner` declares `handoffs: [sprint-lead]`

Skills remain the canonical source. Agent bodies reference `skills/<name>/SKILL.md` for detailed procedures.

### Customizing Agent Metadata

Each skill's `agent:` block in its `{name}.skill.md` frontmatter controls the generated wrapper:

```yaml
agent:
  tools: [read, search, edit]    # VS Code tool restrictions
  agents: []                      # Named subagents this agent can invoke
  model: null                     # Model override (or null for default)
  handoffs: [sprint-lead]         # Agents this one hands off to
```

To change tool restrictions, edit the source `skills/<name>/<name>.skill.md` and re-run `init.py`.

---

## Tuning Quality Thresholds

### Coverage Thresholds

```yaml
# project.config.yml
quality:
  coverage_store_threshold: 85     # Library/store packages
  coverage_web_threshold: 70       # Web/UI components
```

Lower thresholds for legacy code, higher for critical paths.

### Gate Behavior

In sprint `PLAN.md`, disable gates per-sprint:

```markdown
## Quality Gates

- [x] Typecheck
- [x] Lint
- [x] Unit Tests
- [ ] E2E Tests      <!-- Disabled: infrastructure changes only -->
- [ ] Accessibility  <!-- Disabled: no UI changes -->
```

---

## Customizing Escalation Rules

### Deferral Thresholds

```yaml
# project.config.yml
escalation:
  def_p0_threshold: 3     # Deferrals before mandatory P0
  def_kill_threshold: 5   # Deferrals before must-kill
  age_stale_sprints: 10   # Sprints before stale warning
```

**Aggressive (fast-moving project)**:
```yaml
escalation:
  def_p0_threshold: 2
  def_kill_threshold: 3
  age_stale_sprints: 5
```

**Relaxed (stable project)**:
```yaml
escalation:
  def_p0_threshold: 5
  def_kill_threshold: 8
  age_stale_sprints: 20
```

### Sprint Composition

```yaml
escalation:
  sprint_size_min: 4          # Minimum items per sprint
  sprint_size_max: 8          # Maximum items per sprint
  feature_cap_percent: 70     # Max % features (rest is bugs/debt)
  debt_min_allocation_percent: 20  # Minimum % for technical debt
```

---

## Skill-Level Customization

### Disabling Skills

Remove skill folders from `.github/agents/` to disable:

```bash
# Disable performance audits
rm -rf .github/agents/perf/

# Disable accessibility audits
rm -rf .github/agents/a11y/
```

### Skill-Specific Configuration

Some skills read configuration sections:

```yaml
# @perf reads these
quality:
  bundle_warning_kb: 150
  bundle_critical_kb: 400
  build_warning_seconds: 45

# @a11y uses default WCAG 2.1 AA (not configurable yet)
```

---

## Command Customization

### Override All Commands

```yaml
commands:
  install: "pnpm install"
  dev: "pnpm dev"
  test: "pnpm test"
  typecheck: "pnpm typecheck"
  lint: "pnpm lint"
  build: "pnpm build"
  e2e: "pnpm test:e2e"
  coverage: "pnpm test:coverage"
```

### Per-Package Commands

For monorepos with different commands per package:

```yaml
commands:
  coverage_store: "pnpm --filter @myorg/store test:coverage"
  coverage_web: "pnpm --filter @myorg/web test:coverage"
```

### Cross-Platform Timestamps

```yaml
commands:
  # Unix/macOS
  timestamp: "date -u +\"%Y-%m-%dT%H:%M:%SZ\""
  
  # Windows PowerShell
  # timestamp: "powershell -Command \"Get-Date -Format o\""
```

---

## Path Customization

### Standard Paths

```yaml
paths:
  sprints: "sprints/"                    # Sprint folders
  sprints_doc: "SPRINTS.md"              # Sprint tracking
  backlog_ledger: "docs/planning/BACKLOG_LEDGER.md"
  bug_backlog: "docs/planning/BUG_BACKLOG.md"
```

### Alternative Layouts

**Flat structure**:
```yaml
paths:
  sprints: "planning/sprints/"
  backlog_ledger: "planning/BACKLOG.md"
  bug_backlog: "planning/BUGS.md"
```

**Monorepo with multiple products**:
```yaml
paths:
  sprints: "products/main-app/sprints/"
  backlog_ledger: "products/main-app/planning/BACKLOG_LEDGER.md"
```

---

## Extending Capability Presets

### Custom Sandbox Preset

```python
# In your project's setup
from src.phase3_isolation.capabilities import CapabilityPreset, FileCapability

MY_PRESET = CapabilityPreset(
    name="my-project-tests",
    capabilities=[
        FileCapability(action="read", path="**/*"),
        FileCapability(action="write", path="coverage/**"),
        FileCapability(action="write", path="test-results/**"),
    ],
    limits=ResourceLimits(
        max_memory_mb=4096,  # Tests need more memory
        max_execution_seconds=1800  # 30 min for slow tests
    )
)

CapabilityPreset.register("my-project-tests", MY_PRESET)
```

### Using in Config

```yaml
sandbox:
  default_preset: "my-project-tests"
```

---

## Error Recovery Configuration

### Retry Behavior

```yaml
workflow:
  max_retries: 3              # Retry failed tasks up to 3 times
  retry_backoff_base: 2       # Exponential backoff base (seconds)
  retry_backoff_max: 60       # Maximum backoff (seconds)
```

### Gate Failure Handling

```yaml
gates:
  on_failure: "block"         # block | warn | skip
  allow_skip_gates:           # Gates that can be skipped
    - "e2e"
    - "a11y"
```

---

## Observability Customization

### Enable Full Tracing

```yaml
observability:
  enabled: true
  backend: "jaeger"
  endpoint: "http://localhost:4318"
  sample_rate: 1.0            # Trace everything
  log_level: "debug"
```

### Production Settings

```yaml
observability:
  enabled: true
  backend: "honeycomb"
  endpoint: "https://api.honeycomb.io"
  sample_rate: 0.1            # 10% sampling
  log_level: "warn"
  cost_tracking: true
```

### Disable Observability

```yaml
observability:
  enabled: false
```

---

## Security Customization

### Strict Mode

```yaml
security:
  command_whitelist_enforced: true
  path_validation: true
  secret_scanning: true

determinism:
  strict_mode: true           # Enforce temperature=0
```

### Development Mode

```yaml
security:
  command_whitelist_enforced: false  # Allow any command
  secret_scanning: false             # Don't scan for secrets

determinism:
  strict_mode: false          # Allow temperature > 0
```

---

## Profile-Based Configuration

### Creating a Custom Profile

```yaml
# profiles/my-team.config.yml

# Inherit from existing profile
_extends: "react-web-app"

# Override specific settings
quality:
  coverage_store_threshold: 90   # Higher standards

escalation:
  def_p0_threshold: 2            # More aggressive

team:
  cto_name: "Team Lead Name"     # Used in approval markers and skill personalization
```

### Using Profiles

```bash
# Start from profile
cp profiles/my-team.config.yml project.config.yml

# Or merge profiles
python3 init.py --config profiles/my-team.config.yml --merge project.config.yml
```

---

## Instruction Overrides

### Adding Project-Specific Instructions

Create custom instructions in your project:

```bash
# Create in your project (not the library)
cat > .github/instructions/my-rule.instructions.md << 'EOF'
---
name: my-project-rule
description: Project-specific coding standards
applyTo: "src/**/*.ts"
---

# My Project Rules

1. Always use named exports
2. Prefer functional components
3. No default exports except for pages
EOF
```

### Overriding Library Instructions

Copy and modify an instruction:

```bash
# Copy library instruction to project
cp skills-library/resolved/instructions/commit-conventions.instructions.md \
   .github/instructions/commit-conventions.instructions.md

# Edit with your conventions
code .github/instructions/commit-conventions.instructions.md
```

---

## Environment-Specific Config

### Using Environment Variables

```yaml
platform:
  test_url: "${TEST_URL:-https://staging.example.com}"
  prod_url: "${PROD_URL:-https://example.com}"
```

### Separate Config Files

```bash
# Development
python3 init.py --config project.config.dev.yml

# Production
python3 init.py --config project.config.prod.yml
```

---

## Cross-References

- [ONBOARDING.md](ONBOARDING.md) — Initial setup
- [ARCHITECTURE.md](ARCHITECTURE.md) — Why these options exist
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Configuration issues
- [config/project.config.example.yml](../config/project.config.example.yml) — Full option reference
