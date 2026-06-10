# Mode 2 — Install contract

> Standalone install. Mode 1 substrate is NOT assumed present.

## Preconditions

- At least one callable conforming to
  [callable-contract.md](../01-protocols/callable-contract.md) from
  any source (own authoring, Mode 1 substrate, third-party).
- A queue source (issue tracker, file, API).
- A dispatcher implementation satisfying [`contract.md`](contract.md).
- Pins recorded: `mode-2-contract-vN + protocol-vN`.

## Steps

1. Place callables where the dispatcher can discover them (e.g.,
   `callables/`).
2. Configure the dispatcher with: queue-source connection, callable
   discovery path(s), verifier strategy (artifact-existence default
   plus per-callable hooks), state-transition mapping for the queue.
3. Wire the dispatcher into its runtime (CI job, scheduled task, or
   long-running service — implementation choice).
4. Record pins in `.mode-2-pins`.
5. Smoke-test by dispatching one work item end-to-end.

## Postconditions

- Dispatcher picks up new queue items and transitions them through
  `queued → in-progress → done|rejected|failed` per the contract.
- Verifier blocks `done` transitions on failure.
- Each dispatch produces a tier-2-or-3 return.
- Pin file records the contract tags.

## Mode 1 → Mode 2 upgrade-in-place

A project already running Mode 1 adds Mode 2 by following the steps
above. Substrate-provided skills already conform to the callable
contract and can be registered as-is. The Mode 1 install is
unchanged — the dispatcher invokes the same callables
non-interactively.

## Rollback

Stop the dispatcher process. In-flight items remain in their current
queue state; reconcile manually if the dispatcher crashed mid-dispatch.
No substrate or registry rollback required.

---

## Supported implementation

> Informative addition per
> [ADR 0008](../decisions/0008-supported-mode-implementations.md)
> criterion 4. The contract text above is unchanged and remains the
> interface — any conforming dispatcher satisfies this install contract.

The repo's supported Mode 2 implementation is the
`src/mode2_dispatcher/` package with the root CLI `dispatch.py`
(`python dispatch.py {run|status|requeue|validate-callables}`). It
satisfies every step above out of the box: file-queue source
(`queue/inbox/*.yml`), callable discovery from `*.callable.yml`
sidecars and `callable-v1` skill frontmatter, ghost-done verification,
contract-legal state transitions with a durable journal and
crash-resume, and `.mode-2-pins` enforcement.

Adopter documentation: [docs/ORCHESTRATION.md](../../docs/ORCHESTRATION.md).
The reference implementation in
[`reference-impls/file-queue-dispatcher/`](reference-impls/file-queue-dispatcher/)
stays frozen as contract pedagogy (ADR 0008 criterion 5).
