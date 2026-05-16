# Security Policy

## Supported versions

| Version | Status                         |
| ------- | ------------------------------ |
| 2.0.x   | Supported (security + bug fixes) |
| 1.x     | Unsupported                    |
| < 1.0   | Unsupported                    |

When 2.1.0 ships, 2.0.x moves to security-fix-only for six months,
then unsupported.

## Deprecation timeline

| Surface                       | Status                | Removed in |
| ----------------------------- | --------------------- | ---------- |
| `scope:` frontmatter alias    | Deprecated in 2.0.0   | 3.0.0      |
| `jsonschema.RefResolver` path | Deprecated upstream   | 2.1.0      |

The `scope:` → `applies_to` migrator (`tools/migrate-frontmatter.py`)
will continue to work through 3.x.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting:
**https://github.com/j78f88/agent-homebase/security/advisories/new**

Please do **not** open a public issue for security reports.

### What to include

- A description of the issue and the affected component
  (e.g. `init.py` token substitution, a specific schema, a skill).
- The earliest tag/commit you can reproduce on.
- A minimal reproduction (a config file or a substrate snippet is ideal).
- The impact you observed (information leak, arbitrary file write,
  determinism break, supply-chain risk, etc.).

### What to expect

- Acknowledgement within 7 days.
- A triage decision (accept / wontfix / out-of-scope) within 14 days.
- For accepted reports, a fix or mitigation timeline at triage.
- Credit in the release notes unless you ask otherwise.

## Out of scope

- Vulnerabilities in **end-user projects** that consume this substrate.
  Those are the adopter's responsibility; the substrate is a set of
  Markdown instructions, not an executing service.
- Issues that require an attacker who already controls the
  contributor's machine (e.g. modifying `.githooks/`, editing
  `config/project.config.example.yml` locally).
- Theoretical prompt-injection findings without a concrete impact
  path. The project does not execute arbitrary user input.

## Build-time guarantees

`init.py` performs security validation on every config value before
substitution. The build is deterministic: two runs with the same
config must produce byte-identical `resolved/` output. The
release CI (`.github/workflows/release.yml`) enforces this on every
push and tag.
