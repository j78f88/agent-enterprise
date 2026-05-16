# ADR 0007 — Personas, scope, and deferral discipline

> **Status:** Accepted.

## Context

After ADRs 0001–0006 the architecture was settled but the *audience*
was not. Three questions kept resurfacing in review:

1. **Who is this for?** Hyperbolic persona drafts ("the AI-native
   platform team of the future") collapsed under scrutiny.
2. **Is Mode 3 additive on top of Modes 1+2, or standalone?** The
   text could be read either way.
3. **What ships first?** Contracts, reference implementations,
   conformance suites, and JSON schemas were all on the table for the
   initial cut. None could ship to quality simultaneously.

External evidence consulted:

- **Anthropic, *Building Effective Agents*** — "add complexity only
  when it demonstrably improves outcomes." Argues for the smallest
  contract that does the job.
- **OpenAI Symphony** — published as a "low-key engineering
  preview," not a finished product. Precedent for shipping the
  architecture before the implementation.
- **agents.md** — "Are there required fields? No." Precedent for
  contract-first, schema-later.
- **addyosmani/agent-skills** (42.2k★) — 23 skills, 3 personas,
  zero conformance tooling. Persona-led adoption works at scale.
- **NN/g persona guidance** — "each piece must drive a decision;
  avoid witty taglines." Drove the Tag/Bio/JTBD/Behaviours/
  Frustrations/Success-signal/Consumes/Ignores/Evidence-status format
  in [`docs/PERSONAS.md`](../../docs/PERSONAS.md).
- **Christensen, *Jobs to Be Done*** — frame each persona around the
  job they hire the substrate to do, not their title or stack.

## Decision

### 1. Four personas, evidence-tagged

[`docs/PERSONAS.md`](../../docs/PERSONAS.md) defines:

| # | Persona | Evidence status |
| --- | --- | --- |
| P1 | Framework Owner (the author) | REAL |
| P2 | Enterprise Platform Engineer | ASPIRATIONAL |
| P3 | Pro Dev with AI | PLAUSIBLE |
| P4 | Outcome-Driven Builder | DEFERRED |

Every doc, skill, and ADR is written to a named persona. Anything
that cannot point at one is a candidate for deletion. The persona
file is the onboarding standard; the README links it; QUICKSTART is
written for P3.

### 2. Mode 3 is standalone

A consumer adopting Mode 3 (choreography across multiple projects)
is not required to also adopt Mode 1 (team scaffolding) or Mode 2
(orchestration contract). Modes are composable but independent:

- A program may run Mode 3 over projects that use entirely different
  internal team setups.
- A solo developer may use Mode 1 only and never touch the registry.
- Mode 2's contract is consumed by orchestrators that may or may not
  be part of any Mode 3 program.

Each mode's contract is self-contained. Cross-mode coupling lives in
the shared protocols at the root (per ADR 0002), not in mode-to-mode
imports.

### 3. Ship contracts; defer everything else

The first cut ships:

- The four mode contracts (overview, team, orchestration,
  choreography).
- The shared protocols at the root.
- The seven ADRs.
- The personas and quickstart.

The first cut explicitly **defers**:

- Reference implementations of any mode.
- Conformance test suites.
- JSON schemas for the registry, promotion contract, or subagent
  returns *beyond* what [`schemas/`](../../schemas/) already contains
  for the v1 substrate.
- Any CLI beyond the harvest script (per ADR 0006).
- Editor-specific glue beyond what [`init.py`](../../init.py)
  already emits.

Deferral is not abandonment. Each deferred item gets a section in a
future ADR when a real adopter creates pull on it.

## Consequences

**Positive**
- The substrate has a named audience. Persona-less content has
  nowhere to hide.
- Mode 3 can be adopted by programs whose individual projects use
  none of the other modes — meeting them where they are.
- The initial release ships to quality on a narrow surface instead
  of shipping four things half-built.

**Negative**
- "Contracts only, no reference impl" is a real friction for an
  adopter who wants a runnable example today. They get the persona
  guidance, the quickstart, and the v1 substrate (Modes 1+2 are
  fully implemented and tested); Mode 3's CLI-less design (ADR
  0006) is the closest thing to a reference.
- Personas tagged ASPIRATIONAL/PLAUSIBLE/DEFERRED are honest but
  may read as weakness to a casual reader. The evidence-status
  field is the antidote; it is non-negotiable.

## Alternatives considered

- **Skip personas; let docs speak for themselves.** Rejected —
  every prior round of doc rewrites collapsed back into hyperbole
  without persona anchors.
- **Mode 3 as additive on Modes 1+2.** Rejected — couples three
  contracts that have no technical reason to be coupled, and
  excludes programs that span heterogeneous teams.
- **Ship reference impls in the first cut.** Rejected — would
  delay the contracts behind implementation polish for personas
  (P2, P4) who have not yet demonstrated pull.
