# Security Checklist

Cross-skill reference for `@security` and any agent that ships code.

## OWASP Top 10 — quick checks

1. **Broken access control** — every authenticated route checks ownership.
2. **Cryptographic failures** — no plaintext secrets, no MD5/SHA-1 for
   integrity, TLS enforced end-to-end.
3. **Injection** — parameterized queries, never string-built SQL or shell.
4. **Insecure design** — threat-model new features; document trust
   boundaries.
5. **Security misconfiguration** — disable debug endpoints in prod,
   minimal CORS, secure cookie flags.
6. **Vulnerable components** — dependency scanner clean (`npm audit`,
   `pip-audit`, `cargo audit`, etc.).
7. **Identification & auth failures** — MFA on admin, lockouts on brute
   force, no plaintext session IDs in URLs.
8. **Software & data integrity** — verify signatures on downloaded
   artifacts, pin lockfiles, CI from trusted source.
9. **Logging & monitoring failures** — auth events, privilege escalations,
   and failed access attempts all logged.
10. **Server-side request forgery** — allowlist outbound hosts; never
    fetch user-supplied URLs from a privileged context.

## Dependency audit steps

- Run the language-native audit (`npm audit`, `pip-audit`, etc.).
- Cross-check CVE IDs against the GitHub Advisory DB.
- For each CRITICAL/HIGH: file under `starters/SECURITY_CHANGELOG.md` with
  CVE link, affected version range, fix version, exploit status.

## Secret detection patterns

- High-entropy strings in non-test files.
- Common shapes: `AKIA[0-9A-Z]{16}`, `ghp_[A-Za-z0-9]{36}`,
  `xox[baprs]-`, `-----BEGIN .* PRIVATE KEY-----`.
- `.env*` committed to git. `*.pem`, `*.key`, `*.p12` outside of fixtures.
- Hardcoded `password = "…"`, `Bearer …` literals, JDBC URLs with creds.

## Reporting

Every finding includes: severity (CRITICAL / WARNING / SUGGESTION),
evidence (file + line, CVE link, or command output), and a concrete
remediation step. No finding without evidence.
