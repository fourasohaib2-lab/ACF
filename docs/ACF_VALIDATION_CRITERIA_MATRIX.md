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

# ACF VALIDATION CRITERIA MATRIX (ACF-VAL-001)

| Parameter | Reference Source | Metric | Target Threshold |
| :--- | :--- | :--- | :---: |
| **2m Temperature (T2M)** | SYNOP Stations | RMSE / BIAS | RMSE < 1.5 K \| \|BIAS\| < 0.5 K |
| **10m Wind Speed (U10/V10)** | SYNOP / Scatterometer | RMSE / MAE | RMSE < 2.0 m/s |
| **Mean Sea Level Pressure (MSLP)** | SYNOP | RMSE / ACC | RMSE < 1.0 hPa \| ACC > 0.98 |
| **500 hPa Geopotential Height** | TEMP Radiosondes | ACC | ACC > 0.95 (at 5-day lead) |
| **24h Accum. Precipitation** | SYNOP / Radar | ETS / CSI | ETS > 0.30 (> 10mm threshold) |
