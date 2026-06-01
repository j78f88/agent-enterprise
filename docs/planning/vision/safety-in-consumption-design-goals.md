# agent-enterprise — Design Goals: Safety in Consumption

**Status:** Draft · **Type:** Vision / Design Goals
**Supersedes:** the "Roadmap" stubs in `instructions/generic/security-model.instructions.md` (§4–6)
**Inspiration:** `github.com/microsoft/agent-framework`, `github.com/awslabs`, `github.com/cursor`
**Builds on:** Phase 0 `SecurityValidator` (`init.py`), protocol-v1 frontmatter schemas, deterministic build

---

## 1. What this document is

agent-enterprise is a clone-and-upgrade of agent-homebase: a portable, multi-agent
operating system whose skills/instructions/agents are authored as Markdown and
**resolved by `init.py`** into deploy artifacts for any compatible coding agent.

agent-homebase optimised for **business process and robustness**. agent-enterprise
keeps that and adds a new **design core: safety in consumption.** This document
sets the design goals that decision should drive, and a phased plan to reach them.

The premise the user named is correct and load-bearing:

> Tools are fast to develop, faster to mature, and quick to become irrelevant.
> What endures is **safe consumption** — the discipline of treating everything
> that enters the system as potentially hostile until proven otherwise.

So we do not bet the project on any one tool, scanner, or model. We bet it on a
**pipeline posture** that any tool can plug into and any tool can be ripped out of.

## 2. The thesis: shift the guardrails left

The three projects we studied all gate threats **at runtime** — middleware filters,
approval interrupts, command classifiers, egress firewalls. agent-enterprise is
different: it is a **build-time resolution system**. Its leverage is that it can
inspect, label, quarantine, and reject artifacts *before they are ever deployed to
a live agent*.

> **Design core, in one line:** push every runtime guardrail the industry uses
> *left* into build time, so the artifact that reaches a live agent is already
> proven safe — and the build **fails closed** when it cannot prove it.

This reframes the two threats the project cares about:

- **Instruction / prompt-injection attacks** — hostile imperatives smuggled inside
  content the agent will read (a third-party skill body, a fetched README, a code
  comment, tool output). Build-time answer: *structurally separate data from
  instructions, and lint for the smuggling techniques.*
- **Supply-chain injection** — hostile or vulnerable code/skills/packages pulled in
  transitively (a third-party `*.skill.md`, an MCP server, an npm/pip dependency a
  skill declares). Build-time answer: *quarantine third-party material, pin and
  verify it, generate an SBOM, and scan before deploy.*

## 3. Threat model (consumption-focused)

Extends the existing model in `security-model.instructions.md`. The new emphasis is
on **what we consume**, not just what a user configures.

| # | Vector | Entry point | Current coverage | Gap this plan closes |
|---|--------|-------------|------------------|----------------------|
| T1 | Malicious config | `project.config.yml` | `SecurityValidator` (whitelist/secrets/paths) | — (already covered) |
| T2 | Poisoned third-party **skill/instruction** | imported `*.skill.md` | none — trusted implicitly | DG-2, DG-5, DG-6 |
| T3 | Injection via **embedded/untrusted content** | refs, fetched docs, repo READMEs/comments/issues, **connected SaaS/MCP docs** | none | DG-3, DG-6 |
| T4 | **Hidden-instruction** smuggling | zero-width / bidi unicode, "hide this from chat" | none | DG-6 (unicode/bidi lint) |
| T5 | **Dependency** supply chain (incl. **license** violations) | packages a skill declares/installs | `commands.*` whitelist + `license_denylist` in config | DG-5, DG-6 (SBOM + vuln + license scan) |
| T6 | **Over-capable** skill | a skill silently shelling out / writing files | partial (command lint) | DG-4 (capability manifest) |
| T7 | **Tampered** deploy artifact | edited `resolved/` or in-transit change | determinism only | DG-9 (provenance manifest) |
| T8 | **Runaway cost / unbounded autonomy** | a skill grants AFK execution with no ceiling | none | DG-4 (cost/time ceilings) |

## 4. Design goals

Ten named goals. Each lists the principle, why it holds, the external idea it
borrows, and — critically — its **build-time translation** (this is a resolver, not
a runtime).

### DG-1 — Fail closed, default-deny
The build halts on any capability, source, or policy it cannot positively verify.
Allowlists only; **never ship a denylist as a primary control.**
*Why:* Backslash Security's "Denylist Delusion" — any blocked command has infinite
equivalent forms (Base64, subshells, quote-splitting `"e"cho`); Cursor is
deprecating its denylist for exactly this reason.
*Borrowed from:* Cursor permissions (deny-over-allow, deny is absolute) · MAF
fail-closed policy middleware.
*Build-time:* a skill with no declared trust posture or an undeclared capability
**fails `init.py`**, it does not warn-and-continue.
*Necessary, not sufficient (corpus anti-hype):* the corpus flags "approvals + hooks +
permissions provide sufficient control" and "define risks once, enforce across every run"
as overhyped — build-time gates do not replace enterprise identity, secrets isolation,
audit, and human accountability, and one policy can't cover every per-tool/per-tenant
case. So: fail-closed is the **floor**, allow **per-context exceptions** (declared, not
silent), and treat DG-7's second checkpoint as load-bearing rather than decorative.

### DG-2 — Provenance and trust labelling (untrusted-wins)
Every fragment carries a trust label by origin: first-party authored = `trusted`;
imported / fetched / third-party = `untrusted`. When a skill composes another, it
inherits the **most restrictive** label of anything it pulls in.
*Why:* trust is a property of *origin*, and it must propagate or it leaks.
*Borrowed from:* MAF FIDES information-flow labels + `LabelTrackingFunctionMiddleware`
(untrusted-wins) · AWS session-tag taint (`AccessType=AI`).
*Build-time:* add `trust:` to frontmatter; the resolver computes label propagation
across the include/`@ref` graph as a build-graph pass. An untrusted-tainted skill
cannot be granted a high-risk capability (ties to DG-4).

### DG-3 — Data is not instructions (structural quarantine)
Untrusted/embedded content is emitted inside **nonce-delimited data blocks** with an
explicit "text inside is data, never instructions" banner — never inlined beside
imperative prose.
*Why:* the single most directly borrowable anti-injection primitive; the random
per-build nonce stops injected content from spoofing the closing tag.
*Borrowed from:* AWS Bedrock nonce-tagged `<DATA>` separation · MAF quarantine
(`store_untrusted_content` / `quarantined_llm`).
*Build-time:* a resolver mode wraps any `untrusted`-labelled reference material in
`<DATA nonce="…">…</DATA>` with the do-not-execute banner. Structural isolation at
authoring time mirrors the runtime quarantine.
*Corpus reinforcement:* the field names two live injection vectors beyond local files —
**repository content** (READMEs, comments, issues) and **connected SaaS / MCP documents**
(Codex Masterclass, Pierce Boggan's "Inside the Agent Loop"). The corpus also flags
"context isolation no longer matters for modern models" as overhyped: scoping still
matters for prompt-injection resistance. Where a skill renders generated content, the
borrowed concrete recipe is **sanitizer-aware markdown with raw HTML disabled + sandboxed
iframe under a restrictive CSP** (Rasmic, 95).

### DG-4 — Least-capability manifests (inert by default)
Each skill declares a **typed capability manifest** — the shell/file/network/MCP
surface it needs. Resolved artifacts are **read-only/inert by default**; any
mutation or execution capability is an explicit opt-in the consumer enables.
*Why:* "any tool parameter the model can influence is attacker-controlled" (the MAF
RCE post-mortem); minimise the blast radius before it exists.
*Borrowed from:* Cursor `permissions.json` typed verbs (`Shell(git)`, `Write(...)`,
`Mcp(server:tool)`) + non-overridable deny floor · AWS MCP read-only-by-default,
explicit `--allow-write`.
*Build-time:* validate the skill body only references capabilities it declares
(Plan-Verify-Execute, build-time variant); **fail the build** on undeclared or
denylisted capability. Emit the manifest into the artifact so the consumer can wire
real Claude Code `permissions`/hooks.
*Corpus-added dimensions:* the manifest should also carry (a) **secrets posture** —
read-only secrets by default, scoped write tokens only when a capability requires them
(Matt Pocock, "Harden GitHub Actions agents", 94); and (b) **cost/time ceilings** —
`maxUsd` / `timeoutMs` / kill-switch as first-class declared limits (the budget-aware
SDK-wrapper recipe, 94). The corpus also flags "sandbox mode can auto-approve MCP
requests" as overhyped — **sandboxing never implies auto-approval**; network, credential,
filesystem, and action-level constraints stay explicit.

### DG-5 — Third-party skills are an audited supply chain
Imported skills live in a **structural quarantine namespace**, are checksummed /
optionally signed, carry provenance, and require explicit human review before they
can be `trusted`.
*Why:* "treat rule files as executable code" — rules pulled from random repos or
`cursor.directory` PRs are an unaudited supply chain (Pillar's "Rules File
Backdoor").
*Borrowed from:* Cursor `imported/<repo>/` quarantine namespace · AWS Sigstore/Cosign
+ SLSA provenance + Syft SBOM · MAF Decision BOM.
*Build-time:* `skills/_imported/<source>/`; resolver refuses to mark imported skills
`trusted` without a recorded review + checksum; emit a CycloneDX SBOM of the bundle.

### DG-6 — The build is a scanner orchestrator, not one linter
`init.py` becomes an **orchestrator that fans out to many independent validators**
and merges findings into one machine-readable report (SARIF). Validators are
pluggable so any one can be swapped as tools mature (the user's whole premise).
*Why:* no single scanner is sufficient or durable; aggregate and normalise.
*Borrowed from:* AWS ASH (Automated Security Helper) orchestrating Bandit, Semgrep,
detect-secrets, Checkov, Grype, Syft → unified SARIF, each tool version-pinned and
isolated.
*Build-time:* add a validator chain — **unicode/bidi + hidden-instruction linter**
(closes T4), injection-marker linter, `detect-secrets`/`semgrep` over embedded code,
`grype`/`syft` over declared deps — all emitting to one `ash`-style report the build
gates on. Pin and isolate the validator toolchain itself.

### DG-7 — Two checkpoints: author-time and deploy-time
Scan **source on author/commit** (input moderation) *and* scan **resolved artifacts
before deploy** (output moderation). Two gates, not one.
*Why:* a clean source can still resolve to an unsafe artifact (token expansion,
companion-file merge); AWS notes tool I/O bypasses guardrails by default.
*Borrowed from:* AWS Bedrock dual-layer (input + output) moderation · MAF pre- vs
post-termination middleware.
*Build-time:* a pre-commit/CI hook runs the DG-6 chain over `skills/**`; the existing
post-deploy token-free guardrail extends to also assert no injection vectors or
unresolved-trust artifacts survived into `.github/**`.

### DG-8 — Approval gates are compiled, not prose
Mutating / high-risk steps carry a machine-readable **`approval: always|conditional|
never`** that the resolver compiles into *real* gates for each target — Claude Code
permission entries / hooks, not just an English "please confirm."
*Why:* prose guidance is advisory; a hook is load-bearing (your planner-checkpoint
work in Sprint 2 already learned this lesson).
*Borrowed from:* MAF `ApprovalRequiredAIFunction` / `approval_mode` · AWS
mutation-consent elicitation · Cursor `beforeShellExecution` hooks (`allow|deny|ask`).
*Build-time:* resolver emits per-target gate artifacts from the `approval:` field;
a policy violation downgrades-with-warning (requires explicit author override),
never silently strips.

### DG-9 — Tamper-evident provenance manifest (resolution BOM)
Every build emits a signed/hashed **resolution manifest** next to `resolved/`:
every source file, its trust label, content hash, the validators run, and the
policy decisions applied — a hash-chained audit record.
*Why:* lets a consumer verify exactly what went into a deployed artifact and detect
tampering (T7); operationalises the existing (aspirational) audit-log section.
*Borrowed from:* MAF Decision BOM + Merkle/tamper-evident log · AWS SLSA/in-toto
attestation · the repo's own `scripts/` hash-chain verification.
*Honest scope (corpus anti-hype):* the manifest proves **what the resolver recorded at
build time**, not that a downstream agent behaved correctly. A hash binds the resolver's
inputs→outputs; it is **not** cryptographic proof of agent execution (the corpus
explicitly flags "hashing test output proves the agent ran the tests" as overhyped —
a hash proves an output was recorded, not that a command ran against real code). Pair it
with determinism (DG-10) for tamper-evidence of the *build*; never market it as runtime
assurance.
*Build-time:* extend the deterministic build to write `resolved/PROVENANCE.json`
(+ optional Cosign signature); CI verifies the chain.

### DG-10 — Determinism is a safety property (keep and lean on it)
Byte-identical builds from identical inputs is already enforced — reframe it as a
**security control**: any drift in `resolved/` that isn't explained by a source
change is tamper evidence.
*Borrowed from:* the repo's existing determinism gate; MAF deterministic replay.
*Build-time:* already present — wire it to DG-9 so determinism + provenance together
give tamper detection.

## 5. How this maps to the current architecture

What already exists is a strong foundation — most goals are **extensions, not
rewrites**:

| Existing asset | Extended by |
|----------------|-------------|
| `SecurityValidator` (Phase 0) | becomes one validator in the DG-6 chain |
| protocol-v1 frontmatter schemas | gain `trust:`, `capabilities:`, `approval:` fields (DG-2/4/8) |
| deterministic build + `scripts/` hash-chain | DG-9 provenance manifest + DG-10 |
| post-deploy token-free guardrail | DG-7 deploy-time checkpoint (add injection/trust asserts) |
| `instructions/generic/security-model.instructions.md` | this doc replaces its Roadmap stubs with concrete goals |
| `editor.target` multi-platform emit | DG-8 compiles approval gates per target; DG-5 quarantine emits per target |

**Non-trivial new pieces:** the validator-orchestration layer (DG-6), the trust-label
propagation pass (DG-2), and the imported-skill quarantine + review flow (DG-5).

## 5a. Field validation & re-baseline (241-video corpus)

Distilled from a separate synthesis corpus — 241 ranked notes / 1285 verdict-tagged
claims across 9 channels (OpenAI, IBM, Microsoft, VS Code, Cursor/Anysphere voices,
DeepMind, GitHub, etc.), generated 2026-06-01. Full digest:
`docs/planning/research/youtube-synthesis-digest.md`.

### What it confirms

- **The thesis is corroborated, not invented.** Across the highest-scored talks, the
  recurring *enterprise caveat* is near-identical to this doc's design goals:
  permission scoping, secrets isolation, sandboxed execution, audit logging, dependency
  & security scanning, deterministic CI gates, data/model governance, human
  accountability. Sample frequencies across the 239 dual-lens notes (discriminating
  signals; "audit/license" keyword counts are inflated by broad terms and discounted):
  sandboxed execution **31%**, secrets isolation **31%**, permission scoping **30%**,
  cost/runaway control **26%**, deterministic CI gates **21%**, data/model governance
  **21%**, dependency/security scanning **18%**, human accountability **16%**.
- **Strategic read:** the field is racing on *velocity and autonomy*; safety is named
  almost everywhere as the **gap that blocks production**, rarely as the thing being
  built. That is the opening — agent-enterprise's safety-in-consumption core is a
  differentiator, not a follower's checkbox. (Explicit "prompt injection" mentions are
  only ~7% — the corpus skews to workflow content — so we are early, not late.)

### What it changes (anti-hype re-baseline)

The corpus's `overhyped`-verdict claims are guardrails on what **not** to design around.
The five that altered goals above:

1. *"Hashing test output proves the agent ran the tests."* → DG-9 honest-scope edit:
   provenance proves recording, not execution.
2. *"Approvals + hooks + permissions are sufficient control."* → DG-1: gates are the
   floor, not the whole; defense-in-depth + load-bearing second checkpoint.
3. *"Define risks once, enforce across every run."* → DG-1: allow declared per-context
   exceptions; no single policy covers every tool/tenant.
4. *"Sandbox mode can auto-approve MCP requests."* → DG-4: sandboxing never implies
   auto-approval.
5. *"Context isolation no longer matters for modern models."* → DG-3: scoping still
   matters for injection resistance.

### New concrete patterns to adopt (high-score, verified recipes)

- **Secrets posture in the capability manifest** — read-only secrets by default, scoped
  write tokens only on demand, ephemeral execution (folded into DG-4).
- **Cost/time ceilings** — `maxUsd` / `timeoutMs` / kill-switch as declared limits
  (folded into DG-4, new threat T8).
- **Sanitizer + sandboxed-iframe + CSP** for any generated-content rendering (DG-3).
- **Evidence-gated state machine** — sprint/agent transitions require structured outputs
  + evidence artifacts, not free-form prose; capture stdout/stderr/exit/cwd/git-SHA/
  timestamp (not a `.tested` sentinel). Strengthens the existing return-tier contracts
  and feeds DG-9 — *with* the honesty caveat that recorded ≠ executed.
- **Worktree isolation per agent task** — emit guidance/scaffolding so agent runs use a
  Git worktree, not the primary checkout (cheap blast-radius reduction; widely endorsed).
- **AGENTS.md as agent constitution** — already present here; the corpus validates
  including security rules + feature-flag policy in it explicitly.

## 6. Phased roadmap

Sequenced so each sprint ships a usable increment and the cheap, highest-leverage
anti-injection wins land first. Numbers continue the real sprint history (Sprint 2
complete).

### Sprint 3 — Trust labels + hidden-instruction linter *(foundation, low risk)*
Lands **DG-2 (labels), DG-6 (first validators), DG-7 (author-time gate).**
- Add `trust:` to `frontmatter-v1` schema; default `untrusted` for anything outside
  first-party `skills/**`.
- Build a **unicode/bidi + hidden-instruction linter** (reject zero-width joiners,
  bidi-control chars, "hide this from chat" self-concealment) — closes T4 today.
- Add an injection-marker linter over `untrusted`-labelled fragments.
- Wire both as a pre-commit/CI checkpoint emitting a single JSON report.
- *Highest value-to-effort: this is shippable now and kills the Pillar attack class.*

### Sprint 4 — Capability manifests + default-inert *(DG-1, DG-4)*
- Add `capabilities:` to frontmatter (typed verbs: `shell`, `file:write`,
  `network`, `mcp:<server>`); default-deny.
- Resolver validates body references ⊆ declared capabilities; **fail-closed** build.
- Resolved artifacts inert by default; emit per-target permission scaffolding.
- Non-overridable deny floor that imports/overrides cannot lift.
- **Secrets posture** (read-only default, scoped write tokens) + **cost/time ceilings**
  (`maxUsd`/`timeoutMs`/kill-switch) as declared manifest fields (corpus; closes T8).
- Allow **declared per-context exceptions** to the deny floor (not silent overrides).

### Sprint 5 — Data/instruction quarantine + scanner orchestration *(DG-3, DG-6 full)*
- Resolver wraps `untrusted` reference material in nonce-`<DATA>` blocks with banner.
- Turn `init.py` into the ASH-style orchestrator: integrate `detect-secrets` +
  `semgrep` (embedded code), `syft`/`grype` (declared deps), and a **license scan**
  against the existing `security.license_denylist` config → unified SARIF; pin +
  isolate the toolchain.
- Triaged severity, not all-or-nothing: hard-fail security findings; report
  quality findings as blocker/should-fix/consider/info and track accept/reject rates
  (corpus: "calibrate review for high recall without blocking velocity").
- Deploy-time checkpoint (DG-7) asserts artifacts are clean.

### Sprint 6 — Imported-skill supply chain + provenance BOM *(DG-5, DG-8, DG-9)*
- `skills/_imported/<source>/` quarantine namespace + provenance metadata + checksum;
  resolver refuses `trusted` without recorded review.
- Compile `approval:` → real Claude Code gates/hooks (DG-8).
- Emit `resolved/PROVENANCE.json` (sources, hashes, labels, decisions) + CycloneDX
  SBOM; optional Cosign signing; CI verifies the chain (DG-9).

*(Signing / full SLSA attestation in Sprint 6 is the heaviest item — see Open
Decisions; it can be deferred without blocking DG-1–DG-7.)*

## 7. Non-goals

- **Not a runtime sandbox.** We do not execute or sandbox agents; we make the
  *artifacts they load* safe. (Runtime sandboxing remains a separate, later concern —
  the existing Phase 3 stub.)
- **Not protecting the adopter's end-user app** — that stays out of scope per
  `SECURITY.md`.
- **Not attacker-already-on-the-machine** — local tampering of source is out of scope
  (DG-9 detects it after the fact, doesn't prevent it).
- **No reliance on a downstream model guardrail** — AWS's lesson: tool I/O bypasses
  those by default. Safety lives in *our* pipeline.

## 8. Open decisions (need your call)

1. **Ambition / depth of supply-chain verification.** Full Sigstore signing + SLSA
   attestation (Sprint 6) is real engineering for a Markdown project. Options:
   (a) checksums + provenance JSON only, (b) add Cosign signing, (c) full SLSA L2.
   Recommendation: ship (a) in Sprint 6, treat (b)/(c) as opt-in later — the corpus
   anti-hype on hashing argues against overclaiming what signing buys (it proves
   integrity of *what was recorded*, not correct behaviour).
2. **Validator toolchain dependency.** DG-6 pulls in `semgrep`/`grype`/`syft`/
   `detect-secrets`. Bundle them as required dev deps, or make the orchestrator
   degrade gracefully when a scanner is absent (warn, don't fail)?
3. **Default trust for existing first-party skills.** Confirm everything currently in
   `skills/**` is grandfathered `trusted`, with `untrusted` as the default only for
   *new imported* sources.
4. **Where injection-linting runs.** Pre-commit hook (blocks the author) vs. CI-only
   (blocks the merge) vs. both. Recommendation: both, with pre-commit as a fast
   subset.

## 9. Inspiration sources

| Project | Concepts borrowed | Key refs |
|---------|-------------------|----------|
| Microsoft Agent Framework | FIDES trust labels + untrusted-wins propagation; quarantined-LLM; `ApprovalRequiredAIFunction`; fail-closed policy middleware; Decision BOM; capability minimisation (RCE post-mortem) | `microsoft/agent-framework`, `microsoft/agent-governance-toolkit`, MS Security blog on AI-agent RCE (2026-05) |
| AWS Labs | ASH scanner-orchestration → SARIF (Bandit/Semgrep/detect-secrets/Checkov/Grype/Syft, pinned+isolated); MCP read-only-by-default + mutation-consent; Bedrock nonce-`<DATA>` separation + Plan-Verify-Execute; Sigstore/SLSA + SBOM | `awslabs/automated-security-helper`, `awslabs/mcp`, `awslabs/agent-squad`, Bedrock indirect-prompt-injection guide |
| Cursor | Typed `permissions.json` + deny-floor; "Denylist Delusion" (allowlist-only); `imported/` quarantine namespace + review-as-code; unicode/bidi "Rules File Backdoor"; `beforeShellExecution` hooks; derived rule-activation matrix | Cursor docs (rules, agent/security, CLI permissions), Backslash & Pillar Security research |
| YouTube-Sync corpus (241 ranked notes, 2026-06-01) | Field corroboration of the safety caveat set; anti-hype guardrails (recorded≠executed, gates≠sufficient, sandbox≠auto-approve); concrete recipes — secrets posture, cost ceilings, sandboxed-iframe+CSP, evidence-gated state machine, worktree isolation | `docs/planning/research/youtube-synthesis-digest.md` (distilled via `tools/distill_synthesis.py`) |

---

*Next step: review §8 decisions, then promote Sprint 3 to a sprint draft via @planner.*
