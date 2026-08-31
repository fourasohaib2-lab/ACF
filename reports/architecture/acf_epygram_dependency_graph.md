# GRAPHE DE DÉPENDANCES ET D'ARCHITECTURE EPYGRAM (ACF-NWP-EPYGRAM-005)

**Role :** Chief Software Architect & Chief Earth System Architect  
**Date :** 3 août 2026  
**Dépôt :** Atmospheric Complexity Framework (ACF)  

---

## 1. Graphe Complet des Dépendances (ASCII)

```
================================================================================
                    ACF EPYGRAM OFFICIAL DEPENDENCY GRAPH
================================================================================

[METEOROLOGICAL FILE INPUTS]
  │  ├── *.fa / *.fa.gz (ARPEGE / AROME / ALADIN FA Format)
  │  ├── *.lfa (AROME / ALADIN LFA Inline Format)
  │  ├── *.lfi (SURFEX / Surface LFI Format)
  │  ├── *.grib / *.grib2 (WMO GRIB Datasets)
  │  └── *.nc (CF NetCDF Datasets)
  │
  ▼
[FORMAT DETECTION LAYER]
  │  └── FormatDetector (src/acf/data/detector.py)
  │
  ▼
[EPYGRAM & NATIVE BACKEND READERS]
  │  ├── EPyGrAMReader (src/acf/data/readers/epygram_reader.py)
  │  │     └── epygram (Météo-France EPyGrAM 2.1.0)
  │  ├── GRIBReader (src/acf/importers/readers/grib_reader.py)
  │  │     └── xarray + cfgrib + eccodes
  │  └── NetCDFReader (src/acf/importers/readers/netcdf_reader.py)
  │        └── xarray + netcdf4
  │
  ▼
[UNIVERSAL INGESTION & CANONICAL DATASET LAYER]
  │  ├── UniversalDataIngestionEngine (src/acf/data/universal_ingestion.py)
  │  │     ├── ParameterEngine (src/acf/science/parameters/engine.py)
  │  │     └── KnowledgeGraphEngine (src/acf/science/encyclopedia/knowledge_graph/)
  │  └── Dataset (src/acf/data/dataset.py)
  │
  ▼
[NWP MODEL ADAPTERS LAYER - src/acf/models/]
  │  ├── ARPEGEIngestionAdapter (src/acf/models/arpege/)
  │  ├── AROMEIngestionAdapter (src/acf/models/arome/)
  │  ├── ALADINIngestionAdapter (src/acf/models/aladin/)
  │  └── Model Drivers (IFS, ICON, WRF, ERA5, GEFS, GFS)
  │
  ▼
[HPC WORKFLOW ORCHESTRATION LAYER - src/acf/hpc_workflow/]
  │  ├── WorkflowEngine (src/acf/hpc_workflow/workflow_engine.py)
  │  ├── AROMEWorkflow (src/acf/hpc_workflow/arome/)
  │  └── ALADINWorkflow (src/acf/hpc_workflow/aladin/)
  │
  ▼
[OPERATIONAL DOWNSTREAM EXPLOITATION]
     ├── ESOC Workstation Interface (src/acf/gui/esoc/)
     ├── MapEngine & AWCI Rendering (src/acf/maps/ & src/acf/gui/map/)
     ├── Science & Physics Solvers (src/acf/science/ & src/acf/simulation_engine/)
     └── AI Forecast Intelligence (src/acf/intelligence/)

================================================================================
```

---

## 2. Graphe Séquentiel du Flux d'Ingestion

```
[Input File] ──► [FormatDetector] ──► [EPyGrAMReader] ──► [UniversalDataIngestionEngine]
                                                                  │
                                                                  ▼
 [Visualisation / AI / HPC] ◄── [NWP Model Adapters] ◄── [Dataset ACF]
```
