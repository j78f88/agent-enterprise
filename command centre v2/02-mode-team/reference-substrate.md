# Mode 1 — Reference substrate

> The in-repo example of a substrate satisfying `mode-1-contract-v1`.

## Mapping

The agent-homebase root *is* the reference substrate. Mode 1
capabilities map as follows:

| Capability | Location |
| --- | --- |
| Skills library | [`skills/`](../../skills/) |
| Instructions — generic | [`instructions/generic/`](../../instructions/generic/) |
| Instructions — configurable | [`instructions/configurable/`](../../instructions/configurable/) |
| Agents library | [`agents/`](../../agents/) |
| Profile system | [`profiles/`](../../profiles/), [`config/`](../../config/) |
| Build step | [`init.py`](../../init.py) |
| Validation | `init.py` + [`schemas/`](../../schemas/) + [`policies/`](../../policies/) |
| Build output | [`resolved/`](../../resolved/) |

## What's in scope

- Token resolution from profile values.
- Frontmatter validation per [frontmatter spec](../01-protocols/frontmatter-spec.md).
- Schema validation of profiles and registry-shaped inputs.
- Determinism guarantees per [docs/DETERMINISM_GUIDE.md](../../docs/DETERMINISM_GUIDE.md).
- Multi-runtime artifact output (Copilot, Claude Code, Cursor, Codex).

## What's out of scope

- Runtime dispatcher behaviour (Mode 2).
- Cross-project coordination (Mode 3).
- Project-specific content. The substrate ships zero project content.
- Authoring tools beyond a markdown editor and the build.

## Replaceability — using a different substrate

The reference substrate is one valid implementation. A consumer may:

- Keep the contract, replace the build engine (e.g., Node-based).
- Keep the build engine, replace skill/agent/instruction content.
- Replace both, retaining only the contract tag conformance claim.

The Mode 1 contract is the API; the substrate is the implementation.

## Conformance test

The reference substrate is verified against the Mode 1 contract by:

1. [`tests/test_init.py`](../../tests/test_init.py) — build
   determinism, frontmatter validation, schema validation.
2. [`tests/test_contracts.py`](../../tests/test_contracts.py) —
   contract-shape assertions.
3. Runtime smoke tests loading built artifacts in at least two
   runtimes.

Any alternative substrate claiming Mode 1 conformance should provide
equivalent tests against its own implementation.
