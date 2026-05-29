---
id: instruction.security-audit
kind: instruction
version: 1.0.0
applies_to: docs/security/SECURITY_CHANGELOG.md, docs/security/FILE_HASHES.md
description: Procedures the @security agent follows for audits, changelog governance,
  hash registry management, and sprint gate integration.
applyTo: docs/security/SECURITY_CHANGELOG.md, docs/security/FILE_HASHES.md
---

# Security Audit Procedures

Shared instruction governing `@security` agent behaviour: audit scheduling, changelog governance, hash registry management, and integration with sprint gates.

---

## Scheduling

### Manual Invocation

User invokes `@security` at any time. Full pipeline runs, report is produced.

### Sprint Gate Integration

When `@sprint-lead` includes `security` in the PLAN.md Quality Gates checklist:

1. `@sprint-lead` invokes `@security` as a subagent during Phase 3 (Quality Gates)
2. `@security` runs the full pipeline against the current working tree
3. Gate result: PASS/FAIL per the gate logic in the SKILL.md
4. FAIL blocks sprint advancement — `@sprint-lead` must create remediation tasks or get explicit user approval to proceed

### Scheduled Recurring Audit

Users may configure periodic audits. The recommended cadence:

| Cadence | Scope | Trigger |
|---------|-------|---------|
| Every sprint | Full pipeline | `@sprint-lead` Phase 3 |
| Weekly | Dependency scan + exploit research only | User or CI cron |
| On dependency change | Dependency scan | Lock file change detected |
| On merge to main | Full pipeline | CI hook |

When running a scheduled audit, `@security` must:
1. Load the previous audit report from `{{paths.security_reports}}/`
2. Run the full pipeline
3. Diff findings: identify **new**, **resolved**, and **unchanged**
4. Only append **new** findings to `{{paths.security_changelog}}`
5. Update resolved findings' status in the changelog (append a resolution note — do not edit the original entry)

---

## SBOM Governance

### Format

- **Preferred:** CycloneDX JSON (configurable via `{{security.sbom_format}}`)
- **Acceptable:** SPDX JSON
- Output stored at `{{paths.sbom_output}}`

### When to Generate

- Every full audit (on-demand, sprint gate, or scheduled)
- Every dependency change (lock file modification)
- Optionally every build (if CI integration is configured)

### Storage & Retention

- Current SBOM committed at `{{paths.sbom_output}}` alongside lock files
- Previous SBOMs archived in `{{paths.security_reports}}/` — retain last 5 for diff comparison
- Naming: `sbom-YYYY-MM-DD.json`
- Commit message: `security(sbom): update software bill of materials`

### Signing (Recommended, Not Required)

If cosign or Sigstore is available, sign the SBOM artifact. This enables downstream consumers to verify provenance. Not required for gate pass.

---

## Security Changelog Governance

### Ownership

- `@security` is the **primary owner** of `{{paths.security_changelog}}`
- `@reviewer` may append entries when it discovers security findings during code review (use `Found by: @reviewer`)
- No other agent may write to this file

### Entry ID Scheme

- Format: `SEC-NNN` (zero-padded, sequential)
- Start at SEC-001
- Never reuse IDs — even for false positives

### Status Lifecycle

```
OPEN ──→ MITIGATED       (fix applied and verified by @security or @qa)
OPEN ──→ ACCEPTED-RISK   (user explicitly accepts with documented justification)
OPEN ──→ FALSE-POSITIVE  (finding was incorrect, document reasoning)
```

No backwards transitions. If a mitigated issue recurs, open a new `SEC-NNN`.

### Required Fields

Every entry must have: severity, category, affected, status, found-by, remediation. CVE field required for dependency vulnerabilities. Resolution date required when status leaves OPEN.

### Valid Categories

`dependency-vuln` · `secret-leak` · `owasp-finding` · `hash-mismatch` · `supply-chain` · `config-risk` · `sast-finding` · `license-risk` · `git-history-secret` · `security-header` · `container-vuln` · `iac-misconfig`

### Dedup Rule

Before appending a new entry, search existing entries for:
- Same CVE ID (exact match)
- Same file + same line + same category (likely same finding)
- Same package + same vulnerability description

If a duplicate is found, **do not** create a new entry. Instead, add a note to the existing entry's Notes field (append, don't edit).

---

## File Hash Registry Management

### What to Track

The minimum tracked file set:

1. **Lock files** — `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `Pipfile.lock`, `poetry.lock`
2. **Agent configuration** — `{{paths.copilot_instructions}}`, all files in `{{paths.instructions_dir}}/`
3. **Skill definitions** — all `{name}.skill.md` files (resolved as `SKILL.md`)
4. **CI/CD** — `.github/workflows/*.yml`, `Dockerfile`, `docker-compose.yml`
5. **Security policy** — `{{paths.security_changelog}}`
6. **Entry points** — `init.py`, `{{paths.web_app_dir}}/index.html` (if exists)

Users may add additional files via `{{security.tracked_files}}` config list.

### Hash Algorithm

SHA-256 only. No MD5 or SHA-1.

### Verification Process

1. Read `{{paths.file_hashes}}`
2. For each tracked file, compute current SHA-256
3. Compare against stored hash
4. Report:
   - **Match** — file is unchanged (no action)
   - **Mismatch** — CRITICAL finding: file changed since last verification
   - **File missing** — CRITICAL: tracked file was deleted
   - **New file** — WARNING: file exists but is not in registry
5. For mismatches, check `git log --oneline -1 <file>` to identify who changed it and when
6. After human review, update registry with new hashes

### When to Update Hashes

- After every sprint completion (Phase 5 in `@sprint-lead`)
- After any security remediation
- After dependency updates
- After CI/CD configuration changes
- On explicit user request

Always commit hash updates separately: `security(hashes): update file integrity registry`

---

## Git History Secret Scanning Baseline

### First Scan

The first run of git history secret scanning generates a baseline file at:
`{{paths.security_reports}}/gitleaks-baseline.json`

All findings from the first scan are placed into the baseline for initial triage. The operator must review each finding and classify it as:
- **Real secret** → CRITICAL, rotate credential immediately, open SEC-NNN entry
- **False positive** → Document in baseline with justification (date, reviewer, reason)

### Subsequent Scans

- Diff against baseline — only **new** findings (not in baseline) are reported
- New secrets found in history → CRITICAL finding + immediate credential rotation recommendation
- Baseline entries are never removed; false positives stay documented

### Baseline Updates

- After triage, commit updated baseline: `security(baseline): update gitleaks baseline`
- Include a summary of findings triaged in the commit body
- Baseline is tracked in `{{paths.file_hashes}}` (hash changes when new entries are triaged)

---

## License Compliance Policy

### Default Lists

**Deny list** (configurable via `{{security.license_denylist}}`):
- `GPL-3.0-only`
- `AGPL-3.0-only`
- `SSPL-1.0`
- `EUPL-1.1`

**Allow list** (configurable via `{{security.license_allowlist}}`):
- `MIT`, `Apache-2.0`, `BSD-2-Clause`, `BSD-3-Clause`, `ISC`, `0BSD`, `CC0-1.0`, `Unlicense`

### Classification Rules

| Dependency Type | License Status | Severity |
|----------------|---------------|----------|
| Production | Denied license | CRITICAL if `{{security.license_gate}}` is `true`, else WARNING |
| Production | Unknown / not listed | SUGGESTION (manual review required) |
| Dev-only | Denied license | WARNING |
| Dev-only | Unknown / not listed | SUGGESTION |
| Any | Allowed license | No finding |

### Gate Behaviour

- Default: `{{security.license_gate}}` = `false` → denied licenses produce WARNING only (non-blocking)
- When `{{security.license_gate}}` = `true` → denied licenses on production dependencies cause gate FAIL
- Dev-only dependencies never cause gate FAIL for license issues

---

## Remediation Decision Tree

When reporting CRITICAL or WARNING findings, classify each into one of 4 remediation cases (per OWASP Vulnerable Dependency Management guidance):

### Case 1 — Patched Version Available

- **Condition:** A newer version of the dependency fixes the vulnerability
- **Action:** Upgrade to the patched version
- **Timeline:** Same sprint for CRITICAL, next sprint for WARNING
- **Effort tag:** Usually `trivial` (version bump in lock file)

### Case 2 — Patch Delayed / Coming

- **Condition:** Maintainer has acknowledged the issue, fix is in progress but not released
- **Action:** Apply compensating control (wrap vulnerable calls, add WAF rule, restrict input). Track the upstream issue URL
- **Timeline:** Re-check each sprint until patch lands
- **Effort tag:** Usually `moderate` (temporary mitigation code)

### Case 3 — No Fix Forthcoming

- **Condition:** Dependency is abandoned, maintainer won't fix, or vulnerability is architectural
- **Action:** Fork and patch, or replace the dependency entirely. **Requires user approval** before proceeding
- **Timeline:** User decides — this may be a multi-sprint effort
- **Effort tag:** Usually `significant` (dependency replacement)

### Case 4 — Zero-Day / Active Exploitation

- **Condition:** Vulnerability is actively exploited in the wild (CISA KEV, public PoC, threat intel)
- **Action:** Emergency response — disable affected functionality, rotate credentials, apply WAF rule. Auto-escalate to P0
- **Timeline:** Immediate (hours, not days)
- **Effort tag:** Varies — initial mitigation is `trivial` to `moderate`, full fix depends on case

### Escalation Matrix

| Case | CRITICAL Severity | WARNING Severity |
|------|-------------------|------------------|
| 1 | P0 — this sprint | P1 — next sprint |
| 2 | P0 — compensating control this sprint | P2 — track upstream |
| 3 | P0 — user decision required now | P2 — user decision next planning |
| 4 | P0 — immediate action (hours) | P0 — immediate action (hours) |

---

## Backlog Integration

### Auto-Filing Findings

When `@security` finds CRITICAL issues that require code changes:

1. Check `{{paths.backlog_ledger}}` for existing items matching the finding (dedup)
2. If no match exists, recommend that `@bug` append a new item:
   - **Type:** `audit-finding`
   - **Source:** `SEC-NNN`
   - **Notes:** CVE ID, OWASP category, or finding summary
3. Actively exploited CVEs → P0 escalation recommendation (immediate sprint inclusion)

### Escalation Rules

| Condition | Action |
|-----------|--------|
| Actively exploited CVE | P0 — recommend immediate sprint inclusion |
| CRITICAL CVE with public PoC | P0 — recommend next sprint at minimum |
| CRITICAL secret exposure | P0 — rotate immediately, then remediate |
| Hash mismatch on CI/CD files | P0 — investigate before any further deploys |
| WARNING findings (3+ same category) | Recommend grouping into single remediation task |

---

## Enforcement (for @reviewer)

When `@reviewer` runs on commits that touch security-relevant files:

- **CRITICAL:** `{{paths.file_hashes}}` was not updated after changing a tracked file
- **CRITICAL:** `{{paths.security_changelog}}` entry was edited (not appended)
- **WARNING:** Dependency version changed without a corresponding `@security` audit
- **SUGGESTION:** New CI/CD file added but not registered in hash registry
