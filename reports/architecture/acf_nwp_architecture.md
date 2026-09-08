# ARCHITECTURE UNIFIÉE DES MODÈLES NUMÉRIQUES NWP ACF (ACF-NWP-001)

**Signataires :**
- Chief NWP Architect
- Chief Software Architect
- Chief HPC Architect
- Chief Scientific Computing Architect
- Chief Earth System Architect

**Date :** 3 août 2026  
**Workspace :** `/home/souhaib/ACF` (obtenu via `git rev-parse --show-toplevel`)  
**Branche Git :** `develop`  

---

## 1. Vue d'Ensemble de l'Architecture NWP Unifiée

L'architecture unifiée de prévision numérique du temps (NWP) de l'Atmospheric Complexity Framework (ACF) harmonise l'accès et le pilotage de l'ensemble des systèmes de prévision météorologique mondiaux et régionaux au travers d'une interface commune `BaseWeatherModel` (`src/acf/models/base_model.py`).

Tous les modèles — qu'ils proviennent de Météo-France (**AROME**, **ARPEGE**, **ALADIN**, **SURFEX**), de l'ECMWF (**IFS**, **OpenIFS**, **ERA5**), de la NOAA (**GFS**, **GEFS**), du DWD (**ICON**) ou du NCAR (**WRF**) — partagent un contrat d'exécution identique et s'interfacent de manière transparente avec `UniversalDataIngestionEngine`, le `WorkflowEngine` HPC et la plateforme d'intelligence artificielle.

```
                         Atmospheric Complexity Framework (ACF)
                                           │
                                           ▼
                       Interface Canonique BaseWeatherModel
                                           │
           ┌───────────────────────────────┼───────────────────────────────┐
           ▼                               ▼                               ▼
   Météo-France NWP                  ECMWF & NOAA                   DWD & NCAR
(AROME/ARPEGE/ALADIN/SURFEX)       (IFS/ERA5/GFS/GEFS)              (ICON/WRF)
           │                               │                               │
           └───────────────────────────────┼───────────────────────────────┘
                                           ▼
                     Universal Ingestion & Dataset ACF
                                           │
                     ┌─────────────────────┴─────────────────────┐
                     ▼                                           ▼
            WorkflowEngine (HPC)                       Visualization & AI
```

---

## 2. Périphérie des Modèles Pris en Charge

| Modèle NWP | Organisation / Origine | Domaine / Résolution | Adaptateur & Driver ACF | Format Données Entrée/Sortie |
| :--- | :--- | :--- | :--- | :--- |
| **AROME** | Météo-France | Convectif 1.3 km / Lambert-93 | `AROMEIngestionAdapter` / `AROMEModel` | FA / LFA / GRIB2 |
| **ARPEGE** | Météo-France | Global Gaussien étiré / 105 lev | `ARPEGEIngestionAdapter` / `ARPEGEModel` | FA / GRIB2 |
| **ALADIN** | Météo-France | Régional 7.5 km / Lambert | `ALADINIngestionAdapter` / `ALADINModel` | FA / LFA |
| **SURFEX** | Météo-France / CNRM | Modèle de Surface (ISBA/TEB) | `SURFEXEngine` / `SURFEXModel` | LFI / NetCDF |
| **IFS / OpenIFS** | ECMWF | Global / TCo1279 9km | `IFSModel` | GRIB2 / NetCDF |
| **ERA5** | ECMWF | Reanalyse globale 31km | `ERA5Model` | NetCDF4 / GRIB |
| **GFS / GEFS** | NOAA | Global / Ensemble 0.25° | `GFSModel` / `GEFSModel` | GRIB2 |
| **ICON** | DWD | Global Icosaédrique 13km | `ICONModel` | GRIB2 / NetCDF |
| **WRF** | NCAR | Régional Méso-échelle | `WRFModel` | NetCDF4 CF |
