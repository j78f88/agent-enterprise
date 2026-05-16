# Glossary

> Terminology dictionary for v2. Definitions are normative within this
> workbench.

## Callable

A unit of work that can be invoked, declares its inputs and outputs,
and reports a verifiable result. Defined by
[callable-contract.md](../01-protocols/callable-contract.md). Examples:
Mode 1 skills, consumer-authored prompt-file wrappers, MCP tool
invocations with declared schemas.

## Contract

A file under this workbench that defines the shape of conformance for
a specific layer (protocol, mode, install, promotion). Contracts are
stable, versioned with tags, and supersede any reference
implementation.

## Protocol

A contract that sits in [`01-protocols/`](../01-protocols/). Protocols
are shared across modes. The protocol set is small and slow-changing
by design. See [ADR 0002](../decisions/0002-protocols-as-shared-root.md).

## Substrate

The collection of skills, instructions, agents, profiles, schemas, and
build tooling that satisfies the Mode 1 contract. The agent-homebase
repo root is one substrate (the reference). Consumers may use it or
provide their own.

## Delivery mode

One of the three top-level products: Mode 1 (team), Mode 2
(orchestration), Mode 3 (choreography). Each is standalone, defined
by a contract folder, and consumable independently. See
[three-modes.md](three-modes.md).

## Reference implementation

A worked example that proves a contract is satisfiable. Lives under
`reference-impl/` (Modes 2 and 3) or at the repo root (Mode 1).
Reference implementations are replaceable; contracts are not.

## Promotion

The act of moving a project-local artifact into substrate after
harvest evaluation. Governed by [`05-promotion-contract.md`](../05-promotion-contract.md).
Three outcomes per candidate: `promoted`, `parked`, `rejected`.

## Harvest cadence

The declared recurring schedule on which Mode 3 runs harvest cycles.
Not a phase. Defined in [harvest-cadence.md](../04-mode-choreography/harvest-cadence.md).
See [ADR 0005](../decisions/0005-harvest-as-steady-state.md).

## Mode level

A registry-entry field declaring which delivery modes a project
consumes: `team` (Mode 1 only) or `orchestration` (Mode 1 + Mode 2).
Used by Mode 3 meta-agents to adapt behaviour per project. See
[registry-schema.md](../04-mode-choreography/registry-schema.md).

## Contract tag

A git tag identifying a specific contract version. Format:
`<contract>-vN` (e.g., `mode-1-contract-v1`, `protocol-v1`). Bumps
independently of repo semver. Consumers pin to contract tags when they
want stability against a specific contract regardless of other repo
changes. See [versioning-and-tags.md](../01-protocols/versioning-and-tags.md).

## Coordinator

A Mode 3 implementation maintaining a registry, running harvest
cycles, and providing meta-agents. May be CI workflow, script, or
service. Defined by [04-mode-choreography/contract.md](../04-mode-choreography/contract.md).

## Dispatcher

A Mode 2 implementation pulling work from a queue and invoking
callables. Defined by [03-mode-orchestration/contract.md](../03-mode-orchestration/contract.md).

## Meta-agent

A Mode 3 callable operating across the program of works rather than
inside one project. The three required ones are `@framework-dev`,
`@harvest`, `@audit`. See [meta-agents.md](../04-mode-choreography/meta-agents.md).

## Verifier

A hook invoked by a Mode 2 dispatcher to confirm a callable's result.
May be `null` (artifact-existence-only verification). Critical for
blocking ghost-done state transitions.

## Pin file

A consumer-side file (e.g., `.agent-homebase-pins`, `.mode-2-pins`,
`.mode-3-pins`) recording which substrate version and contract tags
the consumer claims conformance to. Read by Mode 3 coordinators during
drift detection.

## Audit record

A markdown file produced by each Mode 3 harvest cycle recording
inputs, candidates, decisions, metric value, and skipped cycles.
Append-only and under version control.
