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

# ACF SPRINT-001 SCIENTIFIC VALIDATION REPORT (ACF-EXEC-001)

## 1. SCIENTIFIC VALIDATION SUMMARY

- **Data Models Validated**: Météo-France **AROME** (1.3 km Lambert conformal grid), **ARPEGE** (global stretched grid), **ALADIN** (regional grid).
- **Physical Fields Verified**: Temperature (`T`), Specific Humidity (`Q`), Wind Components (`U`, `V`), Surface Pressure (`P`), Geopotential (`Z`).
- **Physical Conservation**: Spectral transform to grid-point conversion verified bit-reproducible across test datasets.
