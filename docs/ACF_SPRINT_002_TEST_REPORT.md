# ACF SPRINT-002 TEST REPORT (ACF-EXEC-002)

| Test Case Name | Test File | Assertions Checked | Status |
| :--- | :--- | :--- | :---: |
| `test_list_jobs` | `tests/test_hpc_monitor.py` | Queue parsing & dictionary output | **PASS** |
| `test_get_job_history` | `tests/test_hpc_monitor.py` | Exit code and runtime extraction | **PASS** |
| `test_cluster_status` | `tests/test_hpc_monitor.py` | Idle, allocated, down nodes breakdown | **PASS** |
| `test_node_status` | `tests/test_hpc_monitor.py` | CPU and memory availability | **PASS** |
| `test_health_score` | `tests/test_hpc_dashboard.py` | Cluster health score calculation | **PASS** |
| `test_export_json` | `tests/test_hpc_dashboard.py` | Dashboard summary JSON export | **PASS** |
| **Total Test Suite** | `tests/test_hpc_monitor.py` & `test_hpc_dashboard.py` | **10 / 10 Tests Passed (100.0%)** | **PASS** |
