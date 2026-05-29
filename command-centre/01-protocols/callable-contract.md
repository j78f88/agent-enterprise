# Callable contract

> **Contract tag:** `callable-contract-v1`. Part of `protocol-v1`.
>
> Defines what Mode 2 dispatches against. Runtime- and substrate-
> agnostic. A callable is any unit of work that can be invoked, produces
> declared outputs, and reports a verifiable result.

## Purpose

Mode 2 (orchestration) needs to dispatch units of work without knowing
whether those units are agent-enterprise skills, a consumer's own prompt
files, MCP tool invocations, or something else. This contract is the
shape every callable must satisfy.

## Required fields

Every callable declares the following in its source file (typically
frontmatter or a sidecar manifest):

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Unique identifier within the substrate. Stable across versions. |
| `name` | string | Human-readable name. |
| `description` | string | One-sentence purpose, used by dispatchers for routing. |
| `inputs` | object schema | What the callable consumes (see Input schema below). |
| `outputs` | array | Declared artifact paths and/or return tier (see Output declaration). |
| `verifier` | string or null | Reference to a verifier hook. `null` means "existence of declared outputs is sufficient." |
| `runtime_hints` | object | Optional. E.g., `{ "tools": ["web", "git"], "max_iterations": 10 }`. Dispatchers may ignore. |

## Input schema

The `inputs` field is a JSON Schema object describing required and
optional inputs. Dispatchers validate inputs against this schema before
invocation. Validation failure short-circuits the dispatch with a typed
error.

Minimum acceptable form:

```yaml
inputs:
  type: object
  required: [task]
  properties:
    task:
      type: string
      description: "What the callable should do."
```

## Output declaration

Every callable declares what it produces. Two forms are allowed:

**Form A — artifact paths.** The callable promises to write specific
files. Dispatchers verify the paths exist with fresh content after
invocation.

```yaml
outputs:
  - path: "./reports/{{task_id}}.md"
    required: true
  - path: "./logs/{{task_id}}.log"
    required: false
```

**Form B — return tier.** The callable returns a structured result
conforming to one of the [return tiers](return-schemas.md).

```yaml
outputs:
  - return_tier: 2
```

A callable may declare both. Both are then required for verification
to pass.

## Verifier hook

A verifier is an optional callable (also conforming to this contract!)
that takes the dispatch result and returns pass/fail with reasons.
Dispatchers run the verifier after artifact-existence checks.

A `verifier: null` callable is verified solely by artifact existence
and return tier conformance. This is the common case for simple
skills.

## Return schema reference

Return tiers are defined in [return-schemas.md](return-schemas.md).
Callables that opt into a return tier promise their structured output
will validate against that tier's JSON Schema.

## Non-enterprise callable example

A consumer with their own prompt-file ecosystem can wrap one as a
Mode 2 callable by writing a small manifest:

```yaml
# my-org/callables/draft-prd.callable.yml
id: my-org.draft-prd
name: Draft PRD
description: Draft a product requirements document from a brief.
inputs:
  type: object
  required: [brief_path]
  properties:
    brief_path: { type: string }
outputs:
  - path: "./prd/{{slug}}.md"
    required: true
verifier: null
runtime_hints:
  invocation:
    type: "file_prompt"
    file: "./prompts/draft-prd.md"
```

The consumer's dispatcher (any Mode 2 reference impl) can now invoke
this callable identically to an enterprise skill. No coupling to enterprise
substrate.

## Versioning

Breaking changes to this contract bump `callable-contract-v1` →
`callable-contract-v2`. Substrate must support N-1 for at least one
minor release cycle ([ADR 0003](../decisions/0003-unified-semver-plus-contract-tags.md)).

Non-breaking additions (new optional fields, additional runtime hints)
are allowed within a version.
