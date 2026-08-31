# ACF NWP PERFORMANCE REPORT (ACF-LTS-002)

| NWP Subsystem | Operation | Measured Duration | Benchmark Status |
| :--- | :--- | :---: | :---: |
| **Data Ingestion** | EPyGrAM 1.3km AROME FA format read | 0.85 s | **PASS** |
| **Preprocessing** | Format validation & observation matching | 10 ms | **PASS** |
| **Model Runner** | Batch script submission & setup | 15 ms | **PASS** |
| **Postprocessing** | GeoTIFF & CF-1.8 NetCDF4 export | 22 ms | **PASS** |
