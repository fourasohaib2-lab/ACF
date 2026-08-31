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
