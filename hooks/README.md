# hooks/

VS Code session hooks that run at key lifecycle points.

## Configuration

`hooks.json` defines available hooks and their interpreters:

```json
{
  "session-start": {
    "script": "hooks/session-start.sh",
    "interpreter": "bash",
    "blocking": false
  }
}
```

## Available hooks

| Hook | Script | Purpose |
| --- | --- | --- |
| `session-start` | `session-start.sh` | Warn when source files under `skills/` or `instructions/` are newer than their `resolved/` counterparts |

All hooks are non-blocking by default — they emit warnings but do not
prevent the session from starting.
