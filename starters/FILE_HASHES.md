# File Integrity Registry

SHA-256 hash registry for security-critical files. Managed by `@security`. Any hash mismatch is a CRITICAL finding until reviewed and explained.

Last updated: YYYY-MM-DD
Updated by: @security (initial)

## Hash chain

Each row's **Prior Hash** is the first 8 characters of SHA-256(prior row's `SHA-256` field, lowercase hex, no spaces). The first data row uses `GENESIS`. The chain is tamper-evident: re-ordering, inserting, or modifying any row invalidates every row after it. Validate with `python scripts/verify-hash-chain.py starters/FILE_HASHES.md`.

| File | SHA-256 | Prior Hash | Last Verified | Changed By |
|------|---------|------------|---------------|------------|

<!--
Tracked file categories:
  1. Lock files — package-lock.json, yarn.lock, pnpm-lock.yaml, etc.
  2. Agent config — copilot-instructions.md, all instruction files
  3. Skill definitions — all {name}.skill.md files (resolved as SKILL.md)
  4. CI/CD — .github/workflows/*.yml, Dockerfile, docker-compose.yml
  5. Security policy — policies/*.rego, SECURITY_CHANGELOG.md
  6. Entry points — init.py, index.html

Update rules:
  - Hash algorithm: SHA-256 only (no MD5, no SHA-1)
  - Update after: sprint completion, security remediation, dependency updates, CI/CD changes
  - Always commit separately: security(hashes): update file integrity registry
  - Mismatches are CRITICAL until explained via git log review

Chain rules:
  - First data row: Prior Hash = GENESIS
  - Every subsequent row: Prior Hash = first 8 chars of sha256(prior row's SHA-256 field, lowercase hex)
  - Never reorder rows. Append only.
  - To revoke a row, append a new row noting the revocation; do not delete history.
  - Run `python scripts/verify-hash-chain.py starters/FILE_HASHES.md` before every commit that
    touches this file. CI must also run it.
-->
