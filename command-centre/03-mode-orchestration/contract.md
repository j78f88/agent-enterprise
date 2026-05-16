# Mode 2 — Orchestration contract

> **Contract tag:** `mode-2-contract-v1`.
>
> Defines what a dispatch / verifier layer must do to satisfy Mode 2.
> Runtime- and substrate-agnostic. A conforming implementation can
> dispatch any [callable](../01-protocols/callable-contract.md),
> whether from agent-homebase substrate or elsewhere.

## Purpose

Mode 2 takes a queue of work (typically issues or tickets) and runs
each item to a verified result without continuous human supervision.
It sits above Mode 1 (or any substrate providing callables) and below
Mode 3 (or any program coordinator).

## Dispatcher responsibilities

A conforming dispatcher MUST:

1. **Source work items.** Pull from a queue (issue tracker, file, API).
   Queue source is configurable.
2. **Resolve to a callable.** Map each work item to a registered
   callable using the callable's `id`. Resolution is explicit; no
   implicit selection.
3. **Validate inputs.** Validate work-item inputs against the
   callable's input schema. Validation failure short-circuits with a
   typed error.
4. **Invoke the callable.** Within the appropriate runtime, with
   correct context.
5. **Capture the return.** Conforming to the callable's declared return
   tier ([return-schemas.md](../01-protocols/return-schemas.md)).
6. **Trigger the verifier.** If the callable declares a verifier hook,
   invoke it on the captured return.
7. **Transition state.** Update the work item's state in the source
   queue based on the verified result. Never transition to "done" on
   session end alone.
8. **Emit a dispatcher return.** Tier 2 or 3, summarising what was
   dispatched and the verified outcome.

## Verifier responsibilities

A verifier MUST:

1. **Check artifact existence.** Every required output path must exist
   with non-empty content.
2. **Check artifact freshness.** Artifacts must have been written
   during the current dispatch session (e.g., mtime > session start,
   or fresh git diff).
3. **Run the declared verifier hook.** If present.
4. **Return pass/fail with reasons.** Reasons are machine-readable
   (codes) and human-readable (strings).

A verifier MUST NOT pass solely because the dispatched session ended.
This is the most important guarantee in Mode 2 (Anti-Fragility
Pattern 1 — Ghost-Done).

## Required state transitions

| From | Trigger | To |
| --- | --- | --- |
| `queued` | Dispatcher picks up | `in-progress` |
| `in-progress` | Callable returns + verifier passes | `done` |
| `in-progress` | Callable returns + verifier fails | `rejected` |
| `in-progress` | Callable times out or errors | `failed` |
| `rejected` | Manual or automatic re-queue | `queued` |

A dispatcher MUST NOT skip transitions. It MUST NOT transition from
`in-progress` to `done` without verifier pass.

## Callable invocation contract

Dispatcher invokes per [callable-contract.md](../01-protocols/callable-contract.md):

- Inputs match `inputs` schema.
- Outputs are produced at declared paths.
- Return matches declared tier.

Dispatchers MAY add runtime-specific invocation metadata
(`runtime_hints`) but must not require the callable to know about
them.

## Return schema usage

- Each dispatched callable returns at its declared tier.
- The dispatcher itself returns tier 2 or tier 3 summarising the
  dispatch.
- Aggregated returns (multiple callables in one dispatch session) use
  tier 3 with handoff fields.

## Conformance checklist

A dispatcher claims `mode-2-contract-v1` conformance if and only if:

- [ ] Implements every dispatcher responsibility above.
- [ ] Implements verifier responsibilities (directly or via a pluggable
      verifier).
- [ ] Honours required state transitions; rejects ghost-done
      transitions.
- [ ] Returns tier 2 or 3 results.
- [ ] Includes a worked test against at least one non-substrate
      callable (see [non-homebase-example.md](non-homebase-example.md)).
- [ ] Documents its queue source(s) and how to configure them.

## Independence guarantees

- Mode 2 depends only on [`01-protocols/`](../01-protocols/).
- Mode 2 does NOT require Mode 1 substrate. A consumer may dispatch
  their own callables (declared per the callable contract).
- Mode 2 does NOT require Mode 3. A standalone dispatcher works on a
  single project with no registry.
- Mode 2 reference impls do not import from Mode 1 or Mode 3 source
  trees.

## Versioning

Breaking changes bump `mode-2-contract-v1` → `mode-2-contract-v2`.
Examples of breaking: changing required state transitions, removing
verifier requirement, weakening ghost-done protection.

N-1 coexistence per [ADR 0003](../decisions/0003-unified-semver-plus-contract-tags.md).
