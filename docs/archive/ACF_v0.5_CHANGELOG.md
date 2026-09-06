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

# ACF CHANGELOG — RELEASE v0.5.0

All notable changes to the Atmospheric Complexity Framework for version 0.5.0 are documented below.

## [v0.5.0] - 2026-08-06

### Added
- Added `UniversalModelRunner` in `src/acf/hpc_connector/model_runner.py` for 7 NWP models.
- Added `HPCWorkflowManager` in `src/acf/hpc_connector/workflow_manager.py` for DAG workflow orchestration.
- Added `HPCExecutionPanel` in `src/acf/gui/esoc/hpc_execution_panel.py` for PySide6 ESOC execution UI.
- Added `tests/test_model_runner.py` and `tests/test_hpc_workflow_manager.py`.
