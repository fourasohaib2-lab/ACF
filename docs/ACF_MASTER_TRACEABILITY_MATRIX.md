# ACF MASTER TRACEABILITY MATRIX

| Requirement / Capability | WBS Element | Target Module | Sprint | Test File |
| :--- | :--- | :--- | :---: | :--- |
| **FA/LFA/LFI Spectral Data Ingestion** | 1.1.1 | `src/acf/data/readers/epygram_reader.py` | SPRINT-001 | `tests/test_epygram_reader.py` |
| **Real-time Slurm Cluster Monitoring** | 1.2.1 | `src/acf/hpc_connector/hpc_monitor.py` | SPRINT-002 | `tests/test_hpc_monitor.py` |
| **NWP Universal Execution API** | 1.2.2 | `src/acf/hpc_connector/model_runner.py` | SPRINT-003 | `tests/test_model_runner.py` |
| **Structured Forecast Configuration** | 1.3.1 | `src/acf/models/forecast_config.py` | SPRINT-004 | `tests/test_forecast_config.py` |
| **Single Open(...) Universal Reader** | 1.1.2 | `src/acf/data/universal_reader.py` | SPRINT-005 | `tests/test_universal_reader.py` |
| **NWP Verification Score Calculation** | 1.3.3 | `src/acf/verification/nwp_metrics.py` | SPRINT-005 | `tests/test_nwp_metrics.py` |
| **Module Manifest & Maturity Tracking**| 1.4.2 | `src/acf/master/module_manifest.py` | SPRINT-005 | `tests/test_module_manifest.py` |
