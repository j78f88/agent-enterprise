# Glossary

> One-line pointer dictionary. Full definitions live in the linked
> contracts.

- **Callable** — unit of work invoked by Mode 2; defined by
  [callable-contract.md](../01-protocols/callable-contract.md).
- **Contract** — file defining conformance for a layer. Stable,
  versioned with tags, supersedes any reference implementation.
- **Protocol** — a contract under
  [`01-protocols/`](../01-protocols/), shared across modes.
- **Substrate** — the skills/instructions/agents/profiles/build that
  satisfies the Mode 1 contract. Reference implementation is the
  agent-homebase repo root.
- **Delivery mode** — Mode 1 (team), Mode 2 (orchestration), or
  Mode 3 (choreography). Each standalone. See
  [three-modes.md](three-modes.md).
- **Reference implementation** — worked example proving a contract is
  satisfiable. Replaceable; contracts are not.
- **Promotion** — moving a project-local artifact into substrate after
  harvest evaluation. Governed by
  [`05-promotion-contract.md`](../05-promotion-contract.md).
- **Harvest cadence** — declared recurring schedule on which Mode 3
  runs harvest cycles. See
  [harvest-cadence.md](../04-mode-choreography/harvest-cadence.md).
- **Mode level** — registry field declaring which modes a project
  consumes (`team`, `orchestration`). See
  [registry-schema.md](../04-mode-choreography/registry-schema.md).
- **Contract tag** — git tag identifying a contract version (e.g.,
  `mode-1-contract-v1`, `protocol-v1`). See
  [versioning-and-tags.md](../01-protocols/versioning-and-tags.md).
- **Coordinator** — Mode 3 implementation maintaining a registry,
  running harvest cycles, and providing meta-agents.
- **Dispatcher** — Mode 2 implementation pulling work from a queue and
  invoking callables.
- **Meta-agent** — a Mode 3 callable operating across the program
  rather than inside one project. The three required ones are
  `@framework-dev`, `@harvest`, `@audit`. See
  [meta-agents.md](../04-mode-choreography/meta-agents.md).
- **Verifier** — hook a dispatcher invokes to confirm a callable's
  result. May be `null` (artifact-existence-only).
- **Pin file** — consumer-side file recording the substrate version
  and contract tags claimed for conformance.
- **Audit record** — append-only markdown file produced by each Mode 3
  harvest cycle.
