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

# ACF v0.6 RELEASE NOTES

**Release Version:** v0.6.0  
**Release Date:** August 6, 2026  

---

## 🚀 Key Highlights & New Capabilities

1. **Forecast Configuration Engine (`ForecastConfig`)**:
   - Structured configuration dataclass for model domains, spatial resolutions, nesting ratios, output intervals, and physics schemes.
2. **Automated Preprocessing Engine (`PreprocessingEngine`)**:
   - Multi-format ingestion & validation pipeline for GRIB, GRIB2, NetCDF, BUFR, HDF5, GeoTIFF, FA, LFI, SYNOP, TEMP, AMDAR, Satellite, and Radar.
3. **Advanced Postprocessing Engine (`PostProcessingEngine`)**:
   - Generation of 2D spatial maps, vertical sounding profiles, lat/lon time series, cross-sections, CF-1.8 NetCDF4 exports, GeoTIFFs, and JSON metadata.
4. **Scientific Validation Framework (ACF-VAL-001)**:
   - Automated continuous metrics (RMSE, MAE, BIAS, ACC) and categorical event scores (ETS, CSI, POD, FAR).
