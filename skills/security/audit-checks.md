# Security Agent — Audit Checks

Run all applicable checks. You **never** stop if one fails — run all and report everything.

## 1. Dependency Vulnerability Scan

Scan project dependencies for known CVEs using `npm audit --json`, `pip audit --format=json`, or `safety check --json`.

For each vulnerability: record CVE ID, CVSS score, affected package/version, check for patched version, classify severity (CVSS ≥ 9.0 → CRITICAL, ≥ 7.0 → WARNING, ≥ 4.0 → SUGGESTION), and check if the vulnerable code path is reachable.

## 2. Active Exploit Research

For CRITICAL or WARNING CVEs: search CISA KEV catalog, NVD, GitHub Security Advisories. Check for public PoC exploits. Flag actively exploited CVEs with `[ACTIVELY EXPLOITED]` — these override all other priority.

## 3. Secret Detection

Scan for accidentally committed secrets. Patterns: API keys (`sk-`, `pk_`, `api_key`), tokens (`ghp_`, `gho_`, `xoxb-`), AWS (`AKIA`), Azure (connection strings), generic (`password=`, `secret=`, `private_key`), high-entropy base64 strings, committed `.env` files.

Exclusions: test fixtures with fake values, env var references, documentation examples. Every real secret is CRITICAL.

## 4. OWASP Top 10 Code Patterns

Scan application code for patterns matching OWASP Top 10 (2021):

| # | Category | What to search for |
|---|----------|--------------------|
| A01 | Broken Access Control | Missing auth checks, IDOR patterns |
| A02 | Cryptographic Failures | Weak hashing, hardcoded keys, HTTP for sensitive data |
| A03 | Injection | Unsanitized input in SQL, shell, HTML |
| A04 | Insecure Design | Missing rate limiting, no CSRF, sensitive data in URLs |
| A05 | Security Misconfiguration | Debug mode, default creds, permissive CORS |
| A06 | Vulnerable Components | (covered by dependency scan) |
| A07 | Auth Failures | Weak passwords, missing MFA, JWT without expiry |
| A08 | Data Integrity Failures | Unsigned updates, untrusted deserialization |
| A09 | Logging Failures | Sensitive data in logs, missing audit trail |
| A10 | SSRF | User-controlled URLs in server requests |

Focus on {{project.language}} / {{project.framework}} specific vectors.

## 5. File Integrity Verification

Compare current file hashes against `{{paths.file_hashes}}`. Track: `package.json`, lock files, `{{paths.copilot_instructions}}`, instruction files, skill files, `init.py`, CI/CD workflows, container configs.

Any mismatch → CRITICAL. New untracked file → WARNING. After review, update registry.

## 6. Supply Chain Audit

Check for: recent ownership transfers, install scripts (`preinstall`/`postinstall`), typosquatting, unpinned dependencies, non-standard registries.

## 7. Infrastructure & Configuration Review

If CI/CD config exists: check for secrets in workflows, branch protection references, `pull_request_target` triggers, Docker image pinning, IAM/RBAC permissions.

## 8. SBOM Generation

Generate Software Bill of Materials using `{{commands.sbom_generate}}`, CycloneDX, or Syft. Output to `{{paths.sbom_output}}`. Unable to generate → SUGGESTION. Incomplete → WARNING. Never gate-fail on SBOM alone.

## 9. SAST Scan

Run language-aware static analysis (`{{commands.sast}}`, Bandit, or Semgrep). Scan for injection, insecure deserialization, path traversal, hardcoded credentials, framework-specific vulns. Dedup with check 4 (prefer SAST findings over grep findings for same file/line/category). Tool not installed → SUGGESTION, never gate-fail.

## 10. Git History Secret Scanning

Scan full git history using `{{commands.secret_scan_history}}` or trufflehog. First run generates baseline. Subsequent runs diff against baseline. Any new secret in history → CRITICAL (requires rotation). Tool not installed → SUGGESTION.

## 11. License Compliance

Check dependency licenses against allow/deny lists using `{{commands.license_check}}`, pip-licenses, or SBOM. Default deny: `GPL-3.0-only`, `AGPL-3.0-only`, `SSPL-1.0`. Default allow: `MIT`, `Apache-2.0`, `BSD-2-Clause`, `BSD-3-Clause`, `ISC`, `0BSD`. Override via `{{security.license_denylist}}` and `{{security.license_allowlist}}`. Production dep with denied license → CRITICAL if `{{security.license_gate}}` is true, else WARNING.

## 12. HTTP Security Headers (Web Projects Only)

Only run if `{{paths.web_app_dir}}` is configured. Check: `Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`. All findings WARNING or SUGGESTION (never CRITICAL).

## 13. Container Image Scanning (Conditional)

Only if Dockerfile/docker-compose exists. Use `{{commands.container_scan}}` or Grype. Scan for OS-level/language-level CVEs, Dockerfile misconfigs, base image freshness. CRITICAL CVE → CRITICAL. HIGH CVE → WARNING. Root/stale → WARNING/SUGGESTION.

## 14. IaC Scanning (Conditional)

Only if IaC files exist (`.tf`, `.bicep`, `helm/`, etc.). Use `{{commands.iac_scan}}`, KICS, or Trivy config. Check for permissive security groups, unencrypted storage, public resources, missing logging, hardcoded secrets, wildcard IAM. Public+no auth or wildcard IAM → CRITICAL. Missing encryption/logging → WARNING.
