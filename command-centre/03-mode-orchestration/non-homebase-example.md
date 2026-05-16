# Mode 2 — Non-homebase example

> A worked example showing Mode 2 dispatching against a callable
> defined outside agent-homebase substrate. Proves portability:
> Mode 2 depends on the callable contract, not on substrate.

## Scenario

An organisation has an existing library of prompt files used
interactively in their coding-agent runtime. They want to drive a
subset of these prompt files non-interactively from their issue
tracker, without adopting agent-homebase substrate.

They choose to install Mode 2 standalone. They author callable
manifests over their existing prompts and run a Mode 2 dispatcher
against them.

## Consumer-defined callable

```yaml
# callables/draft-rfc.callable.yml
id: my-org.draft-rfc
name: Draft RFC
description: Draft an RFC from a brief in the issue body.
inputs:
  type: object
  required: [brief, issue_id]
  properties:
    brief:
      type: string
      description: "Brief text from issue body."
    issue_id:
      type: string
      description: "Issue identifier for output naming."
outputs:
  - path: "./rfcs/{{issue_id}}.md"
    required: true
verifier: null
runtime_hints:
  invocation:
    type: "file_prompt"
    file: "./prompts/draft-rfc.md"
```

This manifest references an existing prompt file at
`./prompts/draft-rfc.md`. No agent-homebase substrate is involved.

## Dispatcher configuration

```yaml
# .dispatcher.yml
queue_source:
  type: "github-issues"
  repo: "my-org/rfcs"
  label: "draft"
callables_path: "./callables/"
verifier:
  strategy: "artifact-existence"
contract_pins:
  - mode-2-contract-v1
  - protocol-v1
  - callable-contract-v1
```

The dispatcher discovers callables under `./callables/`, picks up
GitHub issues labelled `draft`, and resolves each to a callable by
matching `id` declared in the issue body.

## Expected dispatch flow

1. Operator creates issue #42 with label `draft` and body:
   ```
   callable: my-org.draft-rfc
   brief: "Propose a new authentication flow."
   ```
2. Dispatcher polls; picks up issue #42.
3. State transition: `queued` → `in-progress` (issue gets label
   `in-progress`).
4. Dispatcher resolves `my-org.draft-rfc` callable from
   `./callables/draft-rfc.callable.yml`.
5. Inputs validated: `brief` and `issue_id` (auto-supplied from issue
   metadata) match schema.
6. Callable invoked in the runtime per `runtime_hints.invocation`.
7. Runtime produces `./rfcs/42.md`.
8. Verifier checks: file exists, non-empty, mtime > session start. Pass.
9. State transition: `in-progress` → `done` (issue closed).
10. Dispatcher emits tier-2 return summarising the outcome.

## Verification result

```json
{
  "status": "success",
  "artifacts": [{
    "path": "./rfcs/42.md",
    "required": true,
    "present": true,
    "hash": "sha256:abcd1234..."
  }],
  "verifier": {
    "ran": true,
    "passed": true,
    "reasons": []
  },
  "summary": {
    "callable_id": "my-org.draft-rfc",
    "queue_item": "issue#42",
    "final_state": "done"
  }
}
```

## What this proves

- Mode 2 install required no agent-homebase substrate.
- The callable was authored entirely by the consumer.
- The dispatcher resolved, invoked, and verified per the Mode 2
  contract.
- The same dispatcher could now be pointed at a homebase-substrate
  skill (also a valid callable) without configuration changes.

Mode 2 is portable because it depends on the callable contract, not
on substrate.
