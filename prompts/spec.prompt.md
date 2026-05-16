---
description: "Lifecycle command — turn a fuzzy idea into a written spec and a vetted design."
mode: chat
---

# /spec

Use this when a request is fuzzy and needs to become a written specification
plus a vetted technical design before any planning starts.

## Flow

1. Invoke `@pm` to capture stakeholders, acceptance criteria, success metrics,
   in-scope / out-of-scope boundaries, and open questions.
2. Hand off to `@architect` to write or update the relevant ADR(s) with
   context, decision, consequences, and alternatives considered.

## Artifacts

- A spec doc (PM-owned) under `docs/planning/` describing what success looks like.
- One or more ADRs under `docs/architecture/` describing how it will be built.

## Exit

Spec and ADR are linked from each other and ready to be handed to `@planner`.
Open questions are either answered or assigned to an owner with a due date.
