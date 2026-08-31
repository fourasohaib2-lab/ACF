# ACF v0.5 RELEASE NOTES

**Release Version:** v0.5.0  
**Release Date:** August 6, 2026  

---

## 🚀 Key Highlights & New Capabilities

1. **Universal NWP Model Execution Engine (`UniversalModelRunner`)**:
   - Unified execution interface (`prepare_case`, `submit`, `monitor`, `cancel`, `restart`, `collect_outputs`, `archive`) for ARPEGE, AROME, ALADIN, WRF, ICON, OpenIFS, and IFS.
2. **Operational Workflow DAG Manager (`HPCWorkflowManager`)**:
   - Automated 6-stage DAG workflow execution (`PRE_PROCESSING` → `INITIALIZATION` → `FORECAST` → `POST_PROCESSING` → `VERIFICATION` → `ARCHIVING`).
3. **ESOC Operations Center HPCExecutionPanel**:
   - PySide6 interactive workflow execution control panel (Start, Pause, Resume, Cancel, Restart).
