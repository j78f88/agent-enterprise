<!--
Thanks for contributing! Fill out the checklist below.
Items marked (CI) are also enforced by .github/workflows/release.yml,
but please run them locally first to keep the PR loop tight.
-->

## What this PR does

<!-- One paragraph. Link any related issue. -->

## Why

<!-- The problem this solves. If it's a contract or substrate change,
     link the ADR under command-centre/decisions/. -->

## Definition of Done

- [ ] Tests pass locally: `python -m pytest` (CI)
- [ ] Build is deterministic: `python init.py --config profiles/python-api.config.yml` runs twice, `resolved/` is byte-identical (CI)
- [ ] Frontmatter validates on all modified `*.skill.md` / `*.instructions.md` / `*.body.md` (CI, via the build)
- [ ] Conventional Commits prefix on every commit (CI, via `.githooks/commit-msg`)
- [ ] No new files committed under `resolved/` or `.agent-state/`
- [ ] If the change touches a public contract (schema, callable, registry, mode protocol): an ADR exists under `command-centre/decisions/` and is linked above
- [ ] If the change touches user-facing behaviour: `CHANGELOG.md` updated under the right section

## Risk + rollback

<!-- One sentence each. "Low/medium/high" and "git revert <sha>" is fine
     for most changes. -->

## Verification

<!-- Paste the commands you actually ran and their tail output. -->
