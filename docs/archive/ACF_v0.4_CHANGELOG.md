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

# ACF CHANGELOG — RELEASE v0.4.0

All notable changes to the Atmospheric Complexity Framework for version 0.4.0 are documented below.

## [v0.4.0] - 2026-08-06

### Added
- Added `EPyGrAMReader` in `src/acf/data/readers/epygram_reader.py` for FA/LFA/LFI format support.
- Added `HPCMonitor` in `src/acf/hpc_connector/hpc_monitor.py` for Slurm cluster monitoring.
- Added `HPCDashboard` in `src/acf/hpc_connector/hpc_dashboard.py` for health score calculation.
- Added `HPCDashboardPanel` in `src/acf/gui/esoc/hpc_dashboard_panel.py` for ESOC operations UI.
- Added `tests/test_epygram_reader.py`, `tests/test_hpc_monitor.py`, and `tests/test_hpc_dashboard.py`.
