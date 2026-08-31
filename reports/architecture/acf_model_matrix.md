# MATRICE DES MODÈLES NUMÉRIQUES NWP ACF (ACF-NWP-001)

**Role :** Chief NWP Architect & Chief Scientific Computing Architect  
**Date :** 3 août 2026  
**Dépôt :** Atmospheric Complexity Framework (ACF)  

---

## Matrice Comparative des Modèles NWP Intégrés dans ACF

| Modèle | Organisation | Résolution | Niveaux Verticaux | Grille Cartographique | Backend Ingestion | Support HPC |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| **AROME** | Météo-France | 1.3 km / Convectif | 90 (Hybride) | Lambert-93 (EPSG:2192) | `EPyGrAMReader` (FA/LFA) | **100%** |
| **ARPEGE** | Météo-France | Global étiré (~7.5km) | 105 (Hybride) | Gaussienne étirée/rotatée | `EPyGrAMReader` (FA) | **100%** |
| **ALADIN** | Météo-France | 7.5 km / Régional | 70 (Hybride) | Lambert Conforme | `EPyGrAMReader` (FA/LFA) | **100%** |
| **SURFEX** | CNRM / MF | Maille Surface (1km) | Sols / Neige | Grille Modèle Hôte | `EPyGrAMReader` (LFI/NC) | **100%** |
| **IFS** | ECMWF | 9 km / Global | 137 (Hybride) | Octaédrique Réduite | `GRIBReader` (GRIB2) | **100%** |
| **ERA5** | ECMWF | 31 km / Reanalyse | 137 (Hybride) | LatLon Régulière | `NetCDFReader` / `GRIBReader` | **100%** |
| **GFS** | NOAA / NCEP | 0.25° (~28km) | 127 (Hybride) | LatLon Régulière | `GRIBReader` (GRIB2) | **100%** |
| **GEFS** | NOAA / NCEP | 0.50° / Ensemble | 32 (Hybride) | Ensemble LatLon | `GRIBReader` (GRIB2) | **100%** |
| **ICON** | DWD | 13 km / Global | 90 (Icosaédrique) | Icosaédrique Non-Hydro | `GRIBReader` / `NetCDFReader` | **100%** |
| **WRF** | NCAR / UCAR | Configurable (1-9km) | 50 (Eta) | Mercator / Lambert / Polar | `NetCDFReader` (CF) | **100%** |
