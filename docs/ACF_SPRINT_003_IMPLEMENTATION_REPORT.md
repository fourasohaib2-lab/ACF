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

# ACF SPRINT-003 IMPLEMENTATION REPORT (ACF-EXEC-003)

## 1. IMPLEMENTATION DETAILS

- **Target Files**:
  - `src/acf/hpc_connector/model_runner.py` (`UniversalModelRunner`)
  - `src/acf/hpc_connector/workflow_manager.py` (`HPCWorkflowManager`)
  - `src/acf/gui/esoc/hpc_execution_panel.py` (`HPCExecutionPanel`)
- **APIs Provided**:
  - `UniversalModelRunner.prepare_case()`: Prepares work directories, namelists, and boundary conditions.
  - `UniversalModelRunner.submit()`: Generates and submits Slurm batch script for target NWP model.
  - `UniversalModelRunner.monitor()`: Tracks job execution state via `HPCMonitor`.
  - `UniversalModelRunner.cancel()` & `restart()`: Controls execution life cycle and checkpoint recovery.
  - `UniversalModelRunner.collect_outputs()` & `archive()`: Organizes output datasets.
  - `HPCWorkflowManager.create_nwp_workflow()`: Builds 6-stage operational DAG (`PRE_PROCESSING` → `INITIALIZATION` → `FORECAST` → `POST_PROCESSING` → `VERIFICATION` → `ARCHIVING`).
