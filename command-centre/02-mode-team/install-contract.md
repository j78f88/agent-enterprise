# Mode 1 — Install contract

> Standalone install. No Mode 2 dispatcher and no Mode 3 coordinator
> are present or assumed.

## Preconditions

- Consumer project repo with version control.
- A coding-agent runtime available (Copilot, Claude Code, Cursor, or
  Codex).
- A substrate decision (reference or custom) and pins recorded:
  `mode-1-contract-vN + protocol-vN`.
- If using the reference substrate: Python 3.12+ for the build tool.

## Steps

For the reference substrate:

1. Vendor or fork agent-homebase into the consumer project (or as a
   sibling repo / submodule).
2. Create a profile at `<consumer>/config/<name>.config.yml` based on
   [`profiles/`](../../profiles/).
3. Run `python init.py --config config/<name>.config.yml`.
4. Commit `resolved/` artifacts (or symlink into the runtime path).
5. Record pins in `<consumer>/.agent-homebase-pins`.

For a custom substrate: the equivalent of the above using the
consumer's own build, producing artifacts in the runtime's shape.

## Postconditions

- Enabled skills are invocable interactively in the runtime.
- Path-scoped instructions surface for matching paths.
- Agents are discoverable.
- Build is reproducible byte-for-byte from a clean clone.
- Pin file records the substrate version and contract tags.

## Upgrade path

Bump `agent-homebase@N.M.P` in the pin file, re-run the build, review
the `resolved/` diff, and commit. If the upgrade crosses a contract-tag
bump, read the release note first.

## Rollback

Revert the pin file and the `resolved/` commit. No external state to
clean up — Mode 1 has no dispatcher process or registry membership.
