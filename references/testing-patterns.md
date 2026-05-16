# Testing Patterns

Cross-skill reference for `@qa` and any agent that writes or evaluates tests.

## Test structure

- One concept per test. Name the test after the behaviour, not the function.
- Arrange → Act → Assert. Keep each phase visually separated.
- Prefer table-driven cases over copy-pasted near-duplicate tests.

## Coverage expectations

- Pure logic: aim for **≥90% line + branch**.
- Glue / wiring code: aim for **≥70%** with the rest exercised in integration.
- New code added in a sprint must not lower the project's overall coverage.

## Snapshot vs assertion

- Use **explicit assertions** for behaviour you care about.
- Reserve **snapshots** for large stable output (rendered HTML, generated
  schemas). Review every snapshot diff — never blindly update.

## Integration patterns

- Boundary tests live where the boundary is (API handler, DB adapter, IPC
  shim). Mock only what crosses the network or disk.
- Each integration test must clean up its own state (transactions, temp
  dirs, fake clocks). Tests must pass in any order.

## E2E patterns

- Test user journeys, not implementation details.
- Wait on observable state, never on `sleep(n)`.
- Capture artifacts (video, trace, logs) on failure.

## Anti-patterns

- Tests that pass because they assert nothing.
- Tests that mock the function under test.
- Tests gated behind `skip` with no linked ticket.
- Coverage farming (asserting on `toBeDefined()` after a call).
