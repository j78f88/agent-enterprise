# Claude Code Setup

Agent-enterprise emits a native invocation surface for each supported platform, selected by `editor.target` in your project config:

| Platform | How agents are invoked | Deploy location |
|---|---|---|
| GitHub Copilot (VS Code) | `@agent-name` in chat | the `paths.skills_deploy_dir` directory |
| Claude Code | `/agent-name` slash commands + native subagents | the `paths.claude_commands` and `paths.claude_agents` directories |
| Cursor | rules + commands | `.cursor/rules/` and the `paths.cursor_commands` directory |
| OpenAI Codex | `AGENTS.md` convention | managed block in the `paths.codex_agents_md` file |

This file covers the Claude Code surfaces in detail, with a short section on Cursor and Codex at the end. The full artifact map lives in `docs/PLATFORMS.md` in the library repo.

## Slash commands

When you run `python init.py --config config/project.config.example.yml --deploy`, the deploy step **automatically seeds the `paths.claude_commands` directory** with one `.md` file per agent. Claude Code reads the filename (without `.md`) as the slash-command name — so `planner.md` becomes `/planner`. This seeding runs for every `editor.target` whenever `paths.claude_commands` is set.

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

## Native subagents

When `editor.target` is `claude-code`, `both`, or `all`, the deploy step also seeds the `paths.claude_agents` directory (default `.claude/agents`) with one native subagent file per agent:

```
.claude/agents/planner.md
.claude/agents/qa.md
...
```

Each file carries Claude Code subagent frontmatter (`name` and `description`). The `tools` field is deliberately omitted — the agent wrappers use VS Code tool identifiers that have no clean mapping onto Claude Code tool names, so each subagent receives Claude Code's default (full) tool set. Claude Code delegates to a subagent automatically when its description matches the task, or explicitly when you name it.

Slash commands and subagents are complementary: a command is something you invoke; a subagent is something Claude Code dispatches work to.

## Configuring the paths

Both directories are set in your project config: `paths.claude_commands` (default `.claude/commands`) and `paths.claude_agents` (default `.claude/agents`). Change them if your project uses different locations — the deploy step always reads the configured paths. Seeding is deterministic and idempotent: re-running deploy with unchanged inputs rewrites identical bytes.

## If you are using Claude Code only

Set `editor.target: "claude-code"` in your config. Agent wrappers (`.agent.md` files) are still generated — every target gets them, and the subagent files are rendered from them — but skills keep `user-invocable: true` (the skill-suppression step is vscode-only), and no Cursor or Codex surfaces are written.

## Cursor and Codex

- **Cursor** (`editor.target: "cursor"` or `"all"`) — instruction files are emitted as `.cursor/rules/*.mdc` rules, and the `paths.cursor_commands` directory (default `.cursor/commands`) is seeded with one command file per agent, the same way `paths.claude_commands` is seeded.
- **Codex** (`editor.target: "codex"` or `"all"`) — a managed block containing the agent roster is merged into the file named by `paths.codex_agents_md` (default `AGENTS.md`), between `agent-enterprise:begin` / `agent-enterprise:end` markers. Content outside the markers is never modified, and re-running the merge with unchanged inputs is byte-identical.
