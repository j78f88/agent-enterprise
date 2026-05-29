# Sprint 1 — Onboarding Path Resolution Remediation

**Status:** Planned · **Type:** debt / bug-fix
**Sources:** BUG-005 · **Ledger:** ITEM-008
**Dependencies:** None

## Goals

- Every deployed file under `resolved/` (and copied to `.github/agents/`) has zero unresolved real-reference tokens.
- Companion `.md` files are resolved and deployed alongside their `SKILL.md`.
- Cross-references resolve to a path that exists in the adopter project.

## Why This Sprint

`init.py` ships raw `{{tokens}}` to every adopter via three independent mechanisms (companion files never resolved, inline code-span tokens skipped, cross-references using non-deployed source paths). This degrades every onboarding (BUG-005, 🟡 Degraded) and is a build-system gap, not a config error — so it cannot be worked around downstream.

## Technical Tasks

Execution order: **A → C → B**. A is purely additive. C depends on where companions land. B is the only behaviour change with blast radius — done last, behind the literal audit.

### Task Group 1 (A): Resolve & deploy companion files
Files: `init.py`, `tests/` (new test)

- [ ] Extend the skill loop to discover non-skill `*.md` companion files in each skill dir, run `substitute()` on them, write to `resolved/skills/<name>/<companion>.md`.
- [ ] Respect setup-only skip logic — companions of skipped skills are skipped too.
- [ ] Add test: companion file present in resolved output with tokens resolved.

### Task Group 2 (C): Cross-reference path correctness
Files: skill source files, `init.py` / config (new token)

- [ ] Introduce a `paths.skills_deploy_dir` token (or similar) and rewrite `skills/<name>/...` references to use it.
- [ ] Update sprint-lead, planner, security, docs cross-references.
- [ ] Add test: no resolved file references a non-deployed `skills/` path.

### Task Group 3 (B): Inline code-span token policy — Option 2a
Files: `init.py`, `tests/`, affected skill + instruction sources

- [ ] Flip the default: resolve `{{tokens}}` inside inline backtick spans (stop skipping them in `substitute()`).
- [ ] Add an explicit escape for genuine literals (e.g. `\{{token}}`) and teach `substitute()` + `find_unresolved_tokens()` to honour it.
- [ ] Audit every existing inline `{{token}}` across `skills/` and `instructions/`, classify real-reference vs. template-literal, add escapes to the literals.
- [ ] Add test: inline `` `{{paths.x}}` `` resolves; escaped `` `\{{paths.x}}` `` survives verbatim.

## Files to Create/Modify

- `init.py` — companion-file loop (A), new path token wiring (C), code-span policy + escape handling (B)
- `config/project.config.yml` + profiles — new `paths.skills_deploy_dir` token (C)
- `skills/**` and `instructions/**` — cross-reference rewrites (C), literal escapes (B)
- `tests/` — new tests for A, B, C

## Quality Gates

- [x] standard (test) — `python -m pytest tests/ -v` stays green (393+)
- [x] Determinism — re-run `init.py` twice, output identical

## Success Criteria

- [ ] `python init.py` produces 0 real-reference unresolved tokens in `resolved/`.
- [ ] Companion files deployed and resolved.
- [ ] grep for `{{` in `resolved/` returns only intentional doc literals (if any).
- [ ] Full test suite green.

## Technical Notes / Decisions

- Defect B policy = **Option 2a** (resolve inline spans + escape for literals). 2b rejected: fenced blocks legitimately carry real `{{commands.*}}`/`{{paths.*}}` that already resolve.
- Sequencing = A → C → B (B last, behind the literal audit).
- Companion files ship separately (not flattened into `SKILL.md`) — avoids agent-context bloat.
- No @architect handoff — build-system mechanics, not an architectural decision.

## Risks

- Defect B fix changes long-standing behaviour — the literal audit (Task Group 3) is load-bearing. A missed literal will resolve when it should stay verbatim; a missed escape-need will leave a real reference unresolved.
- Companion-file resolution interacts with setup-only skip logic.

## Pre-flight Findings

- NON_GOALS: no conflict (file holds only example placeholders).
- Ledger: ITEM-008 not escalated (Age 0, Def 0).
- Claims A/B/C verified against `init.py` source: skill loop processes only `*.skill.md`/`SKILL.md`; `substitute()` and `find_unresolved_tokens()` skip inline code spans via `_code_span_ranges`.

## Compliance Notes

- Determinism gate required (init.py is the deterministic build core).
- No store/migration/a11y gates apply — Python build-system change only.

<!-- Sprint Execution Guidelines + Commit Plan — left for @sprint-lead -->
