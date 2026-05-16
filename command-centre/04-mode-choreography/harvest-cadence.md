# Harvest cadence

> **Decision:** [ADR 0005](../decisions/0005-harvest-as-steady-state.md).
>
> Harvest is a steady-state recurring obligation, not a phase. This
> file defines the cadence contract.

## Why steady-state, not a phase

A "phase" implies completion. Once harvest is marked done, the
flywheel — project learnings → substrate improvements → reusable
artifacts — stalls. Substrate stops absorbing what projects discover.

Observed consequences of phase-shaped harvest in v1:
- Substrate becomes inferior to project-local forks within months.
- Forks diverge, and cross-project learning is lost.
- No owner is accountable for keeping substrate current.

Steady-state harvest treats this as continuous operations work, with
an owner, a cadence, and a metric. There is no "done" state.

## Cadence options

A coordinator MUST declare one of:

| Cadence | Suitable for |
| --- | --- |
| `per-sprint` | Programs with formal sprints; harvest runs on sprint close |
| `monthly` | Slower-moving programs; harvest on a fixed day each month |
| `ad-hoc` | Small fleets (≤3 projects) where cadence is event-driven |

Declared in `harvest-cadence.yml`:

```yaml
cadence: monthly
day_of_month: 15
owner: "@platform-lead"
metric:
  name: "candidates_per_cycle"
  floor: 1
```

`ad-hoc` cadence still requires an owner and a metric — it does not
mean "never." It means "triggered by events the owner monitors."

## Owner role

The owner is the single accountable identity for the harvest cycle.
Responsibilities:

- Ensure the cycle runs on cadence.
- Review promotion candidates with the reviewer (may be the same
  person).
- Sign off the audit record.
- Flag skipped cycles.

The owner is a role, not a name — declared in `harvest-cadence.yml`
and updateable.

## Required metric movement per cycle

Every cycle MUST produce a metric value. The metric measures the flow
of learnings from projects into substrate. Suggested options:

| Metric | What it measures |
| --- | --- |
| `candidates_per_cycle` | Number of promotion candidates surfaced |
| `promotions_per_cycle` | Candidates accepted into substrate |
| `drift_items_closed` | Projects upgraded off stale pins |
| `cycle_age_days` | Days since last successful cycle |

A `floor` value is declared. Cycles producing below-floor values are
recorded as flag conditions in the audit record and surface to the
owner.

A cycle producing 0 candidates is a valid cycle outcome — it must
still be recorded with that value.

## Inputs to a harvest cycle

- Registry snapshot.
- Previous cycle's audit record.
- Project repos accessible (per registry).
- Promotion contract ([`05-promotion-contract.md`](../05-promotion-contract.md)).

## Outputs of a harvest cycle

- Audit record at `audit/<cycle-id>.md` with:
  - Cycle date, owner, cadence.
  - Inputs summary.
  - Promotion candidates list (raw).
  - Reviewer decisions per candidate.
  - Metric value with floor reference.
  - Skipped-cycle history (if any).
- Promotion candidates under `harvest/candidates/<cycle-id>/` (one
  file per candidate with evidence).

## Linkage to the promotion contract

Every promotion candidate is evaluated against
[`05-promotion-contract.md`](../05-promotion-contract.md). Candidates
that fail eligibility are rejected with a documented reason in the
audit record. Candidates that pass eligibility but are declined by
the reviewer are `parked` and reconsidered in a future cycle.

## Skipped-cycle policy

A cycle is `skipped` if cadence elapses without the cycle running.

- One skip: audit record next cycle MUST note the skip with reason.
- Two consecutive skips: triggers a coordinator-level review of
  ownership and cadence — either the cadence is wrong, the owner is
  unavailable, or harvest has lost relevance.
- Three consecutive skips: program-of-works coordination is
  effectively offline. The coordinator SHOULD escalate to a named
  decision-maker.
