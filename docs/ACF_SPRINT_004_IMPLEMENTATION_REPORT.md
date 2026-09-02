<!-- ACF_RECONCILIATION_BANNER_2026-09-02 -->
> **⚠️ Historical / unverified document.** This file was auto-generated as part
> of an earlier documentation sprint, and its completion, certification, or
> "100%"-style claims were not independently reproduced. For the actual,
> reproducible test/status numbers, see [`ROADMAP.md`](../ROADMAP.md) and
> [`README.md`](../README.md)'s "Verified Status" section; for what has
> genuinely been audited and fixed since, see
> [`ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md`](ACF_PHYSICS_GUARD_AUDIT_CHANGELOG.md).
> Treat any specific number, percentage, or "CERTIFIED"/"COMPLETE" claim below
> as aspirational unless it also appears in one of those documents.
>
> _Banner added 2026-09-02 per `ROADMAP.md`'s "reconcile ~150 certificate/
> sprint-report documents" near-term priority — original content preserved
> unchanged below._

---

# ACF SPRINT-004 IMPLEMENTATION REPORT (ACF-EXEC-004)

## 1. IMPLEMENTATION DETAILS

- **Target Files**:
  - `src/acf/models/forecast_config.py` (`ForecastConfig`)
  - `src/acf/data/preprocessing.py` (`PreprocessingEngine`)
  - `src/acf/analysis/postprocessing.py` (`PostProcessingEngine`)
- **APIs Provided**:
  - `ForecastConfig`: Managed dataclass for domain, resolution, nesting, forecast length, initial/boundary conditions, physics schemes, output frequency, and restart intervals.
  - `PreprocessingEngine`: Automated pre-processing and validation for GRIB, GRIB2, NetCDF, BUFR, HDF5, GeoTIFF, FA, LFI, SYNOP, TEMP, AMDAR, Satellite, and Radar.
  - `PostProcessingEngine`: Generation of 2D spatial maps, time series, vertical profiles, cross-sections, NetCDF4 CF & GeoTIFF exports, and JSON metadata.
