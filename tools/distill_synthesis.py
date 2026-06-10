"""One-off distiller for the youtube-sync synthesis report.
Parses the embedded DATA blob, ranks/filters for agent-enterprise relevance,
and emits a compact markdown digest. Not part of the build."""
import json, re, sys, io
from collections import Counter

SRC = r"D:\Cowork projects\youtube-sync\docs\synthesis-report.html"
OUT = r"D:\VS\agent-enterprise\docs\planning\research\youtube-synthesis-digest.md"

line = open(SRC, encoding="utf-8").readlines()[135].strip()
blob = line[len("const DATA = "):].rstrip(";")
DATA = json.loads(blob)

def txt(n, *keys):
    s = " ".join(str(n.get(k, "")) for k in keys)
    for c in n.get("claims", []):
        s += " " + c.get("text", "") + " " + (c.get("assessment") or "")
    for sk in n.get("skills", []):
        s += " " + sk.get("name", "") + " " + sk.get("recipe", "")
    le = n.get("lens", {}) or {}
    s += " " + (le.get("enterprise") or "") + " " + (le.get("homelab") or "")
    s += " " + " ".join(n.get("keypoints", []) or [])
    return s.lower()

# Themes relevant to agent-enterprise's design core
THEMES = {
    "safety/injection": ["prompt inject", "injection", "jailbreak", "guardrail", "red team",
                          "adversaria", "poison", "untrusted", "sanitiz", "content safety"],
    "supply-chain": ["supply chain", "sbom", "dependenc", "package", "provenance", "sign",
                     "sigstore", "slsa", "cve", "vulnerab", "npm", "pinning", "attestation"],
    "permissions/sandbox": ["permission", "sandbox", "least privilege", "capabilit",
                            "allowlist", "denylist", "isolation", "egress", "approval", "trust boundar"],
    "agent-architecture": ["multi-agent", "orchestrat", "subagent", "sub-agent", "context window",
                           "handoff", "middleware", "agent loop", "tool call", "mcp", "skill"],
    "context/memory": ["context engineering", "memory", "rag", "retrieval", "compaction", "context rot"],
    "eval/verification": ["eval", "verifier", "verification", "benchmark", "deterministic",
                          "reproducib", "regression", "observability", "telemetry", "trace"],
    "enterprise-ops": ["enterprise", "governance", "compliance", "audit", "production", "ci/cd",
                       "deploy", "rollback", "cost", "scal"],
}

def themes_for(n):
    body = txt(n, "title", "summary", "channel")
    return [t for t, kws in THEMES.items() if any(k in body for k in kws)]

for n in DATA:
    n["_themes"] = themes_for(n)
    n["_score"] = n.get("score") or 0
    n["_ent"] = (n.get("lens", {}) or {}).get("enterprise") or ""

out = io.StringIO()
W = out.write

W(f"# YouTube-Sync Synthesis — Distilled Digest\n\n")
W(f"_Auto-distilled from `synthesis-report.html` ({len(DATA)} notes). "
  f"Filtered & ranked for agent-enterprise relevance._\n\n")

# Corpus stats
ch = Counter(n.get("channel", "?") for n in DATA)
vd = Counter(c.get("status") for n in DATA for c in n.get("claims", []))
W("## Corpus shape\n\n")
W(f"- {len(DATA)} notes · {sum(len(n.get('claims',[])) for n in DATA)} claims\n")
W(f"- Verdicts: " + ", ".join(f"{k} {v}" for k, v in vd.most_common()) + "\n")
W(f"- Channels: " + ", ".join(f"{k} ({v})" for k, v in ch.most_common()) + "\n")
tc = Counter(t for n in DATA for t in n["_themes"])
W(f"- Theme coverage: " + ", ".join(f"{k} {v}" for k, v in tc.most_common()) + "\n\n")

# Top notes overall (highest signal)
W("## Top 30 notes by score\n\n")
for n in sorted(DATA, key=lambda n: -n["_score"])[:30]:
    th = ",".join(n["_themes"]) or "—"
    W(f"- **{n['_score']}** · {n.get('channel','?')} · _{th}_ · {n.get('title','')[:90]}\n")
W("\n")

# Per-theme: top notes + their verified & overhyped claims
W("## By theme — verified signal vs overhyped\n\n")
for t in THEMES:
    notes = sorted([n for n in DATA if t in n["_themes"]], key=lambda n: -n["_score"])
    if not notes:
        continue
    W(f"### {t}  ({len(notes)} notes)\n\n")
    for n in notes[:8]:
        W(f"- **{n['_score']}** {n.get('title','')[:85]} — _{n.get('channel','')}_\n")
        ver = [c for c in n.get("claims", []) if c.get("status") == "verified"]
        over = [c for c in n.get("claims", []) if c.get("status") == "overhyped"]
        for c in ver[:2]:
            W(f"    - ✅ {c['text'][:200]}\n")
        for c in over[:1]:
            a = (" — " + c["assessment"][:120]) if c.get("assessment") else ""
            W(f"    - ⚠️ OVERHYPED: {c['text'][:160]}{a}\n")
    W("\n")

# Actionable skills, enterprise-leaning, from high-score notes
W("## Actionable skills (score>=80, enterprise/safety themes)\n\n")
seen = set()
rel = {"safety/injection", "supply-chain", "permissions/sandbox",
       "agent-architecture", "eval/verification", "enterprise-ops"}
for n in sorted(DATA, key=lambda n: -n["_score"]):
    if n["_score"] < 80 or not (set(n["_themes"]) & rel):
        continue
    for sk in n.get("skills", []) or []:
        key = sk.get("name", "")[:50]
        if key in seen or not key:
            continue
        seen.add(key)
        W(f"- **{sk['name']}** — {sk.get('recipe','')[:220]}  _(src: {n.get('channel','')}, {n['_score']})_\n")
        if len(seen) >= 40:
            break
    if len(seen) >= 40:
        break
W("\n")

# Enterprise-lens takes from top safety/supply/perm notes
W("## Enterprise-lens takes (top safety & supply-chain notes)\n\n")
core = {"safety/injection", "supply-chain", "permissions/sandbox"}
for n in sorted([n for n in DATA if set(n["_themes"]) & core], key=lambda n: -n["_score"])[:15]:
    if n["_ent"]:
        W(f"- **{n.get('title','')[:80]}** ({n['_score']}): {n['_ent'][:300]}\n")
W("\n")

# QUANTIFIED: how often does each safety caveat recur across ALL enterprise+homelab lens texts?
W("## Caveat frequency across all dual-lens takes (corroboration signal)\n\n")
CAVEATS = {
    "prompt injection": ["prompt inject", "injection"],
    "secrets isolation": ["secret", "credential", "token scope", "scoped write", "read-only secret"],
    "permission scoping": ["permission", "least privilege", "scoped", "access control", "identity-aware"],
    "audit logging": ["audit", "traceab", "observab", "log"],
    "sandboxed execution": ["sandbox", "isolation", "ephemeral container", "worktree", "tenant isolat"],
    "dependency/security scanning": ["dependency", "security scan", "sast", "vulnerab", "supply chain"],
    "license/governance": ["license", "governance", "compliance", "policy"],
    "deterministic CI gates": ["ci gate", "deterministic", "quality gate", "regression", "reproducib"],
    "data/model governance": ["data governance", "model provenance", "data classification", "retention", "data leak"],
    "human accountability/approval": ["human accountab", "human approval", "explicit approval", "hitl", "human in the loop"],
    "cost/runaway control": ["cost", "budget", "kill switch", "quota"],
}
lens_blobs = []
for n in DATA:
    le = n.get("lens", {}) or {}
    b = ((le.get("enterprise") or "") + " " + (le.get("homelab") or "")).lower()
    if b.strip():
        lens_blobs.append(b)
W(f"_Across {len(lens_blobs)} notes with a dual-lens take:_\n\n")
freq = []
for label, kws in CAVEATS.items():
    c = sum(1 for b in lens_blobs if any(k in b for k in kws))
    freq.append((c, label))
for c, label in sorted(freq, reverse=True):
    pct = round(100 * c / max(1, len(lens_blobs)))
    W(f"- **{label}** — {c} notes ({pct}%)\n")
W("\n")

# Overhyped claims = "do not oversell" guardrails. Collect distinct ones touching our themes.
W("## Overhyped claims to NOT design around (anti-hype guardrails)\n\n")
HOT = ["agent", "orchestrat", "autonom", "review", "proof", "prove", "hash", "test",
       "memory", "scal", "factory", "verif", "context"]
seen_over = set()
overs = []
for n in DATA:
    for c in n.get("claims", []):
        if c.get("status") != "overhyped":
            continue
        t = c.get("text", "")
        if not any(h in t.lower() for h in HOT):
            continue
        key = t[:60].lower()
        if key in seen_over:
            continue
        seen_over.add(key)
        overs.append((n["_score"], t, c.get("assessment") or ""))
for sc, t, a in sorted(overs, reverse=True)[:25]:
    W(f"- ({sc}) **{t[:170]}**\n")
    if a:
        W(f"    - reality: {a[:200]}\n")
W("\n")

open(OUT, "w", encoding="utf-8").write(out.getvalue())
print(f"wrote {OUT}")
print(f"digest length: {len(out.getvalue())} chars")
