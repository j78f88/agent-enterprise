# Adoption Plan: Industry Best-Practice Alignment

> **Slug:** `best-practice-alignment`
> **Status:** DRAFT
> **Date:** 2026-05-16
> **Handoff to:** `@sprint-lead` (Phase 1 first, then phases 2–4 as sequential sprints)

---

## Sources

Every upstream artifact this plan drew from:

- `research/best-practice-round-1` — External framework survey (addyosmani/agent-skills 41.9k★, multica 28.7k★, iterate 169★, evlog 1.3k★)
- `research/best-practice-round-2` — Industry best-practice validation (Claude Code docs, GitHub Copilot docs, OpenAI Codex AGENTS.md, agentsmd/agents.md 21.4k★, awesome-cursorrules 39.5k★, addyosmani skill-anatomy.md, cursor.directory)
- Session research artifact: `/memories/session/plan.md`

## Goals

1. Close the 5 confirmed gaps between agent-homebase and industry convention (AGENTS.md, CLAUDE.md, honesty contract, anti-rationalization tables, red flags + verification gates)
2. Add progressive-disclosure infrastructure (`references/` folder) to reduce skill token weight
3. Strengthen handoff rejection actionability with structured-error fields from evlog patterns
4. Enable multi-platform reach (Cursor `.mdc` emission, path-scoped frontmatter, lifecycle commands)
5. Validate the OPA Rego investment with concrete data

## Why This Plan

agent-homebase is architecturally well-differentiated (compilation step, tiered subagent contracts, write permits, OPA policies). However, research rounds 1 and 2 found 5 concrete gaps vs. industry convention that reduce adoption surface and agent adherence. Phase 1 items are all zero-risk, parallel-safe, and close the most visible gaps. Phases 2–4 build on the foundation.

## Dependencies

```
Phase 1: All items independent (parallel-safe)
  1.4 anti-rationalization ─┐
  1.5 red flags + verification ─┤─ both edit skill files; apply 1.4 first, then 1.5 to avoid merge conflicts
  1.7 extension guide ──────────┘─ should reflect 1.4 + 1.5 format in template

Phase 2:
  2.1 handoff rejection fields → standalone
  2.2 hash-chain signing → standalone (no dependency on 2.1)

Phase 3:
  3.1 path-scoped frontmatter → requires understanding of init.py instruction resolution
  3.2 cursor emission → depends on 3.1 (reuses scope field)
  3.3 lifecycle commands → standalone
  3.4 session-start hook → standalone
```

## Pre-flight Findings

| Document | Finding |
|----------|---------|
| `docs/DUAL_PLATFORM_PLAN.md` | Status: Implemented (Phases 1–7 complete). Confirms `editor.target` already supports `vscode`, `claude-code`, `both`. Phase 3 items (3.1, 3.2) must extend this — add `cursor` and `all` as new targets. No conflict. |
| `docs/EXTENSION_GUIDE.md` | Defines consumption model but has NO skill template section. Item 1.7 fills this gap. No conflict. |
| `policies/composition.rego` | Enforces priority ordering, feature/bug balance, capacity constraints. Not affected by this plan — all changes are to skills, instructions, and init.py, not composition inputs. |
| `policies/security.rego` | Enforces command whitelist, path validation, secret detection. Not affected — no new commands or paths introduced. |
| `instructions/configurable/handoff-rejection-format.instructions.md` | Current format has Reason + Proposed resolution. Item 2.1 adds Fix + Link fields. Compatible extension — no existing fields removed. |
| `starters/FILE_HASHES.md` | Current format: File, SHA-256, Last Verified, Changed By. Item 2.2 adds Prior Hash column. Compatible extension. |
| `config/plugin.json` | Lists `resolved/skills/`, `resolved/agents/`, `resolved/instructions/`. Phase 3 items adding `.cursor/rules/` should update this manifest. |
| NON_GOALS | No `NON_GOALS.md` exists in starters yet (template only). No conflict. |

## Compliance Notes

- **Factory pattern / Store versioning / ISO dates / Tailwind / TypeScript strict** — N/A: this plan modifies markdown skills, instructions, and Python init.py only. No application code changes.
- **Testing** — All phases include smoke test requirements. Phase 3 items that modify init.py must add corresponding tests to `tests/test_init.py`.
- **Security** — Phase 3.2 adds `cursor` and `all` to `VALID_EDITOR_TARGETS` — must update `SecurityValidator.validate_config()` to accept new values without false-positive errors.
- **Commit conventions** — Each phase should be committed as a single conventional commit: `feat(skills): add anti-rationalization tables`, `feat(init): add cursor emission target`, etc.

## Carry-Over Check

No existing backlog ledger in agent-homebase (this is a library repo, not a project repo). No carry-over items or escalated deferrals to account for. ✅ Clear.

---

## Baseline (pre-work snapshot)

| Metric | Value |
|--------|-------|
| Tests | 120 passed, 14 skipped, 0 failed |
| Skills | 13 `.skill.md` files (102–610 lines) |
| Resolved agents | 13 `.agent.md` files (25–60 lines) — all under 200-line guideline |
| Resolved instructions | 24 files (17–645 lines) |
| Source instructions | 14 configurable + 10 generic |
| init.py resolution | 27 resolved, 10 copied, 13 agents, 2 expected token warnings |
| Existing `references/` | ❌ Does not exist |
| Existing `AGENTS.md` | ❌ Does not exist |
| Existing `CLAUDE.md` | ❌ Does not exist |
| Existing `.cursor/rules/` | ❌ Does not exist |
| Anti-rationalization tables | ❌ 0 of 13 skills have them |
| Red Flags sections | ❌ 0 of 13 skills have them |
| Verification Gates sections | ❌ 0 of 13 skills have them |
| Honesty contract instruction | ❌ Does not exist |
| Path-scoped frontmatter | ❌ Not emitted in resolved/ |

---

## Phase 1 — Quick Wins (low risk, parallel-safe)

All items in Phase 1 are independent. They can be worked in any order or in parallel.

### Task Group 1.1: Add root `AGENTS.md`

Files: `AGENTS.md`

**Why:** All major platforms (Claude Code, GitHub Copilot, OpenAI Codex) look for `AGENTS.md` at repo root. Agents navigating agent-homebase itself currently have no entry point.

- [ ] Create `AGENTS.md` (~50 lines) at repo root
- [ ] Include: project purpose (1-line), dev setup (Python 3.12+, `pip install pyyaml`, `pip install -r requirements-dev.txt`), build command, test command, architecture summary (skills → init.py → resolved/), key directories table, PR conventions
- [ ] Verify file under 80 lines

---

### Task Group 1.2: Add `CLAUDE.md` (import from AGENTS.md)

Files: `CLAUDE.md`

**Why:** Claude Code loads `CLAUDE.md` automatically. Avoids maintaining two parallel files.

- [ ] Create `CLAUDE.md` at repo root — reference `AGENTS.md`, add Claude Code-specific notes (regeneration command, don't edit resolved/ directly)
- [ ] Verify file under 20 lines and references AGENTS.md

---

### Task Group 1.3: Add honesty contract instruction

Files: `instructions/generic/honesty-contract.instructions.md`

**Why:** Industry pattern (awesome-cursorrules 39.5k★ anti-sycophancy rule). agent-homebase has no explicit honesty/anti-hallucination contract. Security.rego catches dangerous commands but not prompt-level honesty failures.

- [ ] Create `instructions/generic/honesty-contract.instructions.md` (~40 lines) with rules: never fabricate API signatures/function names/file paths, never claim a test passes without running it, never silently skip required steps, never invent package versions, say "uncertain" when uncertain, never soften findings, never hallucinate file contents
- [ ] Verify init.py copies it to `resolved/instructions/` (generic glob handles automatically — no code change)
- [ ] Verify file under 50 lines

**Impact on init.py:** None — existing `generic_src` glob picks up new `.md` files automatically.

---

### Task Group 1.4: Add anti-rationalization tables to all 13 skills

Files: `skills/a11y/a11y.skill.md`, `skills/architect/architect.skill.md`, `skills/bug/bug.skill.md`, `skills/docs/docs.skill.md`, `skills/onboarding/onboarding.skill.md`, `skills/perf/perf.skill.md`, `skills/planner/planner.skill.md`, `skills/pm/pm.skill.md`, `skills/qa/qa.skill.md`, `skills/researcher/researcher.skill.md`, `skills/reviewer/reviewer.skill.md`, `skills/security/security.skill.md`, `skills/sprint-lead/sprint-lead.skill.md`

**Why:** addyosmani/agent-skills (41.9k★) pattern. Every skill ends with a table of common excuses agents use to skip steps, paired with counter-arguments.

- [ ] Append `## Common Rationalizations` section to each of 13 `.skill.md` files
- [ ] Use 3-column table format: Excuse | Why It's Tempting | Counter
- [ ] Each skill gets 3–5 domain-specific rationalizations (qa: "no need to check coverage"; architect: "no ADR needed"; security: "internal tool, security doesn't matter"; planner: "too small for a plan"; researcher: "I already know the answer"; etc.)
- [ ] Verify: `grep -r "Common Rationalizations" skills/ | wc -l` → 13

---

### Task Group 1.5: Add Red Flags + Verification Gates to all 13 skills

Files: `skills/a11y/a11y.skill.md`, `skills/architect/architect.skill.md`, `skills/bug/bug.skill.md`, `skills/docs/docs.skill.md`, `skills/onboarding/onboarding.skill.md`, `skills/perf/perf.skill.md`, `skills/planner/planner.skill.md`, `skills/pm/pm.skill.md`, `skills/qa/qa.skill.md`, `skills/researcher/researcher.skill.md`, `skills/reviewer/reviewer.skill.md`, `skills/security/security.skill.md`, `skills/sprint-lead/sprint-lead.skill.md`

**Why:** addyosmani/agent-skills pattern. Forces agents to produce concrete evidence before exiting.

- [ ] Append `## Red Flags` section (3+ signs per skill) after Common Rationalizations
- [ ] Append `## Verification` section (3+ checklist items per skill) after Red Flags
- [ ] Domain-specific examples — qa: "coverage decreased but not flagged", architect: "ADR has no trade-off section", security: "no dependency scan ran"
- [ ] Verify: `grep -r "## Red Flags" skills/ | wc -l` → 13
- [ ] Verify: `grep -r "## Verification" skills/ | wc -l` → 13

---

### Task Group 1.6: Create `references/` folder with cross-skill checklists

Files: `references/testing-patterns.md`, `references/security-checklist.md`, `references/accessibility-checklist.md`, `references/performance-checklist.md`, `skills/qa/qa.skill.md`, `skills/security/security.skill.md`, `skills/a11y/a11y.skill.md`, `skills/perf/perf.skill.md`

**Why:** addyosmani/agent-skills pattern ("progressive disclosure"). Checklists referenced by multiple skills should live in one place. Reduces token weight.

- [ ] Create `references/testing-patterns.md` — test structure, coverage expectations, snapshot vs assertion, integration test patterns (30–50 lines)
- [ ] Create `references/security-checklist.md` — OWASP top 10 shortlist, dependency audit steps, secret detection patterns (30–50 lines)
- [ ] Create `references/accessibility-checklist.md` — WCAG 2.1 AA quick checks, screen reader testing, color contrast (30–50 lines)
- [ ] Create `references/performance-checklist.md` — bundle size checks, render performance, database query patterns (30–50 lines)
- [ ] Add reference lines in at least 4 skills: qa → testing-patterns, security → security-checklist, a11y → accessibility-checklist, perf → performance-checklist
- [ ] Verify each file under 60 lines

---

### Task Group 1.7: Update `docs/EXTENSION_GUIDE.md` with skill template

Files: `docs/EXTENSION_GUIDE.md`

**Why:** New adopters writing custom skills need a template showing the new sections (Common Rationalizations, Red Flags, Verification).

- [ ] Append "Skill Template" section to `docs/EXTENSION_GUIDE.md`
- [ ] Template documents standard skill structure: frontmatter, identity, core constraints, workflow sections, Common Rationalizations table, Red Flags list, Verification checklist
- [ ] Include a minimal working example (~30 lines)

---

## Phase 2 — Structured Handoffs & Observability (medium effort)

### Task Group 2.1: Adopt structured-error fields for handoff rejections

Files: `instructions/configurable/handoff-rejection-format.instructions.md`

**Why:** evlog pattern. Rejections with `fix` + `link` fields are immediately actionable.

- [ ] Add `Fix` field (one-sentence actionable step) between `Reason` and `Proposed resolution` in entry format
- [ ] Add `Link` field (path to constraining doc/ADR/instruction) after `Fix`
- [ ] Update Enforcement section: add WARNING for missing `Fix` or `Link` on new entries
- [ ] Verify after init.py: resolved version includes new fields

---

### Task Group 2.2: Hash-chain signing for FILE_HASHES.md

Files: `starters/FILE_HASHES.md`, `scripts/verify-hash-chain.py`, `tests/test_hash_chain.py`

**Why:** evlog pattern. Each entry's hash chains to the prior → tamper-evident.

- [ ] Add `Prior Hash` column to FILE_HASHES table (first 8 chars of SHA-256 of prior row's hash; first entry = `GENESIS`)
- [ ] Update template comments to document chain semantics
- [ ] Create `scripts/verify-hash-chain.py` (~40 lines) — parses table, verifies chain integrity, exits non-zero on tamper
- [ ] Create `tests/test_hash_chain.py` — validates a sample chain with known-good and tampered data

---

## Phase 3 — Multi-Platform & Lifecycle (higher effort)

### Task Group 3.1: Emit path-scoped frontmatter in resolved instructions

Files: `init.py`, `instructions/configurable/security-audit.instructions.md`, `instructions/configurable/commit-conventions.instructions.md`, `tests/test_init.py`

**Why:** Claude Code uses `paths:`, GitHub Copilot uses `applyTo:`, Cursor uses `globs:`. Emitting these enables platform-native scoping.

- [ ] Add optional `scope` field support to instruction frontmatter parsing in init.py
- [ ] Emit platform-appropriate frontmatter in resolved instructions based on `editor.target`: Claude Code → `paths:`, GitHub → `applyTo:`, Cursor → `globs:`
- [ ] Add `scope` field to at least 2 instruction files as proof of concept
- [ ] Add test in `tests/test_init.py` for path-scoped emission
- [ ] Verify full test suite still green (120+ tests)

---

### Task Group 3.2: Add `.cursor/rules/` emission target to init.py

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

### Task Group 3.3: Lifecycle slash commands

Files: `prompts/spec.prompt.md`, `prompts/plan.prompt.md`, `prompts/build.prompt.md`, `prompts/review.prompt.md`, `prompts/ship.prompt.md`

**Why:** addyosmani/agent-skills pattern. `/spec /plan /build /review /ship` map the dev lifecycle.

- [ ] Create `prompts/spec.prompt.md` — invokes `@pm` → `@architect` (requirements → design)
- [ ] Create `prompts/plan.prompt.md` — invokes `@planner` (design → sprint plan)
- [ ] Create `prompts/build.prompt.md` — invokes `@sprint-lead` (plan → implementation)
- [ ] Create `prompts/review.prompt.md` — invokes `@reviewer` → `@security` → `@a11y` (code → quality checks)
- [ ] Create `prompts/ship.prompt.md` — invokes `@qa` → `@docs` (validate → document → release)
- [ ] Each file under 30 lines, includes lifecycle description + agent invocation order + expected artifacts

---

### Task Group 3.4: Session-start hook for resolution freshness

Files: `hooks/session-start.sh`, `hooks/hooks.json`

**Why:** addyosmani/agent-skills + Claude Code native hooks. Validates resolved/ freshness at session start.

- [ ] Create `hooks/session-start.sh` — compares timestamps of `skills/**/*.skill.md` and `instructions/**/*.md` against `resolved/`, warns if stale
- [ ] Create `hooks/hooks.json` registry mapping hook names to scripts
- [ ] Verify hook is executable and correctly detects stale vs fresh state

---

## Phase 4 — Validation (audit, not refactor)

### Task Group 4.1: Pressure-test OPA Rego policy catch rate

Files: `docs/POLICY_AUDIT.md`, `policies/composition.rego`, `policies/security.rego`

**Why:** OPA Rego is the most unique feature and most expensive dependency. Need ROI data.

- [ ] Audit git history: count violations flagged by `composition.rego` in CI or manual runs
- [ ] Audit git history: count violations caught by `security.rego`
- [ ] Assess false positive rate
- [ ] Document findings in `docs/POLICY_AUDIT.md` with concrete data
- [ ] Include clear recommendation: keep / simplify / fold into init.py

---

## Quality Gates

- [x] standard (pytest, lint — all existing 120 tests must pass after each phase)
- [x] init.py regression (resolution produces same output: 13 agents, 27+ resolved, 10+ copied, 2 expected token warnings)
- [ ] skill structure audit (all 13 skills have Common Rationalizations, Red Flags, Verification — after Phase 1)
- [ ] cross-platform emission (`.cursor/rules/` populated when target includes cursor — after Phase 3)

## Success Criteria

1. **AGENTS.md + CLAUDE.md exist at repo root** — any coding agent entering the repo can self-orient without reading source files
2. **All 13 skills have anti-rationalization tables** — `grep -r "Common Rationalizations" skills/ | wc -l` = 13
3. **All 13 skills have Red Flags + Verification sections** — `grep -r "## Red Flags" skills/` and `grep -r "## Verification" skills/` each = 13
4. **Honesty contract deployed** — `resolved/instructions/honesty-contract.instructions.md` exists after init.py
5. **Resolved instruction count ≥ 25** (24 existing + honesty-contract)
6. **references/ folder has 4 checklists** — at least 4 skills reference them
7. **Handoff rejections include Fix + Link fields** — format updated in resolved output
8. **Hash-chain column in FILE_HASHES template** — verification script validates chain integrity
9. **Test suite stays green** — 120+ tests pass, zero regressions
10. **No new unresolved `{{tokens}}`** in resolved output beyond the 2 expected

## Technical Notes

- **Skill file growth:** Adding Common Rationalizations (~15 lines) + Red Flags (~10 lines) + Verification (~10 lines) = ~35 lines per skill. Largest skill (security: 610 lines) grows to ~645 lines. This is fine — skills are on-demand, not always-loaded.
- **init.py no-change guarantee (Phase 1):** Items 1.1–1.6 create new files or edit skill markdown only. init.py code is NOT modified in Phase 1. The honesty-contract instruction is auto-discovered by the existing generic glob.
- **init.py changes (Phase 3 only):** Items 3.1 and 3.2 modify init.py — must add tests to `tests/test_init.py` before changing production code.
- **Backward compatibility:** All changes are additive. No existing fields removed, no existing file formats broken, no existing behavior changed.

---

## Implementation Order

```
Phase 1 (all parallel):
  1.1 AGENTS.md ─────────────────┐
  1.2 CLAUDE.md ─────────────────┤
  1.3 honesty-contract ──────────┤
  1.4 anti-rationalization ──────┼─→ Smoke test → commit
  1.5 red flags + verification ──┤
  1.6 references/ ───────────────┤
  1.7 extension guide update ────┘

Phase 2 (sequential):
  2.1 handoff rejection fields ──→ 2.2 hash-chain signing

Phase 3 (parallel within, sequential after Phase 2):
  3.1 path-scoped frontmatter ──┐
  3.2 .cursor/rules/ emission ──┼─→ Smoke test → commit
  3.3 lifecycle commands ────────┤
  3.4 session-start hook ────────┘

Phase 4 (can run anytime, read-only audit):
  4.1 OPA Rego policy audit
```

---

## Smoke Test Checklist

After each phase, verify:

1. `python -m pytest tests/ -v` → all existing tests pass (120+)
2. `python init.py --config config/project.config.example.yml` → completes without errors, same token warning count (2)
3. Resolved agent count unchanged (13)
4. Resolved instruction count ≥ 24 (grows as we add honesty-contract)
5. No new unresolved `{{tokens}}` in output (except the 2 expected: `{{tokens}}` in onboarding, `{{ secrets.* }}` in security)
6. `grep -r "Common Rationalizations" skills/ | wc -l` → 13 (after 1.4)
7. `grep -r "## Red Flags" skills/ | wc -l` → 13 (after 1.5)
8. `grep -r "## Verification" skills/ | wc -l` → 13 (after 1.5)
9. `AGENTS.md` exists at root (after 1.1)
10. `references/` directory has 4 files (after 1.6)

---

## Open Decisions

| # | Question | Options | Recommended |
|---|----------|---------|-------------|
| 1 | Policy audit timing | A: Before Phase 1 / B: Parallel with Phase 1 / C: Defer | **B** — it's read-only, doesn't block |
| 2 | Slash commands | A: Ship as sugar over @agent / B: Skip | **A** — low cost, familiar UX |
| 3 | Audit signing strategy | A: HMAC / B: Hash-chain / C: Defer to git | **B** — fits FILE_HASHES.md model |
| 4 | Cursor target naming | A: Add `cursor` + `all` / B: Only `all` / C: Defer | **A** — explicit is better |
| 5 | `when_to_use` consolidation | A: Merge into `description` / B: Keep both | **B** — keep for now, superset is fine |

---

## Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Anti-rationalization tables age into noise | Medium | Medium | Review quarterly; rotate examples |
| Path-scoped frontmatter breaks init.py | High | Low | New tests cover emission; existing tests gate regression |
| `.cursor/rules/` emission adds maintenance | Low | Medium | Auto-generated; no manual upkeep |
| Lifecycle commands overlap with agent invocations | Medium | Low | Commands are thin wrappers; agents remain canonical |
| Hash-chain adds complexity to FILE_HASHES workflow | Low | Low | Verification script automates checks |
