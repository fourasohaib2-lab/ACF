# GRAPHE DE DÉPENDANCES DE L'INGESTION DE DONNÉES ACF (ACF-DATA-001)

**Role :** Chief Data Architect & Chief Earth System Architect  
**Date :** 3 août 2026  
**Dépôt :** Atmospheric Complexity Framework (ACF)  

---

## 1. Graphe d'Architecture Globale (ASCII)

```
================================================================================
                    ACF UNIFIED DATA INGESTION GRAPH
================================================================================

[RAW DATA SOURCES]
  │  ├── NWP: FA, LFA, LFI, GRIB1, GRIB2, NetCDF4, Zarr
  │  ├── EO: GeoTIFF, COG, HDF5, CSV, JSON, GeoJSON, XML, Parquet, Arrow
  │  ├── Satellite: Sentinel NetCDF, MSG/MTG HDF5, GOES, Himawari
  │  └── Radar: ODIM H5, Rainbow, NEXRAD
  │
  ▼
[FORMAT DETECTION & DISPATCH LAYER]
  │  └── FormatDetector (src/acf/data/detector.py)
  │
  ▼
[CANONICAL READER API (BaseReader)]
  │  ├── EPyGrAMReader (src/acf/data/readers/epygram_reader.py)
  │  ├── GRIBReader (src/acf/importers/readers/grib_reader.py)
  │  ├── NetCDFReader (src/acf/importers/readers/netcdf_reader.py)
  │  ├── BufrReader (src/acf/importers/readers/bufr_reader.py)
  │  ├── GeoTIFFReader (src/acf/data/readers/geotiff_reader.py)
  │  ├── CSVReader (src/acf/data/readers/csv_reader.py)
  │  └── JSONReader (src/acf/data/readers/json_reader.py)
  │
  ▼
[UNIFIED INGESTION ENGINE]
  │  ├── UniversalDataIngestionEngine (src/acf/data/universal_ingestion.py)
  │  ├── ParameterEngine (src/acf/science/parameters/engine.py)
  │  └── KnowledgeGraphEngine (src/acf/science/encyclopedia/knowledge_graph/)
  │
  ▼
[CANONICAL ACF DATASET OBJECT]
  │  └── Dataset (src/acf/data/dataset.py)
  │
  ▼
[CONSUMERS & DOWNSTREAM EXPLOITATION]
     ├── NWP Model Adapters (ARPEGE / AROME / ALADIN / IFS / ICON / WRF)
     ├── HPC Workflows (WorkflowEngine / WorkflowManager)
     ├── Science & Physics Solvers (CoupledSolver / AtmosphericDynamics)
     ├── AI & Decision Support (AIForecastCenter / CausalReasoning)
     └── ESOC GUI & MapEngine Canvas (awci_renderer / LayerEngine)

================================================================================
```
