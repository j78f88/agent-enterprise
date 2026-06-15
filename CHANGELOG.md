# Changelog

## Supported versions

| Version | Status                              |
| ------- | ----------------------------------- |
| 3.0.x   | Supported (security + bug fixes)    |
| 2.0.x   | Security fixes only                 |
| 1.x     | Unsupported                         |
| < 1.0   | Unsupported                         |

See [SECURITY.md](SECURITY.md) for the disclosure process and the
support window once 2.1 ships.

## Deprecation timeline

| Surface                       | Deprecated in | Removed in |
| ----------------------------- | ------------- | ---------- |
| `scope:` frontmatter alias    | 2.0.0         | **3.0.0**  |
| `jsonschema.RefResolver` path | 2.0.0         | **2.1.0**  |

The `scope:` → `applies_to` migrator
(`tools/migrate-frontmatter.py`) keeps working through all 2.x and
3.x releases.

## Planned for 2.1

- Adopter template repository (one-line `git clone` + `init.py`).
- PyPI distribution (`pip install agent-enterprise`).
- Authoring linter for skill/instruction/agent frontmatter (catches
  contract violations before `init.py` runs).

## Known limitations (2.0.0)

- No PyPI package; install is `git clone` + `pip install -r ...`.
- No adopter template repo yet — adopters work from `profiles/*`.
- Windows authoring requires UTF-8-without-BOM git config; the
  `.githooks/commit-msg` hook (installed via
  `git config core.hooksPath .githooks`) rejects BOM commits.
- macOS is not exercised in CI; reports welcome.

---

## Unreleased — Sprint 6 — worktree bootstrap

Tooling for multi-agent workflows where each agent runs in its own git
worktree (default-on in Claude Code / Codex). A linked worktree starts
with no `resolved/` tree and no installed runtime deps; git has no native
"post-worktree-create" hook, so a fresh worktree must be bootstrapped
explicitly.

### Added
- **`scripts/setup-worktree.{sh,ps1}` — fresh-worktree bootstrap.**
  Resolves the repo root via `git rev-parse --show-toplevel`
  (worktree-safe — no absolute-path assumptions), installs runtime deps
  from `requirements.txt`, then runs
  `python init.py --config <config>` (default
  `config/project.config.example.yml`) to produce a working `resolved/`
  tree. Usage: `./scripts/setup-worktree.sh [config]` /
  `.\scripts\setup-worktree.ps1 [-Config <path>]`. The `.sh` auto-detects
  `python3` vs `python` and forces UTF-8
  (`PYTHONUTF8`/`PYTHONIOENCODING`) so `init.py` status glyphs do not
  crash a legacy console codepage; the `.ps1` sets `$env:PYTHONUTF8`.

### Operational notes
- **Removed the dangling `extensions.worktreeConfig` git setting.** It was
  set to `true` with no `config.worktree` file present, so it did nothing
  while carrying a latent risk — the extension makes older/non-canonical
  Git refuse to access the repo. Unset with
  `git config --unset extensions.worktreeConfig`. This is a local
  git-config change, not a tracked file. Git hooks were investigated and
  deliberately not adopted for the build: CI
  (`.github/workflows/ci.yml`) already enforces multi-target build
  health, and `resolved/` is gitignored so there is nothing committed to
  diff against.

---

## Unreleased — Sprint 5 — mode 2 dispatcher promotion

Mode 2 (Orchestration) graduates from frozen contract + reference impl
to a supported implementation per ADR 0008 — all five promotion
criteria met; contracts, schemas, and the reference impl untouched.

### Added
- **`src/mode2_dispatcher/` — supported Mode 2 implementation.**
  Dispatch core ported from the frozen reference impl (state machine,
  ghost-done verifier, tier-3 summary), plus production hardening the
  reference deliberately lacks: an fsynced append-only
  `journal.ndjson` written before each atomic `state.yml` snapshot
  (write-temp + `os.replace`), crash-resume that re-queues in-flight
  items through contract-legal transitions only, and `.mode-2-pins`
  enforcement (unsupported contract/protocol pins refuse to load).
- **Root CLI `dispatch.py`** — `run` (drain inbox, emit tier-3 summary,
  `--summary-out`), `status` (read-only, flags crash-interrupted
  items), `requeue <item-id>` (contract-legal transitions only), and
  `validate-callables` (non-zero exit on violations); `--queue-root`
  is containment-guarded like the `init.py` deploy guard. Works in a
  clean clone with no `init.py` build.
- **Callable discovery** from `*.callable.yml` sidecars (the
  non-enterprise path) and `callable-v1` skill frontmatter (the
  enterprise path), deterministic order, every candidate
  schema-validated — invalid callables are reported, never skipped.
  Native `python` (`module:function`) invocation; custom runtimes via
  `registry_from_manifests(runner=...)`.
- **Return-tier validation** reusing the phase-1
  `SubagentReturnValidator` against the
  `subagent-return-tier{1,2,3}` schemas — session end with missing or
  invalid evidence yields `rejected`, never `done`.
- **`docs/ORCHESTRATION.md`** — adopter guide: install, queue layout,
  callable authoring, `dispatch.py` usage, crash-recovery semantics,
  and the relationship to the frozen reference impl.

### Changed
- **Mode 2 install contract** names `src/mode2_dispatcher/` +
  `dispatch.py` as the supported implementation (ADR 0008 criterion 4)
  in an informative section; the contract text itself is unchanged.
- **Shared conformance parametrization.** The `mode-2-contract-v1`
  checklist now runs against both the frozen reference impl and the
  supported implementation; a byte-freeze test asserts the reference
  impl is unchanged (ADR 0008 criterion 5).
- README Mode 2 row updated from contract-plus-reference to supported
  implementation, linking `docs/ORCHESTRATION.md`.

---


## Unreleased — Sprint 4 — platform parity

Native emission for every supported platform; the README "Works
Everywhere" table is now backed by tests.

### Added
- **`codex` editor target.** `editor.target` accepts `codex`; deploy
  merges a managed agent-roster block into the adopter's `AGENTS.md`
  between `agent-enterprise:begin/end` markers — idempotent, CRLF-safe,
  never touches content outside the markers, and skips (with a warning)
  on malformed or duplicate markers.
- **Claude Code native subagents** seeded to `paths.claude_agents`
  (default `.claude/agents`) for `claude-code`/`both`/`all` targets.
- **Cursor commands** seeded to `paths.cursor_commands` (default
  `.cursor/commands`) for `cursor`/`all` targets.
- **`docs/PLATFORMS.md`** — the per-platform artifact map, with every
  matrix cell pinned by the new `tests/test_platform_emission.py`
  (parametrized over all six targets).
- CI builds the example config for every `editor.target` value and runs
  the canonical build last so post-build guardrails validate the
  canonical tree.

### Changed
- **Agent wrappers now generate for every valid `editor.target`** (was
  vscode-gated). Existing `claude-code`/`cursor` configs that previously
  skipped agent generation now produce `resolved/agents/*.agent.md` and
  their native platform surfaces on deploy. Skill `user-invocable`
  suppression remains vscode-only.
- The repo dogfoods `editor.target: all` on itself: `.claude/agents/`,
  `.cursor/rules/`, `.cursor/commands/`, and the `AGENTS.md` managed
  block are committed platform surfaces.

### Fixed
- **Post-deploy token scan no longer flags documentation literals.**
  Deployed trees are scanned with the same dotted `namespace.key`
  pattern as `scripts/check_tokens.py` (a drift-guard test pins the two
  patterns equal); both scanners now also catch multi-level tokens.
- **Stale agent wrappers are pruned.** Setup-skipped or deleted skills
  no longer leave zombie wrappers in `resolved/agents/` or deployed
  artifacts in the platform directories.
- The canonical-build-command guardrail no longer captures trailing
  quote punctuation from commands embedded in quoted code.

---


## Unreleased — Sprint 3 — claims foundation

Foundations for closing the gap between the README's three-modes /
four-platforms claims and the implementation, per ADR 0008.

### Added
- **ADR 0008 — supported mode implementations.** Defines the 5-point
  promotion contract for shipping one supported implementation per
  delivery mode; revises the `command-centre/PLAN.md` non-goal it
  supersedes. Frozen contracts untouched.
- **Four roadmap draft plans** staged in `docs/planning/drafts/`
  (platform parity, Mode 2 dispatcher promotion, Mode 3 coordinator
  promotion, adopter bootstrap; ledger ITEM-017..020).
- **CI builds every profile.** `profiles/*.config.yml` now build in CI
  alongside the canonical example config, proving each resolves
  token-free.

### Fixed
- **`jsonschema.RefResolver` migration (ITEM-013).** The registry
  coordinator reference impl and conformance tests now use the
  `referencing` API; the suite is green with `DeprecationWarning`
  escalated to error. Declared floor raised to `jsonschema>=4.18`.

### Changed
- **Planning hygiene.** Completed draft plans archived to
  `docs/archive/`; the e1 reconciliation handoff relocated beside
  `HANDOFF_REJECTIONS.md`; `docs/planning/drafts/` now holds only
  pending work.
- **README platform table.** The OpenAI Codex cell carries an interim
  footnote: Codex consumes deployed Markdown via the `AGENTS.md`
  convention today; a native emission target is staged (ITEM-017).

---

## 3.0.3 — 2026-06 — build-system hardening & commit attribution

This release hardens `init.py` and the CI guardrails (Sprint 2) and adds a
commit-attribution gate ported from `agent-homebase-e1`. No authoring-contract
changes; existing skills, instructions, and agent bodies keep working.

### Added
- **Build fails on unresolved tokens.** `init.py` now hard-exits with an
  actionable message if any `{{token}}` survives substitution, instead of
  shipping raw tokens to adopters.
- **`--deploy` seeds `.claude/commands/`** alongside `.github/`, so Claude Code
  slash-commands are available in adopter projects out of the box.
- **`scripts/check_tokens.py`** — a token-free guardrail for the deployed
  `.github/` tree, wired in as a CI step.
- **`scripts/check_build_command.py`** — asserts the docs reference the
  canonical `--config config/project.config.example.yml` build command, wired in
  as a CI step.
- **`.githooks/commit-msg` requires a `Tool:` trailer on durable commits**
  (attribution), porting e1's ADR-002/ADR-006 gate. Ephemeral
  `wip`/`fixup!`/`squash!` checkpoints and merge/revert commits are exempt. A new
  `.gitmessage` template pre-fills the trailer
  (`git config commit.template .gitmessage`).
- **Planner draft-approval checkpoint** — planner mode now blocks on an explicit
  approval before writing a sprint plan.
- **Onboarding `CLAUDE_CODE_SETUP.md` companion** covering Claude Code
  slash-command setup.

### Changed
- **`src/__init__.py` `__version__`** and **`config/plugin.json` `version`**
  bumped to `3.0.3`.
- **`init.py` `ALLOWED_COMMANDS`** extended with the security tool commands.
- **`docs/CONTRIBUTING.md` and the commit-conventions instruction** document the
  `Tool:` trailer and the one-time template setup.

### Fixed
- **Absolute-path guard in `deploy_resolved()`** prevents deploy writes from
  escaping the target tree.

### Verified
- 431 pytest tests pass (up from 401 in 3.0.2).
- `python init.py --config config/project.config.example.yml` builds with 0
  unresolved-token warnings and byte-identical output across consecutive runs.

---

## 3.0.2 — 2026-05 — adopter token resolution fixes

This release fixes `init.py` shipping raw `{{tokens}}` to adopters
(BUG-005). Adopters previously received unresolved tokens in deployed
skill companion files, agent-body cross-references, and inline code
spans. No authoring contract changes; existing skills and agent bodies
keep working.

### Fixed
- **Skill companion files now resolved and deployed.** Companion `*.md`
  files in each skill directory are discovered, run through
  `substitute()`, and written to `resolved/skills/<name>/<companion>.md`
  (respecting the setup-only skip logic). Previously they were copied
  raw or omitted, shipping unresolved tokens.
- **Skill/agent cross-references resolve to a real adopter path.** A new
  `paths.skills_deploy_dir` token (default `.github/agents/`) was
  introduced. All `skills/<name>/...` cross-references in skill sources
  and all 13 agent body wrappers (`agents/*.body.md`) were rewritten to
  `{{paths.skills_deploy_dir}}<name>/...`, so they resolve to a path that
  exists in the adopter project.
- **Tokens inside inline code spans now resolve.** `substitute()` no
  longer skips `{{tokens}}` inside backtick-delimited inline code spans.
  Path references formatted as code (e.g. agent "Key Documents"
  sections) now ship resolved.

### Added
- **`\{{token}}` escape for literal tokens in prose.** A single leading
  backslash marks a token that should survive verbatim. The marker is
  preserved through `substitute()` and the unresolved-token scans, then
  removed by a final `strip_escapes()` pass — yielding a clean `{{...}}`
  literal. `find_unresolved_tokens()` honours the escape so intentional
  literals are not flagged. See `docs/EXTENSION_GUIDE.md`.

### Changed
- **`src/__init__.py` `__version__`** bumped to `3.0.2`.
- **`config/plugin.json` `version`** bumped to `3.0.2`.
- **`.github/copilot-instructions.md`** regen command corrected to
  `config/project.config.example.yml` (matching AGENTS.md).

### Verified
- 401 pytest tests pass / 7 skipped.
- `python init.py --config config/project.config.example.yml` builds with
  0 unresolved-token warnings and byte-identical output across two
  consecutive runs.

---

## 3.0.1 — 2026-05 — enforcement gates and heading hierarchy

This release adds **no new policy**. It adds automated regression
protection for the conventions established in 3.0.0 and normalises a
small number of pseudo-headings that were missed by the 3.0.0 voice
pass.

### Added
- **`tests/test_skill_length.py`** — enforces the 200-line cap on
  `skills/*/*.skill.md` documented in `docs/SKILL_AUTHORING_GUIDE.md`.
  Supporting files in the same skill directory are excluded from the
  count.
- **`tests/test_skill_description.py`** — enforces the four description
  rules from the authoring guide: ≤ 1024 characters, capital first
  letter, presence of a `Use <when|after|to|with|on|...>` trigger
  sentence, and the description must not lead with the skill name.
- **`tests/test_voice_compliance.py`** — fails on bare all-caps
  prohibitions (`MUST`, `NEVER`, `DO NOT`) and on hedging words
  (`consider`, `perhaps`, `might`, `may be useful`, `you could`) in
  skill files. Code spans, link targets, and YAML frontmatter are
  ignored.
- **`tests/test_doc_headings.py`** — fails on standalone bold-only
  lines (pseudo-headings) in user-facing documentation. Inline bold
  field labels in lists and prose are unaffected. Scope: top-level
  user-facing docs (`README.md`, `AGENTS.md`, `CLAUDE.md`,
  `CONTEXT.md`, `CHANGELOG.md`, `ANTI_FRAGILITY.md`,
  `SECURITY.md`, and every top-level `docs/*.md`). Internal sprint records and the long-form
  `sandbox-architecture.instructions.md` are out of scope by design.

### Changed
- **`skills/onboarding/onboarding.skill.md`** description gained a
  `Use when` trigger sentence to satisfy the new description rule.
- **`README.md`** tagline converted from bold paragraph to italic
  subtitle.
- **`ANTI_FRAGILITY.md`** four `**Mitigation.**` pseudo-headings
  converted to `### Mitigation`.
- **`docs/BEST_PRACTICE_ALIGNMENT_JOURNAL.md`** locked-baseline
  pseudo-heading converted to `### Locked baseline`.
- **`docs/ONBOARDING.md`** four `**Option A/B — ...**` pseudo-headings
  converted to `### Option A/B — ...`.
- **`docs/POLICY_AUDIT.md`** `**Proposed disposition**` pseudo-heading
  converted to `### Proposed disposition`.
- **`docs/SKILL_AUTHORING_GUIDE.md`** clarified that the opening
  paragraph IS the skill Overview (mandatory, headingless, sits
  between H1 and `## When to Use`).
- **`CONTEXT.md`** clarified voice-rule scope: rules apply to
  agent-facing prose, not to structured artifacts (ADRs, JSON schemas,
  reference checklists in `references/`).
- **`v3uplift/QA_REPORT.md`** appended a remediation-status redux
  section: 6 of 7 critical violations closed, 1 accepted deviation
  (CV-06, dead ADR-0008 reference in a historical sprint run-sheet).
- **`v3uplift/JOURNEY.md`** filled in phase status table, lessons
  learned, and "what would change" retrospective.
- **`src/__init__.py` `__version__`** bumped to `3.0.1`.
- **`config/plugin.json` `version`** bumped to `3.0.1`.

### Verified
- 395 pytest tests pass / 7 skipped (233 baseline + 162 parametrised
  enforcement cases from the four new tests).
- `python init.py --config config/project.config.example.yml` builds
  clean with byte-identical output across two consecutive runs.

### Changed
- Moved `ANTI_FRAGILITY.md` and `CONTEXT.md` to `docs/` (root declutter)
- Completed AGENTS.md Key directories table (all 17 directories)

### Added
- Per-directory READMEs for `src/`, `hooks/`, `starters/`, `tools/`
- `starters/copilot-instructions.md` platform entry point template
- `/tools/` entry in CODEOWNERS



### Added
- **Skill authoring guide** (`docs/SKILL_AUTHORING_GUIDE.md`) — canonical
  reference for writing skills: section order, voice rules, prohibition
  style, description format, and governance requirements.
- **Domain glossary** (`CONTEXT.md`) — single source of truth for every
  domain term used across skills, instructions, and documentation.
- **Hard/soft dependency ADR**
  (`docs/decisions/0001-hard-soft-instruction-dependencies.md`) —
  classifies each instruction as hard (requires project config tokens)
  or soft (works standalone).

### Changed
- **All 13 skills audited and rewritten** to conform to the authoring
  guide: consistent section order, imperative voice, bold lowercase
  prohibitions (`**never**`, `**must**`, `**do not**`).
- **Voice unification** across documentation, instructions, and agent
  bodies — passive voice and hedging words removed from agent-facing
  content.
- **Cross-references corrected** — stale file counts, dead ADR links,
  and inconsistent build commands fixed.
- **`src/__init__.py` `__version__`** bumped to `3.0.0`.
- **`config/plugin.json` `version`** bumped to `3.0.0`.

### Breaking
- **Prohibition style standardised:** all skills use bold lowercase
  keywords (`**never**`, `**must**`, `**do not**`). Agent bodies use
  `**Never** verb phrase` at list-item start (documented convention).
- **Skill section order standardised:** all 13 skills follow the
  canonical template from the authoring guide.

### Verified
- 233 pytest tests pass / 7 skipped.
- `python init.py --config config/project.config.example.yml` builds
  clean with deterministic output.

---

## 2.0.0 — 2026-05 — `protocol-v1` ships complete

### Added
- **Four JSON Schemas under `schemas/`** that gate the build:
  `frontmatter-v1`, `callable-v1`, `project-v1`, `registry-v1`.
- **`validate_frontmatter()` in `init.py`** — strict by default. Every
  skill, instruction, and agent body is validated against
  `frontmatter-v1`; skills additionally validated against
  `callable-v1`. Use `--allow-frontmatter-warnings` for lax mode.
- **`callable-v1` manifests on all 13 skills** (`inputs`, `outputs`,
  `verifier`). Verifier callables declare `verifier: null` per ADR-0009.
- **Mode-2 reference implementation**
  ([`command-centre/03-mode-orchestration/reference-impls/file-queue-dispatcher/`](../command-centre/03-mode-orchestration/reference-impls/file-queue-dispatcher/))
  — file-backed queue dispatcher with a finite-state machine, freshness
  check, and a passing `conformance_test.py`.
- **Mode-3 reference implementation**
  ([`command-centre/04-mode-choreography/reference-impls/registry-coordinator/`](../command-centre/04-mode-choreography/reference-impls/registry-coordinator/))
  — fleet coordinator that validates a registry, detects contract drift,
  reports contract-bump impact, harvests audit JSON, and ships three
  meta-agents (`framework-dev`, `harvest`, `audit`). Includes a passing
  `conformance_test.py`.
- **Conformance tests** under `tests/test_protocol_v1_conformance.py`
  (schema self-validation, every substrate file validates, fixture
  registry validates, both reference-impl conformance scripts run
  clean) and unit tests under `tests/test_frontmatter_validation.py`.
- **`tools/migrate-frontmatter.py`** — idempotent migrator that brings
  legacy substrate into `frontmatter-v1` shape (renames `scope:` to
  `applies_to:`, adds `id`/`kind`/`version`, seeds default
  `callable-v1` manifest on skills missing one).
- **`jsonschema>=4.0`** added to `requirements.txt`.

### Changed
- **`applies_to:` is canonical, `scope:` is a legacy read-only alias.**
  Per ADR-0012. The validator accepts both on read; new files must use
  `applies_to`. All 25 instruction files and 13 agent body files were
  migrated.
- **`init.py` agent generation** now parses frontmatter on
  `agents/*.body.md` and emits only the body into generated
  `.agent.md`, so newly-added frontmatter is not duplicated.
- **`README.md`** rewritten around `protocol-v1`, the three modes, and
  the four schemas.
- **`src/__init__.py` `__version__`** bumped to `2.0.0`.

### Deprecated
- **`scope:` frontmatter field.** Still accepted on read as an alias for
  `applies_to:`; will be removed in a future major. Run
  `python tools/migrate-frontmatter.py` to migrate.

### Removed
- **`resolved/` and `.agent-state/` from version control.** Both are
  build/runtime output. `.gitignore` updated; existing tracked files
  untracked via `git rm -r --cached`.

### Migration
1. `pip install -r requirements.txt` (picks up `jsonschema`).
2. `python tools/migrate-frontmatter.py` to rename `scope:` →
   `applies_to:` and seed missing IDs/kinds.
3. For any custom skills, add a `callable-v1` manifest (`inputs`,
   `outputs`, `verifier`). See [docs/EXTENSION_GUIDE.md](EXTENSION_GUIDE.md).
4. `python init.py --config <your-config>` — strict frontmatter
   validation is on by default. Use `--allow-frontmatter-warnings`
   only as a temporary escape hatch.

### Verified
- 233 pytest tests pass / 7 skipped.
- `python init.py --config profiles/python-api.config.yml` runs twice
  with byte-identical `resolved/` output (determinism preserved).
- Both reference-impl `conformance_test.py` scripts pass standalone
  and via pytest.

---

## 1.4.0 — 2026-04-30

### Added
- **@onboarding skill** — guided first-time setup agent that walks deployers through profile selection, config filling, skill selection, token resolution, file deployment, seeding, and verification. Self-removes after setup is complete.
- `lifecycle: setup-only` frontmatter field — skills with this value are excluded from `resolved/` output when `setup_complete: true` in config. Stale resolved output is cleaned automatically.
- `setup_complete` config field in `project.config.example.yml` (default: `false`).
- `agents/onboarding.body.md` — lean agent wrapper body for the onboarding skill.

### Changed
- **docs.skill.md** — full review and update:
  - Added Subagent Mode section (sprint-lead invokes @docs as subagent; was undocumented).
  - Added Anti-Patterns section with 7 docs-specific patterns.
  - Added Interaction Style section with `askQuestions` decision points.
  - Added `subagent-return-schemas.instructions.md` to Shared Rules.
  - Replaced hardcoded "Australian English" with `{{project.locale}}` token.
  - Removed project-specific references (Wizard steps, `.github/` paths, `UpdateNotification`, feature matrix exclusions, emoji heading markers).
  - Fixed broken step numbering in Sync Workflow (was: 1-5, 5-8, 7-10, 11, 12; now: sequential 1-15).
  - Converted user_guide mega-paragraph into scannable checklist.
  - Added section separators (`---`) for visual consistency.
  - Simplified README validation to be project-agnostic.
- `init.py` — reads `setup_complete` from config; skips `lifecycle: setup-only` skills and cleans stale resolved output during resolution.

## 1.3.0 — 2026-04-28

### Added
- **Dual-platform agent generation** — `init.py` generates VS Code `.agent.md` wrappers from skill `agent:` metadata when `editor.target` includes `\"vscode\"`.
- `editor.target` config option: `\"vscode\"` | `\"claude-code\"` | `\"both\"` (default). Added to example config and all 3 profiles.
- `resolved/agents/` output directory with 13 generated agent wrappers.
- `agent:` frontmatter block on all 13 skills — `tools`, `agents`, `model`, `handoffs`.
- Tool restriction mapping: `reviewer` is read-only, `architect`/`pm` are read+search, `sprint-lead` gets agent delegation, `researcher` gets web access.
- `parse_frontmatter()`, `extract_agent_body()`, `generate_agent_md()`, `generate_agents()`, and `suppress_skill_invocability()` functions in `init.py`.
- Editor target validation in `SecurityValidator`.

### Changed
- Skills set to `user-invocable: false` in resolved output when agents are generated with `editor.target: \"vscode\"` (prevents duplicate discovery).
- README updated with platform selection table, project structure, and agent copy step.
- ONBOARDING.md updated with `editor.target` guidance, `resolved/agents/` copy step, and verification checks.
- ARCHITECTURE.md updated with dual-platform overview and resolved output structure.
- CUSTOMIZATION.md updated with platform selection section and agent metadata customization.
- SKILL_FLOW.md updated with agent wrapper column in skill inventory.

### Corrections (previously undocumented)
- **Fixed**: Skill source files renamed from `SKILL.md` to `{name}.skill.md` (e.g., `architect.skill.md`) for unique identification in editor tabs and file pickers. `init.py` resolves these to `SKILL.md` in output per VS Code convention.
- 5 generic instruction files added across v1.0–v1.2 but not recorded in prior changelog entries: `determinism-guarantees.instructions.md`, `fsm-orchestration.instructions.md`, `observability.instructions.md`, `security-model.instructions.md`, `state-management.instructions.md`.
- `severity-levels.instructions.md` moved from `instructions/generic/` to `instructions/configurable/`.
- `user-invocable: true` added to `docs`, `planner`, `pm`, and `sprint-lead` skills (was missing from frontmatter).
- Instruction count corrected across all documentation: 10 generic + 14 configurable = 24 total (was incorrectly stated as 23).
- Agent/skill count corrected: 12 roles (was incorrectly stated as 11 in several docs — missed updating after `@security` was added in v1.1.0).
- ONBOARDING.md updated to list `@security` in skill selection guidance.
- TROUBLESHOOTING.md updated to include `security` in skill folder checklist.
- IMPLEMENTATION_PLAN.md target structure updated to reflect current state (security skill, agents/, new instruction files, starter files, resolved/agents/).

## 1.2.0 — 2026-04-28

### Added
- **7 new security checks** (8–14): SBOM generation, SAST scanning, git history secret scanning, license compliance, HTTP security headers, container image scanning, IaC scanning.
- **Remediation playbook** — 4-case OWASP decision tree classifying each finding into patched/delayed/no-fix/zero-day with timelines and effort tags.
- New config tokens: `commands.sbom_generate`, `commands.sast`, `commands.secret_scan_history`, `commands.license_check`, `commands.container_scan`, `commands.iac_scan`, `paths.sbom_output`, `security.sbom_format`, `security.scan_git_history`, `security.license_gate`, `security.license_denylist`, `security.license_allowlist`, `security.check_security_headers`, `security.sast_tool`, `security.iac_scanner`.
- 6 new changelog categories: `sast-finding`, `license-risk`, `git-history-secret`, `security-header`, `container-vuln`, `iac-misconfig`.
- SBOM governance, license compliance policy, git history baseline management, and remediation decision tree added to `security-audit.instructions.md`.

### Changed
- Gate logic expanded: SAST critical findings, git history secrets, critical container vulns, critical IaC misconfigs, and (optionally) license denylist matches now trigger FAIL.
- Report format updated with 7 new metric lines and remediation guidance section.
- Machine-readable JSON summary expanded with 7 new metric fields.

## 1.1.0 — 2026-04-28

### Added
- **@security** skill — vulnerability scanning, CVE research, secret detection, OWASP pattern matching, file integrity hashes, supply chain audit, and security changelog management.
- `security-audit.instructions.md` — audit scheduling, changelog governance, hash registry management, and @reviewer enforcement rules.
- `starters/SECURITY_CHANGELOG.md` — append-only security finding log template.
- `starters/FILE_HASHES.md` — SHA-256 file integrity registry template.
- New config tokens: `paths.security_changelog`, `paths.file_hashes`, `paths.security_reports`, `security.audit_on_sprint`, `security.audit_on_dependency_change`, `security.tracked_files`, `security.cvss_*_threshold`, `security.cisa_kev_check`, `security.sec_id_prefix`.
- `@security` wired as optional sprint quality gate in `@sprint-lead` Phase 3.

### Changed
- `@sprint-lead` now has 6 named specialist agents (was 5).
- `severity-levels.instructions.md` table updated to include `@security`.
- Onboarding Step 6 now seeds `docs/security/` directory with security starter files.

## 1.0.0 — 2026-04-26

Initial release. Extracted from the DIY Project Helper monorepo.

11 skills: pm, planner, sprint-lead, qa, reviewer, architect, researcher, bug, docs, a11y, perf.
18 instruction files: 6 generic, 12 configurable.
3 profiles: monorepo-fullstack, react-web-app, python-api.
7 starter files for new project setup.

Cross-compatible with GitHub Copilot (VS Code) and Claude Code / Cowork.
