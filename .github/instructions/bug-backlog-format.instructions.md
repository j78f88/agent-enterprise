---
id: instruction.bug-backlog-format
kind: instruction
version: 1.0.0
applies_to: '**'
description: bug-backlog-format instruction
applyTo: '**'
paths:
- '**'
---

# Bug Backlog Format

Single schema and lifecycle specification for `docs/planning/BUG_BACKLOG.md`.

> **Note:** `docs/planning/BUG_BACKLOG.md` itself contains the format specification in its header. This instruction file is the agent-readable mirror of that spec. When they diverge, the backlog file wins and this file is updated to match.

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

`BUG-NNN`, zero-padded to 3 digits, sequential. Read `docs/planning/BUG_BACKLOG.md` to find the highest existing N; assign N+1.

## Writer Discipline

| Agent | Permission |
| --- | --- |
| `@bug` | Appends new entries below `<!-- @bug appends new entries below this line -->` marker. Adds `Ledger: ITEM-NNN` cross-reference. Never edits existing entries. |
| All other agents | No write access. Status changes are tracked in `docs/planning/BACKLOG_LEDGER.md`, not in this file. |
