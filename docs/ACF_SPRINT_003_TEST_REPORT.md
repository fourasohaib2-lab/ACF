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

# ACF SPRINT-003 TEST REPORT (ACF-EXEC-003)

| Test Case Name | Test File | Assertions Checked | Status |
| :--- | :--- | :--- | :---: |
| `test_prepare_case_supported_models` | `tests/test_model_runner.py` | Directory structure & case metadata for 7 models | **PASS** |
| `test_prepare_case_unsupported_model` | `tests/test_model_runner.py` | Exception handling on invalid model name | **PASS** |
| `test_submit_and_monitor` | `tests/test_model_runner.py` | Slurm script generation & monitoring | **PASS** |
| `test_cancel_restart_archive` | `tests/test_model_runner.py` | Job cancellation, restart & archival | **PASS** |
| `test_create_nwp_workflow` | `tests/test_hpc_workflow_manager.py` | DAG stage dependency graph creation | **PASS** |
| `test_run_workflow_execution` | `tests/test_hpc_workflow_manager.py` | Workflow execution and stage status tracking | **PASS** |
| **Total Test Suite** | `tests/test_model_runner.py` & `test_hpc_workflow_manager.py` | **6 / 6 Tests Passed (100.0%)** | **PASS** |
