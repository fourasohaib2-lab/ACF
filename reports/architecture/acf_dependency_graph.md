# GRAPHE DE DÉPENDANCES D'INGESTION ACF (ACF-ARCH-INGESTION-001)

**Role :** Principal Software Architect & Principal HPC Architect  
**Date :** 3 août 2026  
**Dépôt :** Atmospheric Complexity Framework (ACF)  

---

## 1. Graphe de Dépendances ASCII Complet

```
================================================================================
                    ACF INGESTION SYSTEM DEPENDENCY GRAPH
================================================================================

[INPUT FILES]
  │  ├── *.fa (AROME / ALADIN / ARPEGE FA Format)
  │  ├── *.lfa (AROME / ALADIN LFA Inline Format)
  │  ├── *.grib / *.grib2 (GRIB Datasets)
  │  └── *.nc (NetCDF CF Datasets)
  │
  ▼
[FORMAT DETECTION LAYER]
  │  ├── FormatDetector (src/acf/data/detector.py)
  │  └── CFDetector (src/acf/importers/readers/cf_detector.py)
  │
  ▼
[EPYGRAM & NATIVE DATA READERS]
  │  ├── EPyGrAMReader (src/acf/data/readers/epygram_reader.py)
  │  │     └── epygram (Météo-France EPyGrAM C/Fortran Backend)
  │  ├── GRIBReader (src/acf/importers/readers/grib_reader.py)
  │  │     ├── xarray
  │  │     └── cfgrib / eccodes
  │  ├── NetCDFReader (src/acf/importers/readers/netcdf_reader.py)
  │  │     ├── xarray
  │  │     └── netCDF4
  │  └── BufrReader (src/acf/importers/readers/bufr_reader.py)
  │        └── eccodes
  │
  ▼
[UNIVERSAL INGESTION & DATA ENGINE LAYER]
  │  ├── UniversalDataIngestionEngine (src/acf/data/universal_ingestion.py)
  │  │     ├── ParameterEngine (src/acf/science/parameters/engine.py)
  │  │     └── KnowledgeGraphEngine (src/acf/science/encyclopedia/knowledge_graph/graph_engine.py)
  │  └── Dataset (src/acf/data/dataset.py)
  │
  ▼
[NWP MODEL INGESTION ADAPTERS]
  │  ├── ARPEGEIngestionAdapter (src/acf/models/arpege/ingestion_adapter.py)
  │  ├── AROMEIngestionAdapter (src/acf/models/arome/ingestion_adapter.py)
  │  └── ALADINIngestionAdapter (src/acf/models/aladin/ingestion_adapter.py)
  │
  ▼
[HPC WORKFLOW ENGINE & PIPELINES]
  │  ├── WorkflowEngine (src/acf/hpc_workflow/workflow_engine.py)
  │  │     ├── WorkflowFactory (src/acf/hpc_workflow/workflow_factory.py)
  │  │     └── WorkflowManager (src/acf/hpc_workflow/workflow_manager.py)
  │  ├── AROMEWorkflow (src/acf/hpc_workflow/arome/arome_workflow.py)
  │  └── ALADINWorkflow (src/acf/hpc_workflow/aladin/aladin_workflow.py)
  │
  ▼
[DOWNSTREAM CONSUMERS]
     ├── MapEngine / AWCI Canvas (src/acf/maps/ & src/acf/gui/map/)
     ├── Science & Analysis Engine (src/acf/science/ & src/acf/analysis/)
     ├── AI & Decision Support (src/acf/ai/ & src/acf/intelligence/)
     └── ESOC Workstation Interface (src/acf/gui/esoc/)

================================================================================
```

---

## 2. Diagramme de Dépendances de Modules (Couplage & Flux)

```
[FormatDetector] ──────► [EPyGrAMReader] ──────► [epygram (Lib)]
       │                      │
       ▼                      ▼
[UniversalDataIngestionEngine] ───────────────► [Dataset]
       │                                           │
       ▼                                           ▼
[NWP Model Adapters] ─────────────────────► [WorkflowEngine]
  (ARPEGE/AROME/ALADIN)                     (HPC Execution)
```
