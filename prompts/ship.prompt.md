---
description: "Lifecycle command — validate, document, and release the sprint."
mode: chat
---

# /ship

Use this after `/review` to validate end-to-end, update docs, and release.

## Flow

1. Invoke `@qa` to run the full quality pipeline (typecheck, lint, unit,
   integration, coverage, E2E). Gate results are recorded in `PLAN.md`.
2. Invoke `@docs` to update README, changelog, and any user-facing docs to
   reflect the sprint's changes. Every linked file is verified to exist;
   every example command is run as written.
3. Tag and release per the project's release process.

## Artifacts

- Updated changelog entry.
- Updated README / user docs.
- A green `PLAN.md` with every gate showing a result + timestamp.
- A release tag and (optionally) a release note.

## Exit

The sprint is in production. `@sprint-lead` runs the retro and the loop is
ready to start again at `/spec`.
