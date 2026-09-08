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

# ACF SPRINT SPECIFICATION — SPRINT 002

**Sprint ID:** SPRINT-002  
**Version Target:** ACF v0.4  
**Title:** Slurm HPC Monitoring Engine & ESOC Dashboard  
**Status:** Completed & Tested (10/10 tests pass)  

---

## 1. Objectives & Scope
- **File Target**: `src/acf/hpc_connector/hpc_monitor.py` & `src/acf/hpc_connector/hpc_dashboard.py`
- **GUI Target**: `src/acf/gui/esoc/hpc_dashboard_panel.py`
- **Test Target**: `tests/test_hpc_monitor.py` & `tests/test_hpc_dashboard.py`.
