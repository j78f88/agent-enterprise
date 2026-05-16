---
id: instruction.batch-report
kind: instruction
version: 1.0.0
applies_to: '**'
description: batch-report instruction
---

# Batch Report Contract

Shared rules for agent workflows that produce non-destructive artifacts (drafts, validation records, research docs, handoff manifests, rejection entries).

**Loading:** this contract is referenced by individual prompt files. It does not auto-load via `applyTo`. Prompts that adopt it inline the operational rules and cite this file as the canonical spec.

## Principle

**Save by default. Gate only irreversible actions.** The user's attention is the scarce resource — spend it on spot-checks, not sign-offs.

## Non-Destructive Actions — auto-save, report at end

These proceed without asking for approval:

- Draft to `docs/planning/drafts/`
- Validation record to `docs/planning/validation/`
- Research doc to `docs/planning/research/`
- Handoff manifest to `docs/planning/_handoffs/`
- REJ-NNN entry to `docs/planning/HANDOFF_REJECTIONS.md`

Save as soon as the artifact is drafted. Do NOT hold files in chat awaiting approval.

## Irreversible Actions — gated, require explicit approval

These MUST use `#tool:askQuestions` before executing:

- Promote draft to `sprints/`
- Commit or merge
- Append to `docs/NON_GOALS.md`
- Append to `docs/planning/ROADMAP.md`

## End-of-Workflow Summary

After completing a workflow (or a logical batch of work), present ONE summary message. This is plain markdown — do NOT wrap it in `#tool:askQuestions`.

Shape:

```
**What I did**
- {Action 1} — {one-line reasoning}
- {Action 2} — {one-line reasoning}

**Files saved**
- `{path/to/file-1}` — {what it is}
- `{path/to/file-2}` — {what it is}

**Spot-check these** (where my judgment was least certain)
- `{path/to/file}` § {section} — {why this needs your eyes}

Push back on any decision, request a revision, or redirect.
```

### Rules

1. **What I did** — every non-trivial choice the agent made without asking. Skip mechanical defaults.
2. **Files saved** — every file written or modified, one-phrase description each.
3. **Spot-check these** — 1–3 items where the agent's confidence was lowest or the user's domain knowledge matters most. If a workflow produces more than 3 uncertain decisions, that's a signal a clarifying question should have been asked earlier — not dumped as spot-checks at the end.
4. **Push back or redirect** — always end with this line.

## Interaction with askQuestions

`askquestions-contract.instructions.md` still governs interactive UI. This contract narrows WHEN agents invoke it:

| Use askQuestions                                                  | Do NOT use askQuestions                                   |
| ----------------------------------------------------------------- | --------------------------------------------------------- |
| Gated actions (irreversible list above)                           | Confirming saves of non-destructive artifacts             |
| Genuine ambiguity where no reasonable default exists              | Presenting intermediate work for approval before saving   |
| Clarifying questions where the agent needs user input to continue | Sequential approve/revise/discard gates on completed work |
| Session-end navigation menus                                      | "Are you sure?" confirmations on auto-save actions        |

## Handoff Manifests

YAML handoff manifests (`docs/planning/_handoffs/`) are agent-to-agent coordination artifacts — separate from the batch summary. Continue writing manifests per each agent's existing protocol.

Add a `session-starter` field to every manifest:

```yaml
session-starter: "Continue <slug> — <completed-stage> is done, pick up at <next-stage>. Read <this-manifest-path> for context."
```

This gives the user a copy-paste one-liner to start the next session. Agents adopt this field when their agent file is migrated to this contract. Existing manifests work without it.
