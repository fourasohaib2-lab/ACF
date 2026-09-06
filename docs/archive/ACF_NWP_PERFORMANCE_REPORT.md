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

# ACF NWP PERFORMANCE REPORT (ACF-LTS-002)

| NWP Subsystem | Operation | Measured Duration | Benchmark Status |
| :--- | :--- | :---: | :---: |
| **Data Ingestion** | EPyGrAM 1.3km AROME FA format read | 0.85 s | **PASS** |
| **Preprocessing** | Format validation & observation matching | 10 ms | **PASS** |
| **Model Runner** | Batch script submission & setup | 15 ms | **PASS** |
| **Postprocessing** | GeoTIFF & CF-1.8 NetCDF4 export | 22 ms | **PASS** |
