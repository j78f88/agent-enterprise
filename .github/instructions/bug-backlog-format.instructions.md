---
id: instruction.bug-backlog-format
kind: instruction
version: 1.0.0
applies_to: '**'
description: bug-backlog-format instruction
applyTo: '**'
---

# Bug Backlog Format

Single schema and lifecycle specification for `{{paths.bug_backlog}}`.

> **Note:** `{{paths.bug_backlog}}` itself contains the format specification in its header. This instruction file is the agent-readable mirror of that spec. When they diverge, the backlog file wins and this file is updated to match.

> **Status tracked in docs/planning/BACKLOG_LEDGER.md — this file holds reproduction context only.**

## Entry Format

```markdown
### BUG-NNN — Short description

- **Severity:** 🔴 Blocks / 🟡 Degraded / 🟢 Cosmetic / ⚪ Edge case
- **Area:** [component or feature area]
- **Reported:** YYYY-MM-DD
- **Ledger:** ITEM-NNN
- **Screenshots:** [filename(s)] or None
- **Description:** What happens, repro steps, expected vs actual
```

## ID Assignment

`{{ids.bug_prefix}}-NNN`, zero-padded to 3 digits, sequential. Read `{{paths.bug_backlog}}` to find the highest existing N; assign N+1.

## Writer Discipline

| Agent | Permission |
| --- | --- |
| `@bug` | Appends new entries below `<!-- @bug appends new entries below this line -->` marker. Adds `Ledger: {{ids.item_prefix}}-NNN` cross-reference. Never edits existing entries. |
| All other agents | No write access. Status changes are tracked in `{{paths.backlog_ledger}}`, not in this file. |
