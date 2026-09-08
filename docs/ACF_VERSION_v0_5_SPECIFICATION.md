# RELEASE SPECIFICATION — ACF v0.5

**Milestone:** Unified NWP Model Execution Engine & Workflow Manager  
**Target Release Date:** Sprint 3  
**Maturity Goal:** Production for Model Execution  

---

## 1. Objectives & Scope
- **Engineering Goal**: `UniversalModelRunner` API (`prepare_case`, `submit`, `monitor`, `cancel`, `restart`, `archive`).
- **Workflow Goal**: `HPCWorkflowManager` DAG execution (`PRE_PROCESSING` → `INITIALIZATION` → `FORECAST` → `POST_PROCESSING` → `VERIFICATION` → `ARCHIVING`).
- **Exit Criteria**: `test_model_runner.py` and `test_hpc_workflow_manager.py` 100% pass.
