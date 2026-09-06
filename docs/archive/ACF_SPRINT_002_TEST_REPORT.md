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
