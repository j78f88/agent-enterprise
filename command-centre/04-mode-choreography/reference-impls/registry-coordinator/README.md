# Mode 3 — Registry reference coordinator

> **Conformance:** [`mode-3-contract-v1`](../../contract.md). Verified
> by `conformance_test.py`.

A minimal coordinator that satisfies every responsibility in
[`command-centre/04-mode-choreography/contract.md`](../../contract.md):

1. Loads a single ``registry.yml`` (validated against
   [`schemas/registry-v1.schema.json`](../../../../schemas/registry-v1.schema.json)).
2. Detects drift between each project's `substrate_version` and the
   current enterprise tag.
3. Reports impact when a contract pin is bumped.
4. Hosts the three minimum meta-agents (`@framework-dev`, `@harvest`,
   `@audit`) as instruction stubs with callable manifests.
5. Runs a (toy) harvest cycle and writes an audit record.
6. Handles mixed-fleet registries (one `team` + one `orchestration`)
   by construction.

Pure stdlib + jsonschema + PyYAML; no service deps.

## Run

```powershell
python conformance_test.py
```

Exit code 0 = every contract checkbox satisfied against the fixture
registry.
