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

# ACF v1.0 RELEASE NOTES — GESOP

**Release Version:** v1.0.0 (Global Earth System Operations Platform)  
**Release Date:** August 6, 2026  

---

## 🌟 Key Highlights & Capabilities of ACF v1.0.0

1. **Global Earth System Operating Platform (GESOP)**:
   - Unified scientific platform covering Atmosphere, Ocean, Hydrology, Cryosphere, Air Quality, Carbon Cycle, Wildfires, and Dust Aerosols.
2. **Universal Data Engine & Readers**:
   - `EPyGrAMReader` and `UniversalReader` supporting 15+ formats (GRIB1/2, NetCDF, HDF5, BUFR, GeoTIFF, FA, LFA, LFI, Zarr, Parquet, Shapefile).
3. **Data Assimilation Engine (`DataAssimilationEngine`)**:
   - Radar (Doppler wind, reflectivity) and satellite (radiances, brightness temp) assimilation via 3D-Var, 4D-Var, and EnKF.
4. **Universal NWP Model Execution (`UniversalModelRunner` & `HPCWorkflowManager`)**:
   - Unified submission and 6-stage DAG workflow management for ARPEGE, AROME, ALADIN, WRF, ICON, OpenIFS, and IFS on Slurm clusters.
5. **AI Hybrid NWP Framework (`FourierNeuralOperator`, `PINNEngine`, `AIBiasCorrector`)**:
   - FNO spectral acceleration, PINN physics conservation constraints, and neural model bias correction.
6. **ESOC Operations Center GUI**:
   - Live PySide6 operational panels (`HPCDashboardPanel`, `HPCExecutionPanel`, `NWPForecastCenterPanel`).
