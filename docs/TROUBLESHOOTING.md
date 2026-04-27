# Troubleshooting Guide

Common issues and solutions when using agent-homebase.

---

## init.py Errors

### ❌ "PyYAML not installed"

```
ERROR: PyYAML not installed. Run: pip install pyyaml
```

**Solution:** Install the required dependency:
```bash
pip install pyyaml
```

---

### ❌ "⚠ Token not found: {{some.token}}"

**Cause:** A token in a skill/instruction template has no matching config value.

**Solution:**
1. Open your `project.config.yml`
2. Search for the missing token path (e.g., `some.token` → `some: token:`)
3. Add the missing value
4. Re-run `python3 init.py --config project.config.yml`

**Example:** If `{{paths.sprints}}` is unresolved:
```yaml
paths:
  sprints: "sprints/"  # Add this line
```

---

### ❌ "SECURITY: Command not whitelisted"

```
SECURITY: Command 'rm -rf' in 'commands.cleanup' not in whitelist
```

**Cause:** The security validator blocks potentially dangerous commands.

**Solution:**
- Use only whitelisted command prefixes: `npm`, `pnpm`, `yarn`, `pip`, `pytest`, `cargo`, `go`, `dotnet`, `mvn`, `gradle`, `git`, `gh`, `make`, `eslint`, `prettier`, `tsc`, `mypy`, etc.
- If your command is safe, wrap it in a script and call the script instead

---

### ❌ "SECURITY: Path traversal detected"

```
SECURITY: Path '../../../etc/passwd' contains traversal pattern
```

**Cause:** A path in your config contains `../` or similar traversal patterns.

**Solution:** Use absolute paths from project root or relative paths without traversal:
```yaml
# Bad
paths:
  config: "../../../sensitive/config"

# Good
paths:
  config: "config/"
```

---

### ❌ "SECURITY: Secret pattern detected"

```
SECURITY: Potential secret found in config value
```

**Cause:** A config value looks like a secret (API key, password, token).

**Solution:**
- Remove secrets from `project.config.yml`
- Use environment variables instead: `${{ secrets.MY_SECRET }}`
- For local development, use `.env` files (not committed to git)

---

## Skill Invocation Issues

### ❌ Skill not responding / "agent not found"

**Possible causes:**
1. Skill files not copied to `.github/agents/`
2. Skill frontmatter has syntax errors
3. VS Code Copilot extension not recognizing the agent folder

**Solution:**
1. Verify files exist: `ls .github/agents/`
2. Re-run init and copy:
   ```bash
   cd skills-library
   python3 init.py --config project.config.yml
   cp -r resolved/skills/* ../.github/agents/
   ```
3. Reload VS Code window: `Ctrl+Shift+P` → "Reload Window"

---

### ❌ Skill uses wrong paths/commands

**Cause:** Template tokens weren't substituted (still shows `{{paths.something}}`).

**Solution:**
1. Check that `init.py` ran without warnings
2. Verify you're using files from `resolved/` not the original `skills/`
3. Re-run init.py and copy fresh output

---

### ❌ "@sprint-lead says skill X not available"

**Cause:** The skill is declared in `agents:` frontmatter but the file doesn't exist.

**Solution:**
1. Check all 11 skill folders exist: `architect`, `planner`, `sprint-lead`, `pm`, `qa`, `reviewer`, `researcher`, `bug`, `docs`, `a11y`, `perf`
2. Copy any missing skills:
   ```bash
   cp -r resolved/skills/MISSING_SKILL ../.github/agents/
   ```

---

## Quality Gate Failures

### ❌ "Gate BLOCKED: coverage below threshold"

**Cause:** Test coverage is below the configured threshold.

**Solution:**
1. Check current coverage: run your coverage command
2. Either:
   - Add tests to meet threshold
   - Lower threshold temporarily in `project.config.yml`:
     ```yaml
     quality:
       coverage_store_threshold: 60  # Was 80
     ```

---

### ❌ "Gate BLOCKED: typecheck failed"

**Solution:**
1. Run typecheck locally: `pnpm typecheck` (or your configured command)
2. Fix type errors in your code
3. Re-run the sprint

---

## Sprint State Issues

### ❌ "Invalid state transition from X to Y"

**Cause:** Your sprint tried to jump between phases out of order.

**Solution:**
1. Check your sprint's PLAN.md for the current status line
2. Sprints follow this sequence: Planning → Implementation → Quality/Review → Documentation → Shipped
3. If the sprint is in an unexpected state, manually edit the status line in PLAN.md to match reality
4. See [SKILL_FLOW.md](SKILL_FLOW.md) for the full state diagram

---

### ❌ Checkpoint restore fails

**Cause:** Checkpoint file is corrupted or incompatible.

**Solution:**
1. List available checkpoints: `ls .agent-state/checkpoints/`
2. Try an earlier checkpoint
3. If all fail, delete `.agent-state/` and restart the sprint fresh

---

## Common Mistakes

### Using wrong config file

```bash
# Wrong — uses example config
python3 init.py --config config/project.config.example.yml

# Right — uses your filled-in config
python3 init.py --config project.config.yml
```

### Copying from wrong directory

```bash
# Wrong — copies templates with {{tokens}}
cp -r skills/* ../.github/agents/

# Right — copies resolved files
cp -r resolved/skills/* ../.github/agents/
```

### Forgetting to reload VS Code

After copying new skills, VS Code may cache old versions. Reload:
- `Ctrl+Shift+P` → "Developer: Reload Window"

### Missing instruction files

Skills reference instruction files. If you only copy skills but not instructions:
```bash
cp -r resolved/instructions/* ../.github/instructions/
```

---

## Getting Help

1. **Check the logs:** `.agent-state/events.jsonl` contains detailed execution logs
2. **Security audit:** `.agent-state/security-audit.jsonl` shows blocked operations
3. **Run tests:** `pytest tests/ -v` to verify library integrity
4. **File an issue:** Include your config (redact secrets) and error output

---

## FAQ

### Q: Can I use a subset of skills?

**A:** Yes. Copy only the skill folders you need. The minimum viable set is: `planner`, `sprint-lead`, `qa`, `reviewer`, `bug`.

### Q: How do I update to a new library version?

**A:** See [ONBOARDING.md](ONBOARDING.md) § Upgrading. Your `project.config.yml` is preserved.

### Q: Why are commits not pushed in autopilot mode?

**A:** By design. Autopilot mode keeps all commits local so you can review before pushing. Run `git push origin main` when ready.

### Q: How do I disable a specific quality gate?

**A:** In your sprint's `PLAN.md`, add the gate to the "Disabled Gates" section:
```markdown
## Quality Gates
- [x] Typecheck
- [x] Lint
- [ ] E2E Tests  <!-- Disabled: no E2E for this sprint -->
```

### Q: What's the difference between configurable and generic instructions?

**A:** 
- **Generic:** Cross-project standards (commit format, security, FSM). Apply everywhere.
- **Configurable:** Project-specific behavior (backlog format, severity levels). Use your config values.

### Q: How do I add a custom skill?

**A:** See [CONTRIBUTING.md](CONTRIBUTING.md) for the skill creation guide.
