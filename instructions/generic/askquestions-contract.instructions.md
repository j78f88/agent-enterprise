---
id: instruction.askquestions-contract
kind: instruction
version: 1.0.0
applies_to: '**'
description: askquestions-contract instruction
---

# askQuestions Contract

Shared rules for agents that use the `vscode/askQuestions` tool (frontmatter declaration) or `#tool:askQuestions` (body invocation).

## When to Use

- Clarifying questions and scoping decisions
- Decision points, workflow gates, and session exits
- Any yes/no or multi-choice decision

**Never render decision menus as plain text lists.** Hard rule.

## When NOT to Use

- Open-ended questions where presets don't make sense (freeform only)

## Rules

- Group related questions into a single `askQuestions` call (up to 3–4 questions).
- Provide 2–4 predefined options per question; mark the most likely as recommended.
- Always allow freeform input alongside options.
- Use concise headers (max 50 chars) and short question text (one sentence).
- For yes/no decisions, provide explicit "Yes" / "No" options.

## Vocabulary Note

This file uses neutral terms ("decision point", "workflow gate", "session exit"). Individual agents define their own context-specific vocabulary (e.g., `@planner` uses "CHECKPOINT", `@sprint-lead` uses "EXIT POINT"). The shared rules apply regardless of local terminology.
