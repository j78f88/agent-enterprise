# Verk Web Audit (Placeholder)

> **Status:** Not yet run. This file will be populated in Phase 4 by `sync harvest verk-web` (or manually if `sync` isn't built yet).

## Purpose

Compare Verk Web's mature 13-agent system + 14 instructions against agent-homebase's substrate. Identify:

1. **Genuine improvements** — patterns in Verk Web that should flow back into homebase substrate
2. **Project-originals** — agents/instructions in Verk Web with no homebase counterpart (candidates for promotion or `delivery-modes/extensions/`)
3. **Drift** — places where Verk Web has diverged from substrate in ways that should reconverge

## Known Differences (initial scan)

Based on initial exploration, the following are likely divergences:

### Agents Verk Web has that homebase doesn't

| Verk Web agent | Likely disposition |
|----------------|-------------------|
| `@delivery-lead` | Promote to substrate (likely generalizable — engagement lifecycle is universal) |
| `@template-auditor` | Keep project-local (Verk-specific to template validation needs) |

### Agents both have

The other 11 agents likely overlap conceptually but Verk Web's versions have 90 sprints of refinement. Deep diff needed.

### Instructions Verk Web likely improved

- `composition-rules.md` (Verk Web has ~14 instruction files; homebase has 24 generic+configurable — overlap probable but unclear which is more refined)
- Sprint composition scoring (Verk Web has lived experience here)
- Release governance

## Audit Procedure (to execute in Phase 4)

1. Run `sync harvest verk-web` (or manually walk `D:\VS\Verk Web\.github\agents\` and `\instructions\`)
2. For each file, classify:
   - Identical to substrate output → ignore
   - Differs only by token substitution → ignore
   - Genuine divergence → record below
   - No substrate counterpart → record below
3. For each genuine divergence, decide: back-port / extension / project-local
4. Update [backport-candidates.md](backport-candidates.md) and [project-local-keep.md](project-local-keep.md)

## Findings

> To be populated.

### Back-port candidates

(Empty — populate in Phase 4)

### Promote-to-extensions candidates

(Empty — populate in Phase 4)

### Keep-project-local

(Empty — populate in Phase 4)
