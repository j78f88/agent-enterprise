# Best-Practice Alignment — Specification

> **Slug:** `best-practice-alignment`
> **Status:** DRAFT
> **Date:** 2026-05-16
> **Work packages:** 5 (`01-scaffolding` → `05-audit`)
> **Cleanup:** Delete this directory when QA.md cleanup checklist is green

---

## Sources

- External framework survey: addyosmani/agent-skills (41.9k★), multica (28.7k★), iterate (169★), evlog (1.3k★)
- Industry validation: Claude Code docs, GitHub Copilot docs, OpenAI Codex AGENTS.md, agentsmd/agents.md (21.4k★), awesome-cursorrules (39.5k★), cursor.directory
- Session research: `/memories/session/plan.md`

## Goals

1. Close the 5 confirmed gaps vs. industry convention (AGENTS.md, CLAUDE.md, honesty contract, anti-rationalization tables, red flags + verification gates)
2. Add progressive-disclosure infrastructure (`references/`) to reduce skill token weight
3. Strengthen handoff rejection actionability with structured-error fields (evlog pattern)
4. Enable multi-platform reach (Cursor `.mdc` emission, path-scoped frontmatter, lifecycle commands)
5. Validate the OPA Rego investment with concrete data

## Why This Plan

agent-homebase is architecturally well-differentiated (compilation step, tiered subagent contracts, write permits, OPA policies). Research found 5 concrete gaps vs. industry convention that reduce adoption surface and agent adherence. Work packages are ordered low-risk first, code-changes last.

## Dependencies

```
01-scaffolding: All items independent (parallel-safe, no code changes)

02-skills: All 13 skills edited
  - Apply anti-rationalization (1.4) first, then red flags (1.5) to avoid merge conflicts
  - Extension guide update (in 01) should happen before or after, not during

03-formats: Both items standalone, no dependency on 01 or 02

04-platform: init.py code changes
  - 3.1 path-scoped frontmatter → must land before 3.2 cursor emission (reuses scope field)
  - 3.3 lifecycle commands → standalone
  - 3.4 session-start hook → standalone

05-audit: Read-only. Can run anytime.
```

## Baseline (pre-work snapshot)

| Metric | Value |
|--------|-------|
| Tests | 120 passed, 14 skipped, 0 failed |
| Skills | 13 `.skill.md` (102–610 lines) |
| Resolved agents | 13 `.agent.md` (25–60 lines, all under 200-line guideline) |
| Resolved instructions | 24 files (17–645 lines) |
| Source instructions | 14 configurable + 10 generic |
| init.py resolution | 27 resolved, 10 copied, 13 agents, 2 expected token warnings |
| Anti-rationalization tables | 0/13 skills |
| Red Flags + Verification sections | 0/13 skills |
| `AGENTS.md` / `CLAUDE.md` / `references/` / `.cursor/rules/` | None exist |

## Open Decisions

| # | Question | Recommended |
|---|----------|-------------|
| 1 | Policy audit timing | Run parallel with other work (read-only, doesn't block) |
| 2 | Slash commands | Ship as sugar over @agent invocation (low cost, familiar UX) |
| 3 | Audit signing strategy | Hash-chain (fits FILE_HASHES.md model) |
| 4 | Cursor target naming | Add `cursor` + `all` (explicit is better) |
| 5 | `when_to_use` consolidation | Keep both fields for now |

## Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Anti-rationalization tables age into noise | Medium | Medium | Review quarterly; rotate examples |
| Path-scoped frontmatter breaks init.py | High | Low | New tests cover emission; existing tests gate regression |
| `.cursor/rules/` emission adds maintenance | Low | Medium | Auto-generated; no manual upkeep |
| Lifecycle commands overlap with agent invocations | Medium | Low | Commands are thin wrappers; agents remain canonical |
| Hash-chain adds complexity to FILE_HASHES workflow | Low | Low | Verification script automates checks |

## Compliance Notes

- **No application code changes** — this plan modifies markdown skills, instructions, and Python init.py only.
- **Testing** — Phase 3/4 items that modify init.py must add corresponding tests to `tests/test_init.py`.
- **Security** — Adding `cursor`/`all` to `VALID_EDITOR_TARGETS` must update `SecurityValidator.validate_config()`.
- **Commit conventions** — One conventional commit per work package: `feat(skills): ...`, `feat(init): ...`, etc.
