# Security Changelog

Append-only log of all security findings. Entries are never edited or deleted — only new entries are appended. Status changes are recorded as new lines within the entry's Notes field.

Owned by: `@security` (primary), `@reviewer` (may append findings from code review)

| Field | Required | Description |
|-------|----------|-------------|
| ID | Yes | SEC-NNN (sequential, zero-padded) |
| Date | Yes | YYYY-MM-DD finding was recorded |
| Severity | Yes | CRITICAL / WARNING / SUGGESTION |
| Category | Yes | dependency-vuln / secret-leak / owasp-finding / hash-mismatch / supply-chain / config-risk / sast-finding / license-risk / git-history-secret / security-header / container-vuln / iac-misconfig |
| CVE | If applicable | CVE-YYYY-NNNNN |
| Affected | Yes | package@version or file path |
| Status | Yes | OPEN / MITIGATED / ACCEPTED-RISK / FALSE-POSITIVE |
| Found by | Yes | @security (audit) / @security (scheduled) / @reviewer (code review) |
| Remediation | Yes | Description of fix or mitigation |
| Resolution date | When resolved | YYYY-MM-DD |
| Notes | Optional | Additional context, status change history |

---

<!-- Append new entries below this line. Do not edit entries above. -->
