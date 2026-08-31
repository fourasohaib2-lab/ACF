# AUDIT D'ARCHITECTURE PLATEFORME NWP GLOBALE (ACF-NWP-001)

**Date :** 4 août 2026  
**Auteur :** Chief NWP Architect & Lead Earth System Engineer  
**Workspace :** `/home/souhaib/ACF` (Branche `develop`)  

---

## 1. Synthèse de l'Audit Globale des Sous-Systèmes

### 1.1 `src/acf/models/`
- **État Actuel :** `BaseWeatherModel`, adaptateurs ARPEGE, AROME, ALADIN, IFS, ERA5, GFS, GEFS, ICON, WRF.
- **Besoins :** Extension du framework pour supporter FV3 et MPAS avec les méthodes unifiées (`prepare`, `configure`, `run`, `restart`, `stop`, `resume`, `collect_outputs`, `verify`).

### 1.2 `src/acf/data/` & Ingestion
- **État Actuel :** `UniversalDataIngestionEngine`, `EPyGrAMReader`, `GRIBReader`, `NetCDFReader`, `BufrReader`.
- **Besoins :** Moteur de pré-traitement automatisé (`preprocessing.py`) couvrant tous les types d'observations (SYNOP, TEMP, AMDAR, Satellites, Radars) et conteneurs (FA, LFI, GRIB1/2, NetCDF, HDF5, GeoTIFF).

### 1.3 `src/acf/analysis/` & `src/acf/verification/`
- **Besoins :** Moteur de post-traitement matriciel (`postprocessing.py`) et calcul automatisé des métriques d'évaluation météorologiques (RMSE, BIAS, MAE, ACC, ETS, CSI, POD, FAR).

### 1.4 `src/acf/gui/esoc/`
- **Besoins :** Intégration du panneau de contrôle centralifié **ESOC NWP Forecast Center** (`nwp_forecast_center_panel.py`).
