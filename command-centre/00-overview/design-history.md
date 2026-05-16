# Design history — Command Centre

> The reasoning trail from initial intent to v2 architecture. Captures
> external research consulted, design errors found, alternatives eliminated,
> and influences that shaped each decision. Read this before
> [three-modes.md](three-modes.md), [architecture.md](architecture.md), or
> any contract document — those files assume the conclusions reached here.

---

## 1. Origin — three stated outcomes

The intent that anchored this entire design effort:

> 1. agent-homebase singularly deployable as an effective project team
> 2. agent-homebase singularly deployable as an orchestration layer
> 3. agent-homebase multi-deployable as a choreography layer across multiple
>    projects in a program-of-works approach — a combination of 1 and 2

These three statements named what later became Mode 1 (team), Mode 2
(orchestration), and Mode 3 (choreography). They were stated as
*deployability modes of agent-homebase*. That framing turned out to need
correction, but the underlying capabilities did not.

Two additional anchoring constraints:

- **agent-homebase must remain 100% generic** — zero references to
  personal projects, zero project-specific files, no examples that name a
  real codebase the author is working on.
- **The three modes must be consumable in any combination, including
  individually** — a consumer can take Mode 2 alone and run it against
  their own callables, never touching the rest of the framework.

The second constraint was added after v1 had already been built. It is
what forced v1 to be redesigned.

---

## 2. The v1 design (committed as `f17eeeb`)

The first response to the three outcomes was to build a workbench called
`command centre/` inside agent-homebase. 28 files across these folders:

```
command centre/
  00-overview/    three-modes, architecture, glossary
  01-mode-team/   spec, install-contract
  02-mode-orchestration/   spec, install-contract, absorption-checklist
  03-mode-choreography/    spec, sync-cli-spec, registry-schema, meta-agents,
                           workspace-template
  04-harvest/     verk-web-audit, backport-candidates, project-local-keep
  05-onboarding/  verk-web, diy-project-helper, verk-v2
  06-migration/   absorption-runbook, graduation-runbook, rollback
  decisions/      0001-0004 ADRs
```

Key v1 design decisions:

- **Containerize the work inside agent-homebase.** The reasoning was that
  a separate command-centre repo would create sprawl; better to keep all
  thinking co-located, then graduate generic parts into
  `delivery-modes/choreography/` at Phase 6.
- **Absorb the existing `agent-orchestration` repo wholesale into Mode 2.**
  Hatice runtime + linear adapter + dispatcher/verifier agents would all
  move into `delivery-modes/orchestration/` as the canonical Mode 2 impl.
- **Build a sync CLI for Mode 3** with six commands —
  `register / deploy / diff / status / harvest / unregister` — to manage
  the program-of-works registry and propagation.
- **Treat harvest as a phase** (Phase 4) — a one-shot audit of Verk Web's
  mature patterns, with the results back-ported to substrate.

v1 was committed and pushed. The author then asked for external validation
of four open recommendations before locking in the ADRs.

---

## 3. The validation request that surfaced the errors

The author explicitly asked for the design to be tested against external
research, with the framing:

> the suggestions make sense, but i want them validated further and with
> external research if possible against design decisions behind [these
> sources] … to be clear i am happy to build the best system, not have an
> echo-chamber of positive reinforcement of prior designs

Three external sources were specified for consultation. A fourth (Anthropic
Enterprise PDF) was shared by the author later when initial fetch failed.

---

## 4. External research consulted

### Symphony (github.com/openai/symphony)

OpenAI's open-source "implementation runs" framework. Key signals:

- **Spec-driven distribution model.** Symphony ships a `SPEC.md` (the
  contract) plus an Elixir reference implementation. Consumers can build
  their own runtime against the spec or use the reference. This decouples
  the contract from any single runtime.
- **Layered on harness engineering.** Symphony positions itself as
  *"the next step after harness engineering"* — additive rather than
  replacement. A consumer keeps their existing setup and adds the
  orchestration layer on top.
- **Proof-of-work artifacts.** Symphony produces CI status, PR reviews,
  complexity analysis, and walkthrough videos as evidence that work
  occurred. Verification is rich, not just "session ended."
- **Informal lifecycle.** No formal releases; the spec is the stable
  artifact. Implementations can evolve at their own pace.

### Harness Engineering, OpenAI (Feb 2026)

Engineering blog post on how OpenAI Codex agents work inside their own
codebase. Key signals adopted into v2:

- **"Give Codex a map, not a 1,000-page instruction manual."** An ~100-line
  AGENTS.md serves as a table of contents; the structured docs/ folder is
  the system of record. v2 README and overview files follow this pattern.
- **Plans are first-class artifacts.** Active plans, completed plans, and
  known technical debt are all versioned and co-located. Validates
  treating ADRs, contracts, and runbooks as repo-resident artifacts.
- **Agent legibility is the goal.** Anything not in the repo doesn't
  exist. Validates the bias toward file-based state over service-based
  state.
- **Enforce boundaries centrally, allow autonomy locally.** Substrate
  defines invariants; per-project configuration handles specifics. This
  shaped the Mode 1 contract vs. consumer-defined callable distinction.
- **Garbage collection.** Recurring "doc-gardening" agents scan for stale
  or obsolete content. Validates the steady-state harvest cadence.
- **Throughput changes the merge philosophy.** Minimal blocking gates,
  short-lived PRs, "corrections are cheap, waiting is expensive."
  Influenced the bias against over-policing substrate composition rules.

### Anthropic — Building AI Agents for the Enterprise (April 2026)

Practitioner guide. Three pillars (upskill employees / accelerate
processes / transform products) and a four-principle deployment framework.
Key signals adopted:

- **Three pillars map onto three modes.** Upskill employees → Mode 1
  team. Accelerate processes → Mode 2 orchestration. Transform products →
  Mode 3 choreography across a program. External validation that the
  trichotomy is not arbitrary.
- **Plugins as the unit of distribution.** Anthropic's "plugins"
  (packages of skills, context, connectors) are functionally identical to
  agent-homebase's existing skills + instructions + profiles structure.
  Confirms the substrate concept predates the term.
- **"Compounding returns assume sustained expert feedback investment.
  Organisations that encode knowledge once and do not maintain it will
  see the flywheel stall."** Direct trigger for anti-fragility Pattern 5.
- **Four deployment principles:** start with specificity not scale; pilots
  with measurable finish lines; build plugins for reuse from the
  beginning; governance is a prerequisite not an afterthought.
- **L'Oreal case study** (90% → 99.9% accuracy via continuous feedback)
  reinforces the harvest cadence requirement.
- **Rakuten case study** ("offload the execution layer") reinforces
  Pattern 6 — don't own infrastructure you don't need to.

### Anthropic — Building Effective Agents (Dec 2024)

Engineering essay on agent patterns. Key signals adopted:

- **"Maintain simplicity in your agent's design."** Caution against
  over-engineering Mode 3. Drove the elimination of the sync CLI.
- **"Frameworks add extra layers of abstraction that obscure underlying
  prompts and responses."** Validates contract+impl separation:
  the framework provides the contract, not the obscuring layer.
- **Workflow vs. agent distinction.** Mode 1 (substrate) is a workflow
  library. Mode 2 (orchestration) is an orchestrator-workers agent.
  Mode 3 (choreography) is orchestrator-workers across repos.
- **"Carefully craft your agent-computer interface (ACI) through thorough
  tool documentation and testing."** Applies to every contract document
  in v2 — they are the ACI for adopters.

### Anthropic — How we built our multi-agent research system (Jun 2025)

Engineering essay on production multi-agent system. Key signals adopted:

- **Rainbow deployments.** "We can't update every agent to the new
  version at the same time; we use rainbow deployments to avoid
  disrupting running agents." This is the strongest single signal in v2's
  versioning strategy — substrate must support N-1 coexistence.
- **End-state evaluation, not turn-by-turn.** Verifier philosophy:
  judge the artifact, not the process. Shapes the Mode 2 verifier
  contract.
- **Subagent output to filesystem.** Subagents write artifacts to disk
  and pass *references* to the lead agent, avoiding "game of telephone."
  Validates tier 1/2/3 return schemas being thin manifests pointing at
  files.
- **Token usage ~15× chat for multi-agent.** Cost discipline for Mode 3.
  Don't add coordination overhead unless it earns its keep.
- **Stateful agents, compounding errors, durable execution with
  checkpoints.** Influenced the promotion contract and harvest workflow
  — every cycle produces durable, inspectable artifacts.

---

## 5. Anti-fragility patterns derived

The existing `ANTI_FRAGILITY.md` documented four patterns from a prior
failure (Ghost-Done, Split-state, Governance-before-proven-loop, Repo
pollution). The new research added three more patterns plus a refinement.

### Pattern 5 — Flywheel stall (new)
Project absorbs substrate, customises, ships value, never feeds learnings
back. Substrate drifts from reality. Next project inherits stale
assumptions. Within 2-3 projects the framework stops matching how real
work gets done.

**Source:** Anthropic Enterprise — *"Organisations that encode knowledge
once will see the flywheel stall."*

**v2 response:** Harvest is a steady-state recurring obligation, not a
phase. Cadence, owner, and at least one measurable substrate metric per
cycle required.

### Pattern 6 — Execution-layer ownership (new)
Framework wraps things it doesn't need to own — git, a registry service,
a job queue. Each owned component becomes a fragility point: it breaks,
ages, locks the framework to a specific runtime.

**Source:** Building Effective Agents — *"frameworks create extra layers
of abstraction that obscure underlying prompts."* Rakuten case study —
*"offloaded the execution layer."*

**v2 response:** Mode 3 sync CLI eliminated. Registry is a file. Harvest
is a script. Git operations stay native.

### Pattern 7 — Vendor coupling drift (new)
A skill or instruction is authored against a specific runtime's
behaviour. Substrate appears to work but only on one platform. Dual-
platform parity erodes silently.

**Source:** Anthropic Enterprise conflates Claude Cowork (product) with
general agentic principles — easy to do the same in your own framework.

**v2 response:** Every mode contract is runtime-agnostic. Reference
implementations live in `reference-impl/` subfolders; the contract above
them is portable.

### Refinement to Pattern 3 — Governance design vs enforcement
Pattern 3 (Governance-before-proven-loop) could be misread as "skip
governance." Refinement: governance **design** belongs up front (schemas,
RBAC shape, audit trail format). Governance **enforcement** waits until
the loop is proven.

**Source:** Anthropic Enterprise — *"Governance is a prerequisite, not an
afterthought"* (when read alongside their three-phase rollout where
enforcement deploys in Phase 3, but design starts in Phase 1).

---

## 6. v1 design errors found

Once the patterns were applied honestly against v1, four design errors
surfaced:

### Error A — Repo pollution (Pattern 4 violation)
v1 put both (a) generic choreography templates and (b) the author's
specific program-of-works state (project list, registry, harvest log,
playbooks for three named projects) into agent-homebase. ADR 0001
("containerize in homebase") conflated these two distinct concerns. The
graduation in Phase 6 only addressed (a). It left (b) inside the
framework forever — the exact failure mode `ANTI_FRAGILITY.md` Pattern 4
warns against.

### Error B — Sync CLI over-build (Pattern 6 violation)
Of the six proposed sync CLI commands (`register / deploy / diff /
status / harvest / unregister`), five were thin git wrappers. Only
`harvest` did irreducible work — and even that needed a schema, not a
CLI.

### Error C — Mode 2 vendor coupling (Pattern 7 violation)
v1 planned to absorb `agent-orchestration`'s hatice runtime as Mode 2
itself. This coupled Mode 2 to one specific dispatcher. If hatice went
stale, Mode 2 would go stale. If a consumer wanted Mode 2 on Symphony or
their own dispatcher, the framework couldn't help.

### Error D — Harvest as a phase (Pattern 5 violation)
v1 PLAN.md had Phase 4 = harvest, then Phases 5 and 6 moved past it.
After Phase 6 graduation, harvest had no home. The plan literally baked
in flywheel stall.

---

## 7. The two clarifications that locked v2's shape

After errors were surfaced, the author added two clarifications that
forced the architecture into its final form:

### Clarification 1 — Total genericity
*"agent-homebase is totally generic and has no information around any of
my personal projects."*

This eliminated the option of a sister command-centre repo I would
scaffold. User-specific work simply leaves the framework entirely and
lives in the author's own private space — not the framework's concern.

### Clarification 2 — Standalone consumability in any combination
*"someone could consume mode 2 for example and then have their own in-
project agents and skills alongside it, adjusting as needed based on
their requirements."*

This forced **Reading B** (modes as standalone products) over **Reading
A** (modes as additive layers on Mode 1). Reading B is more demanding —
each mode must publish a contract in the abstract, not as a tight
coupling to homebase substrate — but it delivers genuine independence.

---

## 8. Reading A vs Reading B — the architectural fork

After the second clarification, two coherent designs were on the table.

| | **Reading A** | **Reading B** (chosen) |
| --- | --- | --- |
| Mode independence | Mode 2 and Mode 3 require Mode 1 substrate | Each mode publishes a contract; substrate is one reference provider |
| Valid combinations | {1}, {1,2}, {1,3}, {1,2,3} — 4 | All 7 non-empty subsets |
| Effort | ~half day | ~1.5 days |
| Contract discipline | Implicit | Explicit per mode |
| Reference impls | Optional | Required (proves portability against non-homebase users) |
| Future-proofing | Locks substrate to specific shape | Substrate can evolve independently within contract |

**Why Reading B was chosen:** the author's stated outcome #3 was
*"someone could consume mode 2 with their own in-project agents and
skills."* Reading A makes that aspirational. Reading B makes it true.
The 1-day delta is the cost of contract extraction and one non-homebase
worked example per mode.

---

## 9. Alternatives considered and eliminated

| Option | Rejected because | Replaced by |
| --- | --- | --- |
| Separate `agent-command-centre` repo | Conflicts with "totally generic" — even an empty sister repo presumes the author's program-of-works belongs in the framework's orbit | User's program-of-works lives in private space, no framework artifact |
| `command centre/` folder graduating to `delivery-modes/` at Phase 6 | Graduation only fixes the generic half; user-specific half stays forever (Error A) | v2 starts in the right shape — `delivery-modes/` directly, with user content excluded by construction |
| Sync CLI for Mode 3 | 5 of 6 commands are git wrappers (Error B / Pattern 6) | `registry.yml` file + single `harvest` script + the project contract |
| Absorb `agent-orchestration` repo wholesale into Mode 2 | Couples Mode 2 to hatice (Error C / Pattern 7) | Mode 2 contract is the artifact; hatice goes into `reference-impl/` as one of N possible impls |
| Harvest as Phase 4 milestone | Bakes in flywheel stall (Error D / Pattern 5) | Steady-state cadence defined in Mode 3 contract; no phase boundary |
| Per-mode independent semver | Maximum coordination overhead for consumers tracking compatibility across three version streams | Unified repo semver + per-mode contract tags (only bump when the contract itself breaks) |
| Skip the protocols layer; let each mode redefine return schemas | Three modes redefining the same protocol → drift → coordination tax | Tiny shared `01-protocols/` folder; modes depend only on it, never on each other |
| Treat substrate (`skills/`, `instructions/`, `agents/`) as Mode 1's implementation | Bundling implementation with contract obscures what Mode 1 actually promises | Substrate is the **reference provider** of Mode 1's callable contract; consumers can swap |
| Single big-bang v1 → v2 rewrite in place | Loses the v1 reasoning trail; if v2 reaches a dead end, recovery is hard | v2 is a parallel folder; v1 stays as historical reference until v2 is reviewed |

---

## 10. Final v2 design choices

### A. `01-protocols/` layer at the top of every dependency arrow
Five tiny artifacts: callable-contract, project-contract, return-
schemas, frontmatter-spec, versioning-and-tags. Stable, slow-changing.
Modes depend only on this; nothing else. This is the layer that makes
standalone consumption work — pull `01-protocols/` plus the mode you
want, and you have a coherent product.

### B. Per-mode `contract.md` + `reference-impl/` separation
Each mode folder is two artifacts:
- The contract — what it means to satisfy this mode.
- One or more reference implementations.

Hatice becomes `03-mode-orchestration/reference-impl/hatice/`, not Mode
2 itself. Symphony, custom dispatchers, or future runtimes drop in as
siblings.

### C. Three versioning streams
- Repo semver (`agent-homebase@2.3.0`) — bumps on any change.
- Protocol version (`protocol-v1`) — bumps very rarely.
- Per-mode contract tags (`mode-2-contract-v1` etc.) — bump only on
  breaking contract changes.

A Mode-2-only consumer pins `protocol-v1 + mode-2-contract-v1` and
tracks `agent-homebase@2.*.*`. They get fixes without tracking other
modes. Supports the rainbow-deployment requirement from Anthropic's
multi-agent research post.

### D. Harvest as steady-state cadence
Mode 3 contract defines: a cadence (per-sprint, monthly, or ad hoc), an
owner role, and an obligation to move at least one substrate metric per
cycle. No "Phase 4." No completion state.

### E. Promotion contract as first-class artifact
`05-promotion-contract.md` defines when a project-local artifact
becomes eligible for substrate. Eligibility criteria, evidence required,
reviewer role, outcome states. Without this, harvest is hand-wavy and
inconsistent.

### F. Mixed-fleet support in Mode 3
Registry schema includes `mode_level` per project. Meta-agents adapt
behaviour: a program-of-works can mix Mode-1-only projects with Mode-2
projects with no special handling.

### G. No `02-mode-orchestration` → `03-mode-choreography` cross-deps
Mode 3 does not require Mode 2 to exist. A program of works can
coordinate plain Mode 1 projects. Mode 2's presence in any project is
purely a `mode_level` enum value in that project's registry entry.

---

## 11. Influences attribution

| Decision | Primary external influence |
| --- | --- |
| Three-mode framing | Anthropic Enterprise three-pillar structure (independent confirmation, not source) |
| Modes as standalone products | User's clarification #2 + Symphony's spec+impl pattern |
| Contract / reference-impl separation | Symphony (SPEC.md + Elixir reference) |
| `01-protocols/` shared layer | Anthropic Multi-Agent — subagent-to-filesystem pattern, shared output protocol |
| Per-mode contract tags + N-1 coexistence | Anthropic Multi-Agent — rainbow deployments |
| Harvest as steady-state cadence | Anthropic Enterprise — flywheel-stall warning + Harness Engineering garbage-collection principle |
| Promotion contract | Harness Engineering — *"when documentation falls short, we promote the rule into code"* |
| No sync CLI | Building Effective Agents — *"reduce abstraction layers"* + Rakuten case (offload execution) |
| File-based registry over service | Harness Engineering — *"anything not in the repo doesn't exist"* |
| Mixed-fleet support in Mode 3 | Anthropic Multi-Agent — lead agent coordinating heterogeneous subagents |
| Promotion / harvest discipline | Anthropic Multi-Agent — durable artifacts with checkpoints |
| Refusal to absorb agent-orchestration wholesale | Pattern 7 (vendor coupling) derived from Anthropic Enterprise's own conflation warning |
| Parallel v2 folder instead of rewrite in place | User direction — preserve v1 reasoning |

See also: [docs/BEST_PRACTICE_ALIGNMENT_JOURNAL.md](../../docs/BEST_PRACTICE_ALIGNMENT_JOURNAL.md)
— the companion record of substrate-level hygiene work (honesty
contract, hash-chain audit, OPA removal, `references/` checklists)
that sits *inside* the shape this history settles on. The journal
patches the substrate; this history explains why the substrate has
the shape it does.

---

## 12. Open questions remaining (for future work)

These were surfaced during v2 design but deliberately deferred until v2
content is filled in:

- **Q1 — Folder name `delivery-modes/`.** Once v2 graduates into the
  repo, is `delivery-modes/` the right name, or just `modes/`? Defer
  until first non-author consumer feedback.
- **Q2 — Conformance test format.** Each contract needs a way for a
  reference impl (or consumer impl) to prove conformance. Test in
  Python? Markdown checklist? JSON schema validation? Defer until the
  first contract is filled in.
- **Q3 — Promotion contract reviewer role.** Should promotion reviews
  require a human, or can a meta-agent (e.g., `@audit`) sign off
  autonomously under certain conditions? Defer until first harvest
  cycle.
- **Q4 — v1 retirement timing.** Keep v1 until v2 is committed and
  reviewed, then delete in a separate commit so history is clean.
  Decision deferred to author after v2 content is populated.
