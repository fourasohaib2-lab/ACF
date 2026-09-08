# RELEASE SPECIFICATION — ACF v0.7

**Milestone:** Earth System Scientific Platform & Universal Reader  
**Target Release Date:** Sprint 5  
**Maturity Goal:** Production for Universal Data Ingestion  

---

## 1. Objectives & Scope
- **API Goal**: `UniversalReader.open(...)` supporting GRIB1/2, FA, LFA, LFI, NetCDF, HDF5, BUFR, GeoTIFF, Shapefile, GeoPackage, CSV, JSON, Zarr, Parquet.
- **Verification Goal**: `NWPVerificationMetrics` (RMSE, BIAS, MAE, ACC, ETS, CSI, POD, FAR).
- **GUI Goal**: `NWPForecastCenterPanel` PySide6 operational tabbed center.
- **Exit Criteria**: `test_universal_reader.py`, `test_nwp_metrics.py`, and `test_module_manifest.py` 100% pass.
