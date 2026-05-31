# Security Agent — Report & Changelog Formats

## Report Format

```
## Security Audit — [date]

### Scan Summary
- Dependencies scanned: N
- CVEs found: N (N critical, N warning)
- Actively exploited: N
- Secrets detected: N
- OWASP findings: N
- Hash mismatches: N
- Supply chain risks: N
- SBOM generated: yes/no (format)
- SAST findings: N (N critical, N warning)
- Git history secrets: N
- License violations: N
- Security header issues: N
- Container vulnerabilities: N
- IaC misconfigurations: N

### CRITICAL (must fix before merge/deploy)
1. [CVE-YYYY-NNNNN] package@version — description. Remediation: upgrade to >=X.Y.Z

### WARNING (should fix, not blocking)
1. [OWASP-A03] file:line — description. Remediation: use framework escaping

### SUGGESTION (hardening opportunity)
1. [SUPPLY-CHAIN] package — description

### Remediation Guidance

| Case | Condition | Action | Timeline |
|------|-----------|--------|----------|
| 1 | Patched version available | Upgrade to `>=X.Y.Z` | Same sprint (CRITICAL), next sprint (WARNING) |
| 2 | Patch delayed | Compensating control + track upstream | Re-check each sprint |
| 3 | No fix forthcoming | Fork & patch or replace — requires user approval | User decides |
| 4 | Zero-day / active exploitation | Disable functionality, rotate creds, WAF rule | Immediate |

### Hash Verification
- Tracked/Matches/Mismatches/New untracked

### Changelog Entries Added
- SEC-NNN: description

### Comparison with Previous Audit
- New/Resolved/Unchanged
```

---

## Machine-Readable Summary (JSON)

Output after the human-readable report for `@sprint-lead`:

```json
{
  "agent": "security",
  "timestamp": "ISO-8601",
  "gate": "PASS | FAIL",
  "gate_reason": "description",
  "counts": { "critical": 0, "warning": 0, "suggestion": 0 },
  "cves": { "total": 0, "actively_exploited": 0, "with_patch": 0 },
  "secrets": 0,
  "hash_mismatches": 0,
  "supply_chain_risks": 0,
  "sbom_generated": true,
  "sast_findings": 0,
  "git_history_secrets": 0,
  "license_violations": 0,
  "security_header_issues": 0,
  "container_vulnerabilities": 0,
  "iac_misconfigurations": 0,
  "changelog_entries_added": [],
  "comparison": { "new": 0, "resolved": 0, "unchanged": 0 }
}
```

**Gate logic — FAIL if:**
- Any CRITICAL finding exists
- Any actively exploited CVE (regardless of severity)
- Any secret detected (current or git history)
- Any unexplained hash mismatch
- Any CRITICAL SAST finding
- Any CRITICAL container vulnerability
- Any CRITICAL IaC misconfiguration
- License denylist match on production dep AND `False` is true

---

## Security Changelog Format

Append-only at `docs/security/SECURITY_CHANGELOG.md`. Entries are **never** modified or deleted.

```markdown
## SEC-NNN — [date] — [category]

- **Severity:** CRITICAL | WARNING | SUGGESTION
- **Category:** dependency-vuln | secret-leak | owasp-finding | hash-mismatch | supply-chain | config-risk | sast-finding | license-risk | git-history-secret | security-header | container-vuln | iac-misconfig
- **CVE:** CVE-YYYY-NNNNN (if applicable)
- **Affected:** package@version or file path
- **Status:** OPEN | MITIGATED | ACCEPTED-RISK | FALSE-POSITIVE
- **Found by:** @security (audit) | @security (scheduled) | @reviewer (code review)
- **Remediation:** description
- **Resolution date:** YYYY-MM-DD (when status changes from OPEN)
- **Notes:** additional context
```

**Status transitions:** OPEN → MITIGATED | ACCEPTED-RISK | FALSE-POSITIVE. No backwards transitions. Recurrence → new SEC-NNN entry.

---

## File Hash Registry Format

At `docs/security/FILE_HASHES.md`:

```markdown
# File Integrity Registry

Last updated: YYYY-MM-DD
Updated by: @security (audit | scheduled | manual)

| File | SHA-256 | Last Verified | Changed By |
|------|---------|---------------|------------|
| package.json | a1b2c3... | 2026-04-28 | @sprint-lead (sprint 5) |
```

**Update rules:** First run generates all hashes. Subsequent runs compare, report, then update after review. Include who/what caused changes. Commit with: `security(hashes): update file integrity registry`
