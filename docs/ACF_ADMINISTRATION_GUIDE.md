# ACF ADMINISTRATION GUIDE (ACF-POST-001)

## 1. HPC CLUSTER & ENVIRONMENT ADMINISTRATION

- **Slurm Connector Settings**: Configured in `config/hpc.yaml` and `config/hpc_profiles/`.
- **Target HPC Host**: `login2.fennec.meteo.dz` (`Researches` partition).
- **Module Manifest Administration**: Managed via `src/acf/master/module_manifest.py` tracking maturity levels (`Prototype`, `Beta`, `Stable`, `Production`).
