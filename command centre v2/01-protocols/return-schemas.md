# Return schemas

> **Contract tag:** `return-schemas-v1`. Part of `protocol-v1`.
>
> Three tiers of structured return shape used by callables, dispatchers,
> and coordinators. Canonical JSON Schemas live at
> [`../../schemas/`](../../schemas/); this file is the human-readable
> contract.

## Tier 1 — minimal

Simplest possible result. Used by callables whose only output is one
or more files on disk; the return shape just confirms what was written.

```json
{
  "status": "success | failure",
  "artifacts": ["./path/to/file1", "./path/to/file2"],
  "message": "optional human-readable summary"
}
```

Canonical schema: [`schemas/subagent-return-tier1.schema.json`](../../schemas/subagent-return-tier1.schema.json).

## Tier 2 — standard

Adds verifier output, error details, and machine-readable summary
fields. Default tier for skills, dispatcher results, and meta-agent
outputs.

```json
{
  "status": "success | failure | partial",
  "artifacts": [{
    "path": "./reports/foo.md",
    "required": true,
    "present": true,
    "hash": "sha256:..."
  }],
  "verifier": {
    "ran": true,
    "passed": true,
    "reasons": []
  },
  "summary": {
    "items_processed": 12,
    "items_skipped": 0
  },
  "message": "optional human-readable summary",
  "errors": []
}
```

Canonical schema: [`schemas/subagent-return-tier2.schema.json`](../../schemas/subagent-return-tier2.schema.json).

## Tier 3 — extended

Adds telemetry, decision logs, and structured handoff fields. Used by
long-running callables, meta-agents, and any callable whose output
feeds another callable in a chain.

```json
{
  "status": "success | failure | partial",
  "artifacts": [...],
  "verifier": {...},
  "summary": {...},
  "telemetry": {
    "started_at": "2026-05-16T10:00:00Z",
    "ended_at": "2026-05-16T10:04:32Z",
    "token_usage": { "input": 8421, "output": 1203 },
    "tool_calls": 17
  },
  "decisions": [
    { "at": "2026-05-16T10:01:14Z", "chose": "...", "because": "..." }
  ],
  "handoff": {
    "next_callable": "my-org.review-prd",
    "inputs": { "prd_path": "./prd/foo.md" },
    "context": ["./decisions/2026-05-16-architecture.md"]
  },
  "errors": []
}
```

Canonical schema: [`schemas/subagent-return-tier3.schema.json`](../../schemas/subagent-return-tier3.schema.json).

## When each tier applies

| Use case | Tier |
| --- | --- |
| Single-shot skill writing one file | 1 |
| Standard skill with declared verifier | 2 |
| Skill in a chain or handoff | 3 |
| Meta-agent (`@harvest`, `@audit`) | 3 |
| Dispatcher result aggregation | 2 |
| Coordinator (Mode 3) cross-project report | 3 |

A callable may declare a higher tier than strictly required (e.g., a
simple skill returning tier 3 to capture telemetry). Returning a lower
tier than declared is a contract violation.

## Cross-mode usage

Return schemas are the shared currency between modes:

- A Mode 1 skill returns tier 1 or 2.
- A Mode 2 dispatcher consumes those returns and produces tier 2 or 3.
- A Mode 3 coordinator consumes Mode 2 returns and produces tier 3
  cross-project reports.

No mode invents its own return shape. This is what makes the modes
composable without coupling.

## Versioning

Breaking changes to any tier bump `return-schemas-v1` →
`return-schemas-v2`. Non-breaking additions (new optional fields, new
enum values) are allowed within a version.

Adding a new tier (e.g., a tier 4) is not breaking provided existing
tiers are unchanged.
