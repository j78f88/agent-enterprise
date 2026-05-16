# Mode 2 — Install contract

> Standalone install. Mode 1 substrate is NOT assumed present.

## Preconditions

- Consumer has at least one callable conforming to
  [callable-contract.md](../01-protocols/callable-contract.md), from
  any source (own authoring, Mode 1 substrate, third-party).
- A queue source exists (issue tracker, file, API).
- A dispatcher implementation is available, satisfying
  [`contract.md`](contract.md).
- Pins recorded: `mode-2-contract-vN + protocol-vN`.

## Steps

1. Place callables where the dispatcher can discover them (e.g.,
   `callables/` in the consumer repo).
2. Configure the dispatcher with:
   - Queue source connection details.
   - Callable discovery path(s).
   - Verifier strategy (artifact-existence default + per-callable
     hooks).
   - State-transition mapping for the queue source.
3. Wire the dispatcher into its runtime (CI job, scheduled task,
   long-running service — implementation choice).
4. Record pins in `.mode-2-pins` (or equivalent).
5. Smoke test by dispatching one work item end-to-end.

## Postconditions

- Dispatcher picks up new queue items and transitions them through
  `queued → in-progress → done|rejected|failed` per the contract.
- Verifier blocks `done` transitions on failure.
- Each dispatch produces a tier-2-or-3 return.
- Pin file records the contract tags in use.

## Exit codes (dispatcher CLI, if provided)

Reference vocabulary for any dispatcher exposing a CLI:

| Code | Meaning |
| --- | --- |
| 0 | Dispatch succeeded; verifier passed |
| 1 | Configuration error (queue, callable, verifier) |
| 2 | Input validation failed against callable schema |
| 3 | Callable invocation failed |
| 4 | Verifier failed |
| 5 | State transition failed (queue source rejected update) |

## Test plan

1. Author a test callable whose verifier deliberately fails; dispatch
   it; confirm state transitions to `rejected`, NOT `done`.
2. Author a passing test callable; dispatch it; confirm state
   transitions to `done` only after verifier pass.
3. Submit malformed inputs; confirm typed validation error and no
   invocation.
4. Time-out a long-running callable; confirm state transitions to
   `failed` with diagnostic.

## Rollback

- Stop the dispatcher process.
- In-flight items remain in their current state in the queue; manual
  reconciliation may be needed if the dispatcher crashed mid-dispatch.
- No substrate or registry rollback required (Mode 2 doesn't touch
  either).

## Mode 1 → Mode 2 upgrade-in-place addendum

A project already running Mode 1 adds Mode 2 by:

1. Adding the dispatcher per the steps above.
2. Registering substrate-provided skills as callables (they already
   conform to the callable contract).
3. No changes to the Mode 1 install — the substrate continues to be
   used interactively as before; the dispatcher uses the same
   callables non-interactively.
