# Draft Plan — Onboarding Path Resolution Remediation

**Type:** debt / bug-fix · **Status:** draft · **Source:** BUG-005 · **Ledger:** ITEM-008

## Problem

`init.py` leaves unresolved `{{tokens}}` in deployed artifacts via three distinct mechanisms. Adopters see raw `{{paths.*}}` / `{{commands.*}}` / `{{git.*}}` across skills and agent docs after onboarding.

- **(A) Companion files never resolved or deployed.** The build loop only processes the main `*.skill.md` file per directory ([init.py](../../../init.py) skill loop). These companion files keep raw tokens and are never copied to `resolved/` or `.github/agents/`:
  - `skills/planner/session-lifecycle.md`, `skills/planner/session-end-menu.md`
  - `skills/sprint-lead/phase-details.md`, `skills/sprint-lead/subagent-templates.md`
  - `skills/security/report-format.md`, `skills/security/audit-checks.md`
  - `skills/docs/sync-workflow.md`
- **(B) Inline code-span tokens skipped.** `substitute()` ([init.py](../../../init.py) `substitute()` / `_code_span_ranges()`) deliberately skips `{{tokens}}` inside **inline** backtick spans only — fenced ```` ``` ```` blocks already resolve (confirmed: deployed `a11y/SKILL.md` resolves `{{commands.e2e}}` correctly inside a `bash` block). The inline-backtick convention is **overloaded**: it marks both (i) genuine template-system literals in prose (correctly skipped) and (ii) real path references formatted as code (wrongly skipped, e.g. `.github/agents/docs.agent.md` "Key Documents" section). Position alone cannot distinguish the two.
- **(C) Cross-references use source paths.** References point at `skills/<name>/...` source paths that do not exist in an adopter deployment that only ships `.github/agents/`.

## Goals

- Every deployed file under `resolved/` (and copied to `.github/agents/`) has zero unresolved real-reference tokens.
- Companion `.md` files are resolved and deployed alongside their `SKILL.md`.
- Cross-references resolve to a path that exists in the adopter project.

## Technical Tasks

Execution order: **A → C → B**. A is purely additive (no behaviour change). C depends on where companions land. B is the only behaviour change with blast radius — do it last, behind the literal audit.

### Task Group 1 (A): Resolve & deploy companion files
Files: `init.py`, `tests/` (new test)

- [ ] Extend the skill loop to discover non-skill `*.md` companion files in each skill dir, run `substitute()` on them, and write to `resolved/skills/<name>/<companion>.md`.
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
- [ ] **Audit** every existing inline `{{token}}` across `skills/` and `instructions/`, classify real-reference vs. template-literal, and add escapes to the literals (mostly authoring/prose contexts).
- [ ] Add test: inline `` `{{paths.x}}` `` resolves; escaped `` `\{{paths.x}}` `` survives verbatim.

## Quality Gates

- [x] standard (test) — `python -m pytest tests/ -v` stays green (393+)
- [ ] Determinism — re-run `init.py` twice, output identical

## Acceptance Criteria

- [ ] `python init.py` produces 0 real-reference unresolved tokens in `resolved/`.
- [ ] Companion files deployed and resolved.
- [ ] grep for `{{` in `resolved/` returns only intentional doc literals (if any).
- [ ] Full test suite green.

## Decisions

- **Defect B policy = Option 2a** (resolve inline spans + escape for literals). Option 2b was rejected after audit: fenced blocks legitimately carry real `{{commands.*}}` / `{{paths.*}}` tokens that already resolve, so skipping them would break command resolution.
- **Sequencing = A → C → B.**
- **No @architect handoff** — this is a build-system mechanics fix, not an architectural decision.
- **Companion files ship separately** (not flattened into `SKILL.md`) — resolved `SKILL.md` files already reference them by path, and flattening would bloat agent context windows.

## Risks

- Defect B fix changes long-standing behaviour — the literal audit (Task Group 3) is load-bearing. A missed literal will resolve when it should stay verbatim; a missed escape-need will leave a real reference unresolved.
- Companion-file resolution interacts with setup-only skip logic.

## Open Questions

- None blocking. The escape token syntax (`\{{...}}` vs. an alternative) is an implementation detail for the executing sprint.
