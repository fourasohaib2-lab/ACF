# GRAPHE DE DÉPENDANCES DU SOUS-SYSTÈME NWP ACF (ACF-NWP-001)

**Role :** Chief NWP Architect & Chief Earth System Architect  
**Date :** 3 août 2026  
**Dépôt :** Atmospheric Complexity Framework (ACF)  

---

## 1. Graphe de Dépendances Unifié (ASCII)

```
================================================================================
                    ACF UNIFIED NWP DEPENDENCY GRAPH
================================================================================

[RAW MODEL OUTPUTS & DATASETS]
  │  ├── Météo-France: FA, LFA, LFI (AROME, ARPEGE, ALADIN, SURFEX)
  │  ├── ECMWF: GRIB2, NetCDF (IFS, OpenIFS, ERA5)
  │  ├── NOAA: GRIB2 (GFS, GEFS)
  │  ├── DWD: GRIB2, NetCDF (ICON)
  │  └── NCAR: NetCDF (WRF)
  │
  ▼
[EPYGRAM & UNIVERSAL INGESTION LAYER]
  │  ├── EPyGrAMReader (src/acf/data/readers/epygram_reader.py)
  │  ├── UniversalDataIngestionEngine (src/acf/data/universal_ingestion.py)
  │  └── Dataset (src/acf/data/dataset.py)
  │
  ▼
[NWP MODEL ADAPTERS & DRIVERS - src/acf/models/]
  │  ├── BaseWeatherModel (src/acf/models/base_model.py)
  │  ├── ARPEGEIngestionAdapter / ARPEGEModel
  │  ├── AROMEIngestionAdapter / AROMEModel
  │  ├── ALADINIngestionAdapter / ALADINModel
  │  └── IFSModel, ERA5Model, GFSModel, GEFSModel, ICONModel, WRFModel
  │
  ▼
[HPC ORCHESTRATION & PIPELINES - src/acf/hpc_workflow/]
  │  ├── WorkflowEngine (12-stage forecasting cycle execution)
  │  ├── JobManager & SchedulerInterface (SLURM / PBS submission)
  │  └── RemoteExecutor & FileTransfer (Cluster staging)
  │
  ▼
[EXPLOITATION & DECISION SUPPORT]
     ├── ESOC Workstation Interface (src/acf/gui/esoc/)
     ├── MapEngine Canvas & AWCI Rendering (src/acf/maps/)
     ├── Physics Solvers (src/acf/simulation_engine/ & src/acf/earth_physics/)
     └── AI Forecast & Causal Reasoning (src/acf/intelligence/)

================================================================================
```
