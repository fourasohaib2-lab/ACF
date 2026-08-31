# ACF SPRINT-003 SCIENTIFIC VALIDATION REPORT (ACF-EXEC-003)

## 1. SCIENTIFIC & WORKFLOW VALIDATION

- **NWP Models Validated**: **ARPEGE**, **AROME**, **ALADIN**, **WRF**, **ICON**, **OpenIFS**, **IFS**.
- **DAG Workflow Lifecycle**: 6-stage operational pipeline (`PRE_PROCESSING` → `INITIALIZATION` → `FORECAST` → `POST_PROCESSING` → `VERIFICATION` → `ARCHIVING`).
- **Checkpoint Recovery**: Automatic restart from specified checkpoint forecast steps (`fort.4` namelist update).
