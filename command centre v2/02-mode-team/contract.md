# Mode 1 — Team contract

> **Contract tag:** `mode-1-contract-v1`.
>
> Defines what it means for a substrate to provide a working project
> team — a library of callables (skills, instructions, agents,
> profiles) usable interactively from a coding agent.

## Purpose

Mode 1 is the foundation. A substrate satisfying this contract provides
everything a single project needs to work with a coding agent in an
organised way: shared skills, shared instructions, role-shaped agents,
and a profile system for project-specific configuration.

Mode 1 is consumable standalone. No dispatcher, no coordinator, no
registry required.

## Capabilities a Mode 1 substrate must provide

A conforming substrate exposes:

1. **A skills library.** A collection of named, discoverable units of
   work. Each skill is a [callable](../01-protocols/callable-contract.md).
2. **An instructions library.** Path-scoped rules (generic + configurable)
   that apply across skills.
3. **An agents library.** Role-shaped agent definitions (e.g.,
   `architect`, `qa`, `security`) that compose skills.
4. **A profile system.** A way for a consumer project to supply token
   values and select which substrate elements to enable.
5. **A build step.** Deterministic resolution of profile + substrate →
   deployable artifacts under a build output folder.
6. **Validation.** Frontmatter validation per [frontmatter-spec.md](../01-protocols/frontmatter-spec.md);
   security validation of all configured values.
7. **Multi-runtime support.** The build produces artifacts loadable by
   at least two coding-agent runtimes (e.g., Copilot + Claude Code).

## Conformance checklist

A substrate claims `mode-1-contract-v1` conformance if and only if:

- [ ] Every skill file declares required frontmatter ([spec](../01-protocols/frontmatter-spec.md)).
- [ ] Every skill is a valid [callable](../01-protocols/callable-contract.md).
- [ ] Instructions declare `applies_to` path globs and are honoured by
      the build.
- [ ] Agents reference skills by `id`; missing references are build
      errors.
- [ ] Profiles are validated against a schema; required tokens missing
      from a profile are build errors.
- [ ] The build is deterministic: same inputs → byte-identical outputs.
- [ ] Build artifacts load successfully in at least two runtimes.

A conformance test under [`reference-substrate.md`](reference-substrate.md)
demonstrates these for the in-repo reference.

## Reference substrate

The reference substrate is the root of agent-homebase itself:
[`skills/`](../../skills/), [`instructions/`](../../instructions/),
[`agents/`](../../agents/), [`profiles/`](../../profiles/),
[`schemas/`](../../schemas/), with the build implemented in
[`init.py`](../../init.py).

A consumer may use this substrate as-is, fork it, or write their own.
See [reference-substrate.md](reference-substrate.md) for the mapping
and the conformance test.

## Independence guarantees

Mode 1 has zero runtime dependencies on Mode 2 or Mode 3. Specifically:

- A Mode 1 install never produces a dispatcher.
- A Mode 1 install never produces or consumes a registry.
- A Mode 1 install never invokes meta-agents.
- A Mode 1 substrate file never imports from `03-mode-orchestration/`
  or `04-mode-choreography/`.

Mode 1 depends only on [`01-protocols/`](../01-protocols/).

## Versioning

Breaking changes to this contract bump `mode-1-contract-v1` →
`mode-1-contract-v2`. N-1 coexistence per
[ADR 0003](../decisions/0003-unified-semver-plus-contract-tags.md).

Examples of breaking changes:
- Removing a required capability above.
- Changing the build determinism requirement.
- Removing multi-runtime support requirement.

Non-breaking: adding new optional capabilities, additional runtimes
beyond the required two.
