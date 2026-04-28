# File Integrity Registry

SHA-256 hash registry for security-critical files. Managed by `@security`. Any hash mismatch is a CRITICAL finding until reviewed and explained.

Last updated: YYYY-MM-DD
Updated by: @security (initial)

| File | SHA-256 | Last Verified | Changed By |
|------|---------|---------------|------------|

<!-- 
Tracked file categories:
  1. Lock files — package-lock.json, yarn.lock, pnpm-lock.yaml, etc.
  2. Agent config — copilot-instructions.md, all instruction files
  3. Skill definitions — all SKILL.md files
  4. CI/CD — .github/workflows/*.yml, Dockerfile, docker-compose.yml
  5. Security policy — policies/*.rego, SECURITY_CHANGELOG.md
  6. Entry points — init.py, index.html

Update rules:
  - Hash algorithm: SHA-256 only (no MD5, no SHA-1)
  - Update after: sprint completion, security remediation, dependency updates, CI/CD changes
  - Always commit separately: security(hashes): update file integrity registry
  - Mismatches are CRITICAL until explained via git log review
-->
