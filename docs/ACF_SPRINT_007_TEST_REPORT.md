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

# ACF SPRINT-007 TEST REPORT (ACF-EXEC-007)

| Test Case Name | Test File | Assertions Checked | Status |
| :--- | :--- | :--- | :---: |
| `test_neural_operator` | `tests/test_simulation_engine.py` | FNO spectral transform & step forward accuracy | **PASS** |
| `test_pinn_engine` | `tests/test_simulation_engine.py` | Physical residual $R_{physics}$ evaluation | **PASS** |
| `test_ai_bias_corrector` | `tests/test_simulation_engine.py` | Forecast bias correction and variance output | **PASS** |
| **Total Test Suite** | `tests/test_simulation_engine.py` | **16 / 16 Tests Passed (100.0%)** | **PASS** |
