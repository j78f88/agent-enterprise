# Personas

The four archetypes agent-enterprise is designed against. Used as the
forcing function for what we build, what we defer, and what we
declare out of scope.

**Format basis.** Nielsen Norman Group ("each piece of information
must drive a design decision; remove if it doesn't") and Christensen,
*Know Your Customers' Jobs to Be Done* ("anchor on the job the user
hires the product to do").

**Evidence status legend.** Gates how much infrastructure we build
for a persona:
- **REAL** — exists today, ship for them.
- **PLAUSIBLE** — positioned for in README, ship for them.
- **ASPIRATIONAL** — design the contract; defer the build until first
  real adopter signal. Cite [Anthropic, *Building Effective Agents*](https://www.anthropic.com/research/building-effective-agents):
  "add complexity only when it demonstrably improves outcomes."
- **DEFERRED** — declared out of scope; revisit only on signal.

---

## P1 — Framework Owner

- **Tag:** Solo author of the substrate.
- **Bio:** Senior engineer maintaining agent-enterprise across several
  of their own codebases.
- **Job to be done:** Encode a pattern once and reuse it next sprint
  without re-deriving it.
- **Behaviours:** Authors skills, agents, ADRs, journal entries.
  Reads `resolved/` to verify build output. Works in CLI + Markdown.
- **Frustrations:** Losing reasoning trail between sessions. Process
  steps with no downstream consumer. Half-finished abstractions.
- **Success signal:** New skill from intent to `resolved/` in under
  30 minutes.
- **Consumes:** All of it — sources, build, ADRs, journal, memory.
- **Ignores:** Conformance tests for runtimes not in use.
- **Evidence status:** REAL. Primary author today.

---

## P2 — Enterprise Platform Engineer

- **Tag:** Platform owner standardising AI-assisted dev across the org.
- **Bio:** DevEx/SRE on a small internal-tools team serving dozens to
  hundreds of developers.
- **Job to be done:** Roll out a vetted catalogue of skills and agents
  that passes security review and produces an audit trail.
- **Behaviours:** Forks upstream catalogues, pins versions, integrates
  with internal CI/SSO/audit. Reviews ADRs before adopting.
- **Frustrations:** Hidden prompt paths. Hard-coded runtimes. No
  deprecation policy. "Optional" steps in a public contract.
- **Success signal:** Substrate upgrade from version N to N+1 ships
  without breaking pinned consumers.
- **Consumes:** Mode 1 contract; protocols layer; security skills;
  honesty contract; hash-chain audit. Later: Mode 3 registry.
- **Ignores:** Lifecycle prompts assuming a single dev; experimental
  skills without a stable version.
- **Evidence status:** ASPIRATIONAL. Mode 3 standalone is designed
  for them by intent; defer schemas, conformance tests, and reference
  impls until first real signal.

---

## P3 — Pro Dev with AI

- **Tag:** Working engineer who uses coding agents as a primary tool.
- **Bio:** Mid-to-senior IC, employed or freelance, shipping
  production code daily across one to five repos.
- **Job to be done:** Make the agent follow this repo's conventions
  every session without re-explaining them.
- **Behaviours:** Uses Copilot or Claude Code in their editor. Runs
  tests before merging. Reads agent output critically.
- **Frustrations:** Confident wrong code with no uncertainty signal.
  Repeating context every session. Skills that assume infrastructure
  they don't have.
- **Success signal:** Onboarding a new project to the substrate takes
  under an hour.
- **Consumes:** QUICKSTART; one matching profile; 3-5 skills (qa,
  review, security); honesty contract; maybe `/plan` and `/review`.
- **Ignores:** Modes 2/3; contract tags; promotion workflow;
  meta-agents.
- **Evidence status:** PLAUSIBLE. Ship for them.

---

## P4 — Outcome-Driven Builder

- **Tag:** Ships ideas; treats the agent as a co-pilot, not a pipeline.
- **Bio:** Founder, designer, PM, or hobbyist building a prototype or
  MVP. May not call themselves a developer.
- **Job to be done:** Get a working app in front of users this week
  without learning a framework first.
- **Behaviours:** Re-prompts until the result works. Deploys to
  Vercel or similar. Skips tests. Often skips Git branches.
- **Frustrations:** Vocabulary they don't know (substrate, callable,
  contract). Multi-step setup before the first useful interaction.
- **Success signal:** App is live and the agent prevented one
  irreversible mistake (leaked key, dropped prod data).
- **Consumes:** At most — a 3-command quickstart, one safety skill.
- **Ignores:** Everything else.
- **Evidence status:** DEFERRED. Declared out of scope in README;
  revisit only on signal.

---

## Persona-to-substrate consumption matrix

| Substrate element | P1 owner | P2 enterprise | P3 pro+AI | P4 builder |
|---|:---:|:---:|:---:|:---:|
| AGENTS.md / CLAUDE.md | authors | reads | reads | skips |
| QUICKSTART.md | maintains | adapts | uses | uses (if exists) |
| Profile (`config/*.yml`) | authors | forks | one fill | n/a |
| Skills (interactive) | authors all | curates subset | uses 3-5 | uses 0-1 |
| Honesty / red-flags | authors | mandates | values | tolerates |
| Mode 1 contract | drafts | conforms | doesn't read | invisible |
| Mode 2 contract + dispatcher | drafts | builds against | doesn't use | invisible |
| Mode 3 contract + registry | drafts | adopts later | doesn't use | invisible |
| Schemas + conformance tests | drafts | demands | doesn't read | invisible |
| Hash-chain audit | drafts | demands | tolerates | invisible |
| Lifecycle prompts (/plan, /review) | uses | curates | uses some | skips |
| Promotion workflow | drafts | adopts later | n/a | n/a |

---

## Why this list is the forcing function

Each persona's evidence status decides what we ship:

- **REAL + PLAUSIBLE (P1, P3)** — ship for them now.
- **ASPIRATIONAL (P2)** — design the contract; defer the build.
- **DEFERRED (P4)** — declare out of scope; one sentence in README.

This list directly resists the failure mode of building for absent
personas. If a proposed change does not move a signal for one of
P1-P3 today, it waits. New personas may be added when first real
signal appears — never speculatively.
