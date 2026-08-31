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
