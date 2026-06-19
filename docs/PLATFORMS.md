# Platform Guide

What each `editor.target` value emits, where it lands, and how each platform
consumes it. Every claim on this page is pinned by
`tests/test_platform_emission.py` — if a cell says an artifact exists, a test
builds that target and asserts it.

---

## Choosing a target

Set `editor.target` in your `project.config.yml`:

| Value | Platforms covered |
|:------|:------------------|
| `"vscode"` | GitHub Copilot (VS Code) |
| `"claude-code"` | Claude Code |
| `"cursor"` | Cursor |
| `"codex"` | OpenAI Codex |
| `"both"` | GitHub Copilot + Claude Code |
| `"all"` | Everything above |

All targets share the same build: `init.py` resolves `{{tokens}}` from your
config, validates frontmatter, and writes `resolved/`. The target controls
which platform-native artifacts are emitted on top of that. In the supported
embedded topology (`<adopter>/skills-library`), run from `skills-library/` with
`python init.py --config config/project.config.example.yml --deploy --deploy-root ..`
so deploy artifacts land in the adopter root while `resolved/` stays in the
library checkout. Cursor rules (`.cursor/rules/*.mdc`) are generated during the
build phase; when `--deploy` is used they are also rooted under `--deploy-root`.

---

## Artifact matrix

Emitted by `python init.py --config config/project.config.example.yml --deploy --deploy-root ..`
for an embedded checkout. Every row is written during the `--deploy` step
except Cursor rules (`*.mdc`), which the build phase emits and follows
`--deploy-root` when deploy mode is active:

| Artifact | Path token (default) | vscode | claude-code | cursor | codex | both | all |
|:---------|:---------------------|:------:|:-----------:|:------:|:-----:|:----:|:---:|
| Skill bundles | `paths.skills_deploy_dir` (`.github/agents/`) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Agent wrappers (`*.agent.md`) | `paths.skills_deploy_dir` (`.github/agents/`) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Shared instructions | `paths.instructions_dir` (`.github/instructions`) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Claude Code slash commands | `paths.claude_commands` (`.claude/commands`) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Claude Code native subagents | `paths.claude_agents` (`.claude/agents`) | — | ✓ | — | — | ✓ | ✓ |
| Cursor rules (`*.mdc`) | fixed: `.cursor/rules/` | — | — | ✓ | — | — | ✓ |
| Cursor commands | `paths.cursor_commands` (`.cursor/commands`) | — | — | ✓ | — | — | ✓ |
| Codex `AGENTS.md` managed block | `paths.codex_agents_md` (`AGENTS.md`) | — | — | — | ✓ | — | ✓ |
| Skill suppression (`user-invocable: false`) | n/a | ✓ | — | — | — | — | — |

Notes on the matrix:

- Agent wrappers are generated for **every** valid target — the per-platform
  emitters (subagents, commands, managed block) all consume them downstream.
- Slash-command seeding is not gated by target: any config that sets
  `paths.claude_commands` gets the directory seeded, so a mixed team on a
  `vscode` build still gets working `/commands` in Claude Code.
- Skill suppression is strictly vscode-only. On other targets, skills keep
  `user-invocable: true` so the platform can discover them directly.
- A path token left unset skips that emission; an absolute path or a path with
  `..` aborts the deploy. Keep config paths relative to `--deploy-root`; use
  `--deploy-root ..` for embedded installs instead of path-token traversal.

---

## GitHub Copilot (`vscode`)

Copilot discovers agents from `.agent.md` files in `paths.skills_deploy_dir`
and invokes them as `@agent-name` in chat (e.g. `@planner`, `@qa`).

- Agent wrappers carry `name`, `description`, `tools`, and optional
  `agents`/`model`/`handoffs` frontmatter generated from each skill's
  `agent:` metadata.
- Instruction files get their `applies_to` scope rewritten to Copilot's
  `applyTo` field (comma-joined glob string).
- Skills that have an agent wrapper are set to `user-invocable: false` in the
  resolved output, so users see one entry point (`@agent`) instead of a
  duplicate `/skill`. This suppression fires **only** on the `vscode` target.

## Claude Code (`claude-code`)

Claude Code consumes two surfaces:

- **Slash commands** — `paths.claude_commands` gets one `.md` file per agent;
  the filename (without `.md`) becomes the command, so `planner.md` is
  invoked as `/planner`.
- **Native subagents** — `paths.claude_agents` gets one `.md` file per agent
  with Claude Code subagent frontmatter (`name` + `description`). The `tools`
  list is deliberately omitted: the wrapper's tool identifiers are VS Code
  names with no clean mapping, so each subagent gets Claude Code's default
  (full) tool set. Claude Code delegates to these automatically based on the
  description, or explicitly when you ask it to use a named subagent.

Instruction files get their `applies_to` scope rewritten to Claude Code's
`paths` field (a list). Subagent seeding runs for `claude-code`, `both`, and
`all`.

## Cursor (`cursor`)

Cursor consumes two surfaces:

- **Rules** — every instruction file is also emitted as
  `.cursor/rules/<name>.mdc` with Cursor frontmatter (`description`, `globs`,
  `alwaysApply`). Unscoped instructions become always-applied rules; scoped
  ones carry their globs. The rules directory is Cursor's own convention and
  is not configurable.
- **Commands** — `paths.cursor_commands` gets one `.md` file per agent
  (verbatim wrapper copies), invocable from Cursor's command palette.

Both run for `cursor` and `all`.

## OpenAI Codex (`codex`)

Codex reads repository context from the `AGENTS.md` convention, so the build
emits a **managed block** into the file named by `paths.codex_agents_md`
(default: the adopter's root `AGENTS.md`). The block contains the agent
roster (name + description, sorted) and pointers to the deployed skills and
instructions directories. Codex has no per-file scoping frontmatter, so no
scope rewrite happens on this target. Emission runs for `codex` and `all` —
this repo dogfoods it on its own `AGENTS.md`.

---

## The Codex managed-block contract

The block is delimited by two HTML-comment markers:

```markdown
<!-- agent-enterprise:begin -->
... generated roster and pointers ...
<!-- agent-enterprise:end -->
```

Merge semantics — content outside the markers is never touched:

- **Both markers present** — only the content between the first begin marker
  and the first end marker is replaced; the marker lines themselves are
  preserved.
- **No markers** — the block is appended to the end of the file, separated by
  a blank line.
- **File missing** — the file is created containing just the block.
- **Malformed markers** (begin without end, end without begin, or end before
  begin) — the build prints a warning and leaves the file untouched. Fix or
  remove the markers and re-run; no data is lost.
- **Duplicate markers** (more than one begin or end marker anywhere in the
  file) — the build prints a warning and leaves the file untouched, same as
  the malformed case.

Marker detection is textual and code fences do not hide markers from it — a
verbatim marker example anywhere in the file counts as a duplicate, so keep
exactly one real marker pair and indent or alter any examples you write.

The block is deterministic (sorted roster, no timestamps), so a second run
with unchanged inputs is byte-identical — safe to run in CI and diff-review.
Because the adopter owns everything around the block, the file is excluded
from the post-deploy token scan.

---

## Config tokens by platform

| Token | Default | Controls |
|:------|:--------|:---------|
| `editor.target` | `"both"` | Which platform artifact sets are emitted |
| `paths.skills_deploy_dir` | `.github/agents/` | Skill bundles + agent wrappers (all targets) |
| `paths.instructions_dir` | `.github/instructions` | Shared instruction files (all targets) |
| `paths.claude_commands` | `.claude/commands` | Claude Code slash commands (any target, when set) |
| `paths.claude_agents` | `.claude/agents` | Claude Code native subagents (`claude-code`, `both`, `all`) |
| `paths.cursor_commands` | `.cursor/commands` | Cursor commands (`cursor`, `all`) |
| `paths.codex_agents_md` | `AGENTS.md` | Codex managed-block target file (`codex`, `all`) |

Every seeded directory is covered by the post-deploy token scan — a deploy
that leaves a real `{{namespace.key}}` token in any platform artifact fails
the build. See [ONBOARDING.md](ONBOARDING.md) for the full setup flow and
[CUSTOMIZATION.md](CUSTOMIZATION.md) for tuning the tokens.
