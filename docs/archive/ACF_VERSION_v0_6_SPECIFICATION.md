# RELEASE SPECIFICATION — ACF v0.6

**Milestone:** Global NWP Forecast Platform & Pre/Post Processing  
**Target Release Date:** Sprint 4  
**Maturity Goal:** Production for Pre/Post Processing  

---

## 1. Objectives & Scope
- **Configuration Goal**: `ForecastConfig` dataclass supporting domain, resolution, nesting, forecast length, initial/boundary conditions.
- **Processing Goal**: `PreprocessingEngine` & `PostProcessingEngine` (maps, profiles, time series, NetCDF/GeoTIFF exports).
- **Exit Criteria**: `test_forecast_config.py`, `test_preprocessing.py`, and `test_postprocessing.py` 100% pass.
