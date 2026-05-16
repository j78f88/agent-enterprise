# Mode 2 — File-queue reference dispatcher

> **Conformance:** [`mode-2-contract-v1`](../../contract.md). Verified
> by `conformance_test.py`.

A minimal, runtime-agnostic dispatcher that satisfies every responsibility in
[`command-centre/03-mode-orchestration/contract.md`](../../contract.md):

1. Sources work items from a YAML inbox queue (`fixtures/inbox/`).
2. Resolves each item to a registered callable by `id`.
3. Validates inputs against the callable's `inputs` JSON Schema.
4. Invokes the callable as a Python entry point (the fixture callables
   are plain Python functions).
5. Captures a [tier-2 return](../../../01-protocols/return-schemas.md).
6. Runs the verifier (artifact existence + freshness + optional hook).
7. Transitions queue state (`queued → in-progress → done | rejected | failed`).
8. Emits a tier-3 dispatch summary at the end.

The reference impl exists to prove the contract, not to be a production
queue. It is ~200 lines of pure-Python with no external service deps.

## Run

```powershell
python conformance_test.py
```

Exit code 0 = every contract checkbox satisfied against the three-item
fixture queue (one success, one verifier-fail, one input-validation-fail).
