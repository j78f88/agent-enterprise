# Changelog

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
