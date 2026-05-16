# ADR 0006 — No sync CLI; just registry file + harvest script

> **Status:** Accepted.

## Context

v1 specified a Mode 3 sync CLI with six commands:
`register / deploy / diff / status / harvest / unregister`. Audit of
what each command would actually do:

| Command | Work performed | Native equivalent |
| --- | --- | --- |
| `register` | Append project entry to registry | `git add registry.yml` |
| `deploy` | Pull substrate version into a project | `git submodule update` or `git pull` |
| `diff` | Show drift between project and substrate | `git diff` / `git submodule status` |
| `status` | List projects + pinned versions | `git submodule foreach 'git describe'` |
| `harvest` | Propose project-local artifact for substrate | **Irreducible work — needs a schema** |
| `unregister` | Remove project from registry | `git rm` line from `registry.yml` |

Five of six commands are thin wrappers over git. Owning them creates
surface area without adding capability — a direct Anti-Fragility
Pattern 6 violation (execution-layer ownership).

## Decision

Mode 3 ships **two artifacts**, not a CLI:

1. A **registry file** (`registry.yml` per
   [`04-mode-choreography/registry-schema.md`](../04-mode-choreography/registry-schema.md))
   listing projects in the program of works.
2. A **harvest script** (per
   [`04-mode-choreography/harvest-cadence.md`](../04-mode-choreography/harvest-cadence.md)
   and [`05-promotion-contract.md`](../05-promotion-contract.md))
   implementing the only operation that has no good native equivalent.

Git operations remain native. Consumers are expected to be comfortable
with `git submodule`, `git pull`, and `git diff` — these are not
exotic.

A convenience wrapper (Justfile, PowerShell module, shell aliases) MAY
be added by a consumer or a reference implementation but is not part of
the Mode 3 contract.

## Consequences

**Positive**
- Mode 3's owned surface area is one file format and one script.
- No CLI binary to ship, version, package, or document beyond what git
  already provides.
- Consumers can integrate with their existing tooling (GitHub Actions,
  Azure DevOps, custom scripts) without adapting to a bespoke CLI.

**Negative**
- A consumer expecting a polished `cc deploy` experience will not find
  one. The trade-off is explicit and documented.
- The harvest script does need to exist and be maintained. Its scope is
  bounded by the promotion contract.

## Alternatives considered

- **Full six-command CLI (v1 design).** Rejected — Pattern 6 violation.
- **Single CLI that wraps only harvest.** Acceptable; basically the
  same as "a script." Naming distinction only.
- **No tooling at all; consumers write their own everything.**
  Rejected — the promotion workflow has enough structure that one
  reference script saves every consumer reinventing it.
