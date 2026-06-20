# Choreography Guide (Mode 3)

Mode 3 coordinates a program of works across multiple projects. It runs above
projects rather than inside them: each project satisfies the shared protocol
contracts, while a coordinator workspace owns the registry, cadence, meta-agents,
and audit records.

The contract of record is
[`mode-3-contract-v1`](../command-centre/04-mode-choreography/contract.md).
This guide documents the repo's reference coordinator under
`command-centre/04-mode-choreography/reference-impls/registry-coordinator/`.

---

## When to use Mode 3

Use Mode 3 when you need to answer portfolio questions such as:

- Which projects are using this substrate?
- Which projects are pinned to an older substrate version?
- Which projects are affected by a contract change?
- Which project-local patterns should be harvested back into the substrate?
- Which projects are Mode 1 only vs Mode 1 + Mode 2?

Do not use Mode 3 as a replacement for a project backlog or dispatcher. It is a
coordinator layer, not a task runner.

---

## Workspace shape

A coordinator workspace should be its own directory or repo:

```text
coordinator-workspace/
├── registry.yml
├── harvest-cadence.yml
├── meta_agents/
│   ├── audit.agent.md
│   ├── framework-dev.agent.md
│   └── harvest.agent.md
├── audit/
│   └── <cycle-id>.md or .json
└── .mode-3-pins
```

Coordinated projects remain independent. They only need to satisfy the project
contract and declare their pins in the registry.

---

## Registry

`registry.yml` is the single source of truth for the program of works. It
conforms to [`registry-v1`](../schemas/registry-v1.schema.json), which embeds
project entries conforming to [`project-v1`](../schemas/project-v1.schema.json).

Minimal shape:

```yaml
version: "1"
coordinator:
  id: my-coordinator
  name: "My Coordinator"
  substrate_version: "2.0.0"
projects:
  - id: project-a
    name: "Project A"
    repo: "github:owner/project-a"
    mode_level: team
    substrate_version: "2.0.0"
    contract_pins:
      - protocol-v1
      - mode-1-contract-v1
    owner: "team-a"
```

Mixed fleets are valid: one registry can contain `mode_level: team` and
`mode_level: orchestration` projects.

---

## Reference coordinator smoke

Install dependencies first:

```bash
pip install -r requirements.txt
```

Run the reference conformance smoke:

```bash
python command-centre/04-mode-choreography/reference-impls/registry-coordinator/conformance_test.py
```

Expected:

```text
OK — mode-3-contract-v1 conformance: all checks pass
```

This proves the reference coordinator:

- loads a single registry file;
- validates registry/project schema conformance;
- detects substrate-version drift;
- surfaces impact for a contract-pin bump;
- handles mixed-fleet registries;
- exposes the three required meta-agents;
- runs a harvest cycle and writes a non-empty audit record.

---

## Relationship to Modes 1 and 2

Mode 3 is independent:

- It does not require a project to run Mode 1.
- It does not require a project to run Mode 2.
- It can coordinate projects that use custom substrate, as long as they satisfy
  the project contract.

Typical progression:

1. Mode 1: embed agents/instructions into a project.
2. Mode 2: add non-interactive queue dispatch to a project.
3. Mode 3: coordinate several projects and harvest learning back into the
   substrate.

---

## Operational contract

A Mode 3 coordinator should:

1. Keep registry entries current.
2. Run drift checks on a declared cadence.
3. Surface impact when substrate contracts change.
4. Run harvest cycles and write audit records.
5. Apply the promotion contract before moving project-local learning into the
   shared substrate.
6. Leave coordinated projects untouched unless the operator explicitly chooses
   to apply changes there.

---

## Related docs

- [Mode 3 contract](../command-centre/04-mode-choreography/contract.md)
- [Mode 3 install contract](../command-centre/04-mode-choreography/install-contract.md)
- [Registry schema](../command-centre/04-mode-choreography/registry-schema.md)
- [Meta-agents](../command-centre/04-mode-choreography/meta-agents.md)
- [Harvest cadence](../command-centre/04-mode-choreography/harvest-cadence.md)
- [Promotion contract](../command-centre/05-promotion-contract.md)
- [Work Loop](WORK_LOOP.md)
