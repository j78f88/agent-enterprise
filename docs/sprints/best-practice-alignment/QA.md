# QA — Quality Gates, Success Criteria, Cleanup

## Quality Gates

Run after each work package:

- [ ] `python -m pytest tests/ -v` → all existing 120+ tests pass
- [ ] `python init.py --config config/project.config.example.yml` → same output (13 agents, 27+ resolved, 10+ copied, 2 expected token warnings)
- [ ] No new unresolved `{{tokens}}` beyond the 2 expected (`{{tokens}}` in onboarding, `{{ secrets.* }}` in security)

Run after `02-skills`:

- [ ] `(Select-String -Path skills/*/*.skill.md -Pattern "## Common Rationalizations").Count` = 13
- [ ] `(Select-String -Path skills/*/*.skill.md -Pattern "## Red Flags").Count` = 13
- [ ] `(Select-String -Path skills/*/*.skill.md -Pattern "## Verification").Count` = 13

Run after `04-platform`:

- [ ] `.cursor/rules/` populated when target includes cursor (test validates this)
- [ ] New tests in `tests/test_init.py` cover path-scoped emission and `.mdc` output

## Success Criteria

1. **AGENTS.md + CLAUDE.md exist at repo root** — any coding agent can self-orient
2. **All 13 skills have anti-rationalization tables** — grep count = 13
3. **All 13 skills have Red Flags + Verification sections** — grep count = 13 each
4. **Honesty contract deployed** — `resolved/instructions/honesty-contract.instructions.md` exists after init.py
5. **Resolved instruction count ≥ 25** (24 existing + honesty-contract)
6. **references/ folder has 4 checklists** — at least 4 skills reference them
7. **Handoff rejections include Fix + Link fields** — format updated in resolved output
8. **Hash-chain column in FILE_HASHES template** — verification script validates chain integrity
9. **Test suite stays green** — 120+ tests pass, zero regressions
10. **No new unresolved `{{tokens}}`** in resolved output beyond the 2 expected

## Smoke Test Procedure

After each work package, run:

```powershell
$env:PYTHONIOENCODING='utf-8'
python -m pytest tests/ -v
python init.py --config config/project.config.example.yml
```

Both must complete cleanly before committing.

## Cleanup Checklist

> **⛔ MANUAL ONLY — Do NOT automate or delegate deletion to any agent.**
> The repo owner deletes this directory by hand after confirming all criteria pass.

When all 5 work packages are complete and all criteria above are green:

- [ ] Verify all 10 success criteria pass
- [ ] **Owner manually deletes** `docs/sprints/best-practice-alignment/` (this entire directory)
- [ ] Commit: `chore: remove best-practice-alignment work packages (complete)`

**Deliverables that remain permanently:**
- `AGENTS.md`, `CLAUDE.md` (root)
- `instructions/generic/honesty-contract.instructions.md`
- `references/` (4 checklists)
- Updated skills (13 files with new sections)
- Updated `docs/EXTENSION_GUIDE.md`
- Updated `instructions/configurable/handoff-rejection-format.instructions.md`
- Updated `starters/FILE_HASHES.md` + `scripts/verify-hash-chain.py` + `tests/test_hash_chain.py`
- Updated `init.py` + new tests
- `prompts/` (5 lifecycle commands)
- `hooks/` (session-start hook)
- `docs/POLICY_AUDIT.md`
