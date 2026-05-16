# 05 — Audit: OPA Rego Policy Pressure Test

> **Depends on:** Nothing (read-only analysis, can run anytime)
> **Commit:** `docs(audit): OPA Rego policy catch-rate assessment`
> **Verify:** `docs/POLICY_AUDIT.md` exists with concrete data and recommendation

---

## Task Group 4.1: Pressure-test OPA Rego policy catch rate

Files: `docs/POLICY_AUDIT.md`, `policies/composition.rego`, `policies/security.rego`

**Why:** OPA Rego is the most unique feature and most expensive dependency. Need ROI data.

- [ ] Audit git history: count violations flagged by `composition.rego` in CI or manual runs
- [ ] Audit git history: count violations caught by `security.rego`
- [ ] Assess false positive rate
- [ ] Document findings in `docs/POLICY_AUDIT.md` with concrete data
- [ ] Include clear recommendation: keep / simplify / fold into init.py

---

## Verification

```powershell
Test-Path docs/POLICY_AUDIT.md  # True
# File contains: violation counts, false positive rate, recommendation
```
