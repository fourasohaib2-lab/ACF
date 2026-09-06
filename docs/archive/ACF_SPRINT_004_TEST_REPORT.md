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

# ACF SPRINT-004 TEST REPORT (ACF-EXEC-004)

| Test Case Name | Test File | Assertions Checked | Status |
| :--- | :--- | :--- | :---: |
| `test_forecast_config_defaults` | `tests/test_forecast_config.py` | Config initialization & validation rules | **PASS** |
| `test_forecast_config_json_serialization` | `tests/test_forecast_config.py` | JSON serialization and deserialization | **PASS** |
| `test_preprocessing_validation` | `tests/test_preprocessing.py` | File existence, size & format detector checks | **PASS** |
| `test_postprocessing_engine_products` | `tests/test_postprocessing.py` | Map generation, time series, profiles, NetCDF/TIFF exports | **PASS** |
| **Total Test Suite** | `tests/test_forecast_config.py`, `test_preprocessing.py`, `test_postprocessing.py` | **4 / 4 Tests Passed (100.0%)** | **PASS** |
