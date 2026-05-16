# 04 — Multi-Platform: init.py Changes, Cursor, Prompts, Hooks

> **Depends on:** 01-scaffolding and 02-skills should be done first (this changes init.py)
> **Commit:** `feat(init): path-scoped frontmatter, cursor emission, lifecycle commands, session hook`
> **Verify:** full test suite green, new tests cover emission, `.cursor/rules/` populated when target=cursor

**⚠️ This is the only work package that modifies init.py. Tests first.**

---

## Task Group 3.1: Path-scoped frontmatter in resolved instructions

Files: `init.py`, `instructions/configurable/security-audit.instructions.md`, `instructions/configurable/commit-conventions.instructions.md`, `tests/test_init.py`

**Why:** Claude Code uses `paths:`, GitHub Copilot uses `applyTo:`, Cursor uses `globs:`. Emitting these enables platform-native scoping.

- [ ] Add optional `scope` field support to instruction frontmatter parsing in init.py
- [ ] Emit platform-appropriate frontmatter in resolved instructions based on `editor.target`: Claude Code → `paths:`, GitHub → `applyTo:`, Cursor → `globs:`
- [ ] Add `scope` field to at least 2 instruction files as proof of concept
- [ ] Add test in `tests/test_init.py` for path-scoped emission
- [ ] Verify full test suite still green (120+ tests)

---

## Task Group 3.2: `.cursor/rules/` emission target

Files: `init.py`, `config/project.config.example.yml`, `config/plugin.json`, `tests/test_init.py`

**Why:** Cursor (39.5k★ ecosystem) uses `.cursor/rules/*.mdc` files.

- [ ] Add `'cursor'` and `'all'` to `VALID_EDITOR_TARGETS` in init.py
- [ ] Update `SecurityValidator.validate_config()` to accept new targets without false positives
- [ ] Add `.mdc` emission logic: for each resolved instruction, emit `.cursor/rules/<name>.mdc` with `description`, `globs`, `alwaysApply` frontmatter
- [ ] Update `config/project.config.example.yml` to document new target options
- [ ] Update `config/plugin.json` to include `.cursor/rules/` output path
- [ ] Add test in `tests/test_init.py` validating `.mdc` output format
- [ ] Verify existing tests still pass

---

## Task Group 3.3: Lifecycle slash commands

Files: `prompts/spec.prompt.md`, `prompts/plan.prompt.md`, `prompts/build.prompt.md`, `prompts/review.prompt.md`, `prompts/ship.prompt.md`

**Why:** `/spec /plan /build /review /ship` map the dev lifecycle.

- [ ] Create `prompts/spec.prompt.md` — invokes `@pm` → `@architect` (requirements → design)
- [ ] Create `prompts/plan.prompt.md` — invokes `@planner` (design → sprint plan)
- [ ] Create `prompts/build.prompt.md` — invokes `@sprint-lead` (plan → implementation)
- [ ] Create `prompts/review.prompt.md` — invokes `@reviewer` → `@security` → `@a11y` (code → quality checks)
- [ ] Create `prompts/ship.prompt.md` — invokes `@qa` → `@docs` (validate → document → release)
- [ ] Each file under 30 lines, includes lifecycle description + agent invocation order + expected artifacts

---

## Task Group 3.4: Session-start hook for resolution freshness

Files: `hooks/session-start.sh`, `hooks/hooks.json`

**Why:** Validates resolved/ freshness at session start. Warns if source files changed since last init.py run.

- [ ] Create `hooks/session-start.sh` — compares timestamps of `skills/**/*.skill.md` and `instructions/**/*.md` against `resolved/`, warns if stale
- [ ] Create `hooks/hooks.json` registry mapping hook names to scripts
- [ ] Verify hook is executable and correctly detects stale vs fresh state

---

## Verification

```powershell
# Full test suite (including new tests)
python -m pytest tests/ -v
# Expected: 120+ original tests pass + new emission tests pass

# init.py resolves with cursor target
# (requires a temp config or test; the example config uses "both")

# Prompt files exist
(Get-ChildItem prompts/*.prompt.md).Count  # 5

# Hook files exist
Test-Path hooks/session-start.sh   # True
Test-Path hooks/hooks.json         # True
```
