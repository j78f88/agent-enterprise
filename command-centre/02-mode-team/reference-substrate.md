# Mode 1 — Reference substrate

> Pointer page. The agent-enterprise root *is* the reference substrate
> satisfying `mode-1-contract-v1`. See
> [contract.md](contract.md) for the normative contract.

## Mapping

| Capability | Location |
| --- | --- |
| Skills library | [`skills/`](../../skills/) |
| Instructions — generic | [`instructions/generic/`](../../instructions/generic/) |
| Instructions — configurable | [`instructions/configurable/`](../../instructions/configurable/) |
| Agents library | [`agents/`](../../agents/) |
| Profile system | [`profiles/`](../../profiles/), [`config/`](../../config/) |
| Build step | [`init.py`](../../init.py) |
| Validation | `init.py` + [`schemas/`](../../schemas/) |
| Build output | [`resolved/`](../../resolved/) |
| Honesty contract *(recommended, not required by Mode 1)* | [`instructions/generic/honesty-contract.instructions.md`](../../instructions/generic/honesty-contract.instructions.md) |

## Replaceability

The reference is one valid implementation. A consumer may replace the
build engine, the substrate content, or both — only the contract-tag
conformance claim matters.

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
