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

# ACF SPRINT-002 IMPLEMENTATION REPORT (ACF-EXEC-002)

## 1. IMPLEMENTATION DETAILS

- **Target Files**:
  - `src/acf/hpc_connector/hpc_monitor.py` (`HPCMonitor`)
  - `src/acf/hpc_connector/hpc_dashboard.py` (`HPCDashboard`)
  - `src/acf/gui/esoc/hpc_dashboard_panel.py` (`HPCDashboardPanel`)
- **APIs Provided**:
  - `HPCMonitor.list_jobs()`: Live Slurm queue inspection via `squeue`.
  - `HPCMonitor.get_job_history(job_id)`: Historical job state via `sacct`.
  - `HPCMonitor.cluster_status()`: Partition & node states via `sinfo`.
  - `HPCMonitor.node_status()`: Hardware resource details via `scontrol`.
  - `HPCDashboard.refresh()` & `health_score()`: Summary metrics & health scoring for ESOC.
