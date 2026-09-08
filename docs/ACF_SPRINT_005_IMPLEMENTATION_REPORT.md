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

# ACF SPRINT-005 IMPLEMENTATION REPORT (ACF-EXEC-005)

## 1. IMPLEMENTATION DETAILS

- **Target Files**:
  - `src/acf/verification/nwp_metrics.py` (`NWPVerificationMetrics`)
  - `src/acf/gui/esoc/nwp_forecast_center_panel.py` (`NWPForecastCenterPanel`)
- **APIs Provided**:
  - `NWPVerificationMetrics.calculate_continuous_metrics(obs, fcst, climatology=None)`: Evaluates RMSE, MAE, BIAS, ACC for T2M, U10M, V10M, MSLP, RH2M, RR24, Z500, T850, U250, V250, Q700.
  - `NWPVerificationMetrics.calculate_categorical_metrics(obs, fcst, threshold)`: Computes 2x2 contingency matrix, ETS, CSI, POD, FAR for precipitation and severe events.
  - `NWPVerificationMetrics.generate_verification_report(obs, fcst, variables, thresholds)`: Compiles full JSON scorecards and summary reports.
  - `NWPForecastCenterPanel`: PySide6 ESOC panel rendering verification scorecards, metric evolution curves, and model comparison tables.
