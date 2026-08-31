# APPENDIX A — COMPLETE MODULE REGISTRY (ACF-MISSION-001A)

| Module ID | Module Name | Directory | Scientific Domain | Status | Version | Owner | Test Coverage | Maturity |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- | :---: | :---: |
| **MOD-DATA-01** | `universal_reader` | `src/acf/data/` | Data Ingestion | Production | 1.0.0 | Chief Data Architect | 100% | Production |
| **MOD-DATA-02** | `epygram_reader` | `src/acf/data/readers/` | NWP Formats (FA/LFA/LFI) | Production | 2.1.0 | Chief NWP Architect | 100% | Production |
| **MOD-DATA-03** | `preprocessing` | `src/acf/data/` | Preprocessing & Validation | Production | 1.0.0 | Chief Data Architect | 100% | Production |
| **MOD-HPC-01** | `hpc_monitor` | `src/acf/hpc_connector/` | HPC Slurm Monitoring | Production | 2.0.0 | Chief HPC Architect | 100% | Production |
| **MOD-HPC-02** | `model_runner` | `src/acf/hpc_connector/` | Universal Model Engine | Production | 1.0.0 | Chief HPC Architect | 100% | Production |
| **MOD-HPC-03** | `workflow_manager` | `src/acf/hpc_connector/` | Workflow DAG Scheduler | Production | 1.0.0 | Chief HPC Architect | 100% | Production |
| **MOD-NWP-01** | `forecast_config` | `src/acf/models/` | Forecast Configuration | Production | 1.0.0 | Chief NWP Architect | 100% | Production |
| **MOD-NWP-02** | `base_model` | `src/acf/models/` | Universal Base Model API | Production | 1.0.0 | Chief NWP Architect | 100% | Production |
| **MOD-VERIF-01**| `nwp_metrics` | `src/acf/verification/` | NWP Verification Metrics | Production | 1.0.0 | Chief QA Engineer | 100% | Production |
| **MOD-POST-01** | `postprocessing` | `src/acf/analysis/` | Post-Processing Engine | Production | 1.0.0 | Chief Scientific Architect | 100% | Production |
| **MOD-GUI-01** | `nwp_forecast_center` | `src/acf/gui/esoc/` | ESOC Command Center | Production | 1.0.0 | Chief UI Architect | 100% | Production |
| **MOD-MAST-01** | `module_manifest` | `src/acf/master/` | Module Maturity Manifest | Production | 1.0.0 | Chief Systems Architect | 100% | Production |
