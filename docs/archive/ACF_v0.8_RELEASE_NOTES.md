<!-- ACF_RECONCILIATION_BANNER_2026-09-02 -->
> **⚠️ Historical / unverified document.** This file was auto-generated as part
> of an earlier documentation sprint, and its completion, certification, or
> "100%"-style claims were not independently reproduced. For the actual,
> reproducible test/status numbers, see [`ROADMAP.md`](../ROADMAP.md) and
> [`README.md`](../README.md)'s "Verified Status" section; for what has
> genuinely been audited and fixed since, see
> [`ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md`](ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md).
> Treat any specific number, percentage, or "CERTIFIED"/"COMPLETE" claim below
> as aspirational unless it also appears in one of those documents.
>
> _Banner added 2026-09-02 per `ROADMAP.md`'s "reconcile ~150 certificate/
> sprint-report documents" near-term priority — original content preserved
> unchanged below._

---

# ACF v0.8 RELEASE NOTES

**Release Version:** v0.8.0  
**Release Date:** August 6, 2026  

---

## 🚀 Key Highlights & New Capabilities

1. **Data Assimilation Engine (`DataAssimilationEngine`)**:
   - Integrated observation processing pipeline supporting Doppler radial wind, radar reflectivity, satellite radiances, and brightness temperatures.
2. **Multi-Method Assimilation Solvers**:
   - Unified analysis increment $x_a = x_b + K (y - H(x_b))$ solver supporting 3D-Var, 4D-Var, and Ensemble Kalman Filter (EnKF) assimilation cycles.
3. **Automated Observation Quality Control (QC)**:
   - Range checks, spatial consistency checks, and observation operator $H$ evaluations.
