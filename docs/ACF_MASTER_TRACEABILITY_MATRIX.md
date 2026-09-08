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

# ACF MASTER TRACEABILITY MATRIX

| Requirement / Capability | WBS Element | Target Module | Sprint | Test File |
| :--- | :--- | :--- | :---: | :--- |
| **FA/LFA/LFI Spectral Data Ingestion** | 1.1.1 | `src/acf/data/readers/epygram_reader.py` | SPRINT-001 | `tests/test_epygram_reader.py` |
| **Real-time Slurm Cluster Monitoring** | 1.2.1 | `src/acf/hpc_connector/hpc_monitor.py` | SPRINT-002 | `tests/test_hpc_monitor.py` |
| **NWP Universal Execution API** | 1.2.2 | `src/acf/hpc_connector/model_runner.py` | SPRINT-003 | `tests/test_model_runner.py` |
| **Structured Forecast Configuration** | 1.3.1 | `src/acf/models/forecast_config.py` | SPRINT-004 | `tests/test_forecast_config.py` |
| **Single Open(...) Universal Reader** | 1.1.2 | `src/acf/data/universal_reader.py` | SPRINT-005 | `tests/test_universal_reader.py` |
| **NWP Verification Score Calculation** | 1.3.3 | `src/acf/verification/nwp_metrics.py` | SPRINT-005 | `tests/test_nwp_metrics.py` |
| **Module Manifest & Maturity Tracking**| 1.4.2 | `src/acf/master/module_manifest.py` | SPRINT-005 | `tests/test_module_manifest.py` |
