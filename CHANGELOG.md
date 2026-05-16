# Changelog

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
- `resolved/agents/` output directory with 12 generated agent wrappers.
- `agent:` frontmatter block on all 12 skills — `tools`, `agents`, `model`, `handoffs`.
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
