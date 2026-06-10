# Claude Code Setup

Agent-enterprise supports two agent invocation mechanisms depending on your editor:

| Platform | How agents are invoked | Deploy directory |
|---|---|---|
| GitHub Copilot (VS Code) | `@agent-name` in chat | `.github/agents/` |
| Claude Code | `/agent-name` slash commands | the `paths.claude_commands` directory |

When you run `python init.py --config config/project.config.example.yml --deploy`, the deploy step **automatically seeds the `paths.claude_commands` directory** with one `.md` file per agent. Claude Code reads the filename (without `.md`) as the slash-command name — so `planner.md` becomes `/planner`.

## How it works

```bash
python init.py --config config/project.config.example.yml --deploy
```

This creates files under the `paths.claude_commands` directory (default `.claude/commands`), such as:

```
.claude/commands/planner.md
.claude/commands/sprint-lead.md
.claude/commands/reviewer.md
...
```

After deploy, open any file in Claude Code and type `/planner` (or another agent name) to invoke it.

## Configuring the commands path

The slash-command directory is set via `paths.claude_commands` in your project config (default: `.claude/commands`). Change it if your project uses a different location — the deploy step always reads the configured path.

## If you are using Claude Code only

Set `editor.target: "claude-code"` in your config. Agent wrapper generation (`.agent.md` files for VS Code) is skipped, but the `paths.claude_commands` seeding still runs on `--deploy`.
