# Mode 1 — Install contract

> Standalone install. No Mode 2 dispatcher and no Mode 3 coordinator
> are present or assumed.

## Preconditions

- Consumer project repo exists with version control.
- A coding-agent runtime available (Copilot, Claude Code, Cursor, or
  Codex).
- Python 3.12+ on the operator's machine (only if using the
  reference substrate's build tool).
- Decision recorded: which substrate (reference or custom) and which
  contract pins (`mode-1-contract-vN + protocol-vN`).

## Steps

For the reference substrate:

1. Vendor or fork agent-homebase into the consumer project (or as a
   sibling repo referenced by submodule).
2. Create a profile at `<consumer>/config/<name>.config.yml` based on
   [`profiles/`](../../profiles/).
3. Run `python init.py --config config/<name>.config.yml`.
4. Commit `resolved/` artifacts (or symlink into the runtime's expected
   location).
5. Record pins in `<consumer>/.agent-homebase-pins` (or equivalent).

For a custom substrate: the equivalent of the above using the
consumer's own build, producing artifacts in the shape the chosen
runtime expects.

## Postconditions

- Enabled skills are invocable interactively in the runtime.
- Path-scoped instructions surface for matching paths.
- Agents are discoverable.
- Build is reproducible byte-for-byte from a clean clone.
- Pin file records the substrate version and contract tags in use.

## Exit codes (build tool)

For the reference `init.py`:

| Code | Meaning |
| --- | --- |
| 0 | Build succeeded |
| 1 | Profile validation failed |
| 2 | Frontmatter validation failed |
| 3 | Security validation failed |
| 4 | Resolution failed (missing token, broken reference) |
| 5 | Output write failed |

Custom build tools should expose an equivalent vocabulary.

## Test plan

1. Run build twice from a clean clone; diff `resolved/` → must be
   empty (determinism).
2. Load built artifacts in primary runtime; invoke one skill
   interactively; verify expected output.
3. Load built artifacts in a second runtime; verify same skill
   resolves and runs.
4. Modify profile (e.g., disable one skill); rebuild; verify the
   removed skill is absent from artifacts.

## Rollback

Revert the pin file and the `resolved/` commit. No external state to
clean up — Mode 1 has no dispatcher process or registry membership.

## Upgrade path

1. Bump `agent-homebase@N.M.P` in the pin file.
2. Re-run the build.
3. Review the `resolved/` diff.
4. If the upgrade crosses a contract-tag bump, read the release note
   for migration steps before committing.
5. Commit.
