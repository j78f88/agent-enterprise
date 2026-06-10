# Platform Parity — Native Emission for Claude Code, Cursor, and Codex

**Status:** Planned (promoted to sprints/sprint-4/PLAN.md)
**Type:** Feature (claims-truth / build-system)
**Sources:** session review 2026-06-10 (user-approved "close the gap upward" roadmap) · **Ledger:** ITEM-017
**Dependencies:** Sprint 3 (claims foundation: ADR 0008, CI profile matrix, README Codex footnote)

## Goals

- Agent generation is no longer gated to VS Code targets: `claude-code`,
  `cursor`, and a new `codex` value of `editor.target` each produce a
  native artifact set, while `suppress_skill_invocability` stays
  vscode-only.
- Claude Code adopters get native subagents in `.claude/agents/` (in
  addition to the existing `.claude/commands/` slash commands).
- Cursor adopters get `.cursor/commands/` seeded the same way Claude
  commands are seeded today.
- Codex adopters get a managed block merged idempotently into their
  `AGENTS.md` — never clobbering content outside the markers — and this
  repo dogfoods the emission on its own `AGENTS.md`.
- Every target is proven by a parametrized test module and a CI
  `editor.target` build dimension; the README "Works Everywhere" table
  and badges say only what the tests prove.

## Why This Sprint

The 2026-06-10 review found the README claims four platforms "Ready"
while `init.py:1106` only generates agent wrappers for
`('vscode', 'both', 'all')` and `codex` is absent from
`VALID_EDITOR_TARGETS` (`init.py:109`). Sprint 3 footnoted the Codex
cell (README ~L321-323) as an interim honesty measure; this sprint
removes the need for the footnote by making the claim true. Platform
parity is the first rung of the approved roadmap because it touches
only the build tool (`init.py`) and emission targets — no frozen
contract, no runtime — and the mode-promotion drafts
(`mode2-dispatcher-promotion-draft-plan.md`,
`mode3-coordinator-promotion-draft-plan.md`) deliver more value once
every platform can consume their artifacts.

## Technical Tasks

Execution order: **1** first (target plumbing), then **2, 3, 4** in
parallel (one emission target each), then **5 → 6 → 7** (tests, CI,
docs).

### Task Group 1: Ungate agent generation per target
Files: `init.py`, `tests/test_init.py`

- [ ] Add `'codex'` to `VALID_EDITOR_TARGETS` (`init.py:109`); keep the
      `SecurityValidator` editor-target check (`init.py:243-247`) intact.
- [ ] Rework the agent-wrapper gate (`init.py:1102-1124`): run
      `generate_agents()` (`init.py:588`) for `claude-code`, `cursor`,
      and `codex` as well, dispatching to per-target emission.
- [ ] Keep `suppress_skill_invocability` (`init.py:650`,
      called at `init.py:1112-1114`) strictly vscode-only — Claude
      Code/Cursor/Codex must not get `user-invocable: false` skills.
- [ ] Verify the existing cursor frontmatter transform path
      (`emit_cursor`, `init.py:1058-1066`) composes with the new gate
      rather than duplicating emission.
- [ ] Tests: each target value produces its artifact set; invalid target
      still fails validation.

### Task Group 2: Claude Code native subagents → `.claude/agents/`
Files: `init.py`, `config/project.config.example.yml`, `profiles/monorepo-fullstack.config.yml`, `profiles/python-api.config.yml`, `profiles/react-web-app.config.yml`, `tests/test_init.py`

- [ ] Add a `paths.claude_agents` token (default `.claude/agents`) to the
      example config and all three profiles, alongside the existing
      `paths.claude_commands` (profiles ~L52-53).
- [ ] Emit one native subagent file per agent into `paths.claude_agents`,
      reusing `generate_agent_md` (`init.py:553`) with Claude Code
      subagent frontmatter (name/description/tools), wired through
      `deploy_resolved` (`init.py:782`).
- [ ] Seeding is deterministic, sorted, and idempotent (mirror the
      `.claude/commands/` seeding pattern at `init.py:850-860`).
- [ ] Respect the absolute-path deploy guard (`init.py:805-816`) for the
      new token.

### Task Group 3: Cursor `.cursor/commands/` seeding
Files: `init.py`, `config/project.config.example.yml`, `profiles/*.config.yml`, `tests/test_init.py`

- [ ] Add a `paths.cursor_commands` token (default `.cursor/commands`)
      to the example config and all three profiles.
- [ ] Mirror the Claude commands seeding logic (`init.py:850-860`):
      `resolved/agents/*.agent.md` → `cursor_commands/<name>.md`, with
      any cursor-specific frontmatter handled by the existing
      `transform_frontmatter_for_target` path (`init.py:1066`).
- [ ] Include the new directory in the post-deploy token-free scan
      (pattern at `init.py:872-873`).

### Task Group 4: Codex `AGENTS.md` managed-block emission
Files: `init.py`, `AGENTS.md` (this repo, dogfood), `tests/test_init.py`

- [ ] Implement `emit_codex_agents_md()`: render the agent roster +
      pointers to deployed skills into a managed block delimited by
      `<!-- agent-enterprise:begin -->` / `<!-- agent-enterprise:end -->`.
- [ ] Merge semantics: if the adopter's `AGENTS.md` exists, replace only
      the content between the markers (append the block if absent);
      **never modify anything outside the markers**; create the file if
      missing. A second run with unchanged inputs is byte-identical.
- [ ] Dogfood: run the `codex` emission against this repo's own
      `AGENTS.md` and commit the managed block.
- [ ] Tests: merge into a pre-existing `AGENTS.md` with surrounding
      content; idempotency (run twice → identical); malformed/missing
      markers handled without data loss.

### Task Group 5: `tests/test_platform_emission.py` parametrized over targets
Files: `tests/test_platform_emission.py` (new)

- [ ] Parametrize over `vscode`, `claude-code`, `cursor`, `codex`,
      `both`, `all`: build into a temp dir and assert the expected
      artifact set per target (and the absence of other targets'
      artifacts).
- [ ] Assert every emitted artifact is token-free
      (`find_unresolved_tokens`) and deterministic (double-build,
      identical bytes).
- [ ] Assert the `AGENTS.md` managed-block merge is idempotent and
      preserves out-of-marker content.
- [ ] Assert `suppress_skill_invocability` fires only for `vscode`.

### Task Group 6: CI `editor.target` dimension
Files: `.github/workflows/ci.yml`

- [ ] Extend the Sprint 3 profile build loop with an `editor.target`
      dimension: build the example config once per target value and rely
      on the existing fail-on-unresolved + token-free guardrails.
- [ ] Keep the canonical-build-command doc check (ITEM-011) intact —
      target builds are additional, not a new canonical command.

### Task Group 7: docs/PLATFORMS.md + README truth pass
Files: `docs/PLATFORMS.md` (new), `README.md`, `skills/onboarding/onboarding.skill.md`, `docs/ONBOARDING.md`

- [ ] Write `docs/PLATFORMS.md`: per-platform artifact map (what each
      `editor.target` emits, where, and how the platform consumes it),
      including the Codex managed-block contract.
- [ ] README truth pass: remove the Codex footnote (README ~L321-323),
      update the "Works Everywhere" table and badges so every "Ready"
      cell is backed by `tests/test_platform_emission.py`.
- [ ] Onboarding skill: document the per-platform setup split
      (Copilot `@agent` / Claude Code `/command` + subagents / Cursor
      commands / Codex `AGENTS.md`).

## Files to Create/Modify

- `init.py` — target ungating, `paths.claude_agents` + `paths.cursor_commands` deploy, `emit_codex_agents_md()` (TG1-4)
- `config/project.config.example.yml` + 3 `profiles/*.config.yml` — new path tokens (TG2, TG3)
- `AGENTS.md` — dogfooded managed block (TG4)
- `tests/test_platform_emission.py` (new) + `tests/test_init.py` additions (TG1-5)
- `.github/workflows/ci.yml` — `editor.target` dimension (TG6)
- `docs/PLATFORMS.md` (new), `README.md`, `skills/onboarding/onboarding.skill.md`, `docs/ONBOARDING.md` (TG7)

## Quality Gates

- [ ] standard — `python -m pytest tests/ -v` stays green (401+), zero new warnings
- [ ] Determinism — re-run `init.py` twice per target, output identical (including the `AGENTS.md` merge)
- [ ] guardrail — token-free `.github/**` check passes; new target dirs covered by the post-deploy token scan
- [ ] docs — voice/heading tests green for `docs/PLATFORMS.md` and updated docs

## Success Criteria

- [ ] All four platform targets emit native artifacts; `codex` is a valid `editor.target`.
- [ ] `.claude/agents/`, `.cursor/commands/`, and the `AGENTS.md` managed block are seeded deterministically and idempotently.
- [ ] This repo's own `AGENTS.md` carries the dogfooded managed block with no content lost outside markers.
- [ ] `tests/test_platform_emission.py` passes for every target; CI builds every target token-free.
- [ ] README Codex footnote removed; platform table backed by tests; `docs/PLATFORMS.md` published.
- [ ] `suppress_skill_invocability` remains vscode-only.

## Risks

- The `AGENTS.md` merge writes into an adopter-owned file — mitigation:
  marker-bounded replacement only, never touch outside markers, tests
  cover pre-existing content and missing/duplicated markers, and the
  dogfood run on this repo's `AGENTS.md` is reviewed in the diff.
- Ungating at `init.py:1106` changes behaviour for existing
  `claude-code`/`cursor` configs that previously skipped agent
  generation — mitigation: `tests/test_platform_emission.py` pins the
  exact artifact set per target; CHANGELOG entry calls out the change.
- New path tokens can drift across example config and profiles —
  mitigation: the Sprint 3 CI profile matrix builds all four configs;
  fail-on-unresolved catches a missing token.
- Cursor emission already partially exists (`init.py:1058-1066`) and
  could be duplicated — mitigation: TG1 explicitly audits and composes
  with the existing transform instead of adding a parallel path.
- Roadmap line refs drift as `init.py` grows — mitigation: Files:
  annotations above were re-verified against the current tree
  (gate at `init.py:1102-1124`, guard at `init.py:805-816`, seeding at
  `init.py:850-860`).

## Sprint Execution Guidelines

_(left for @sprint-lead)_

## Commit Plan

_(left for @sprint-lead)_
