# AUDIT D'ARCHITECTURE D'INGESTION & D'INTÉGRATION EPYGRAM — ACF (ACF-ARCH-INGESTION-001)

**Role :** Principal Software Architect / Principal HPC Architect / Principal Python Architect / Principal NWP Architect  
**Branche Git :** `develop`  
**Dépôt :** `/home/souhaib/ACF` (obtenu via `git rev-parse --show-toplevel`)  
**Date :** 3 août 2026  

---

## 1. Inventaire Complet & Responsabilités des Composants

### 1.1 Composants d'Ingestion & Lecteurs de Données (`src/acf/data/readers/`, `src/acf/importers/`)

| Fichier / Module | Classe / Enité | Responsabilité Principal | Dépendances | Utilisateurs / Appelants |
| :--- | :--- | :--- | :--- | :--- |
| `src/acf/data/readers/epygram_reader.py` | `EPyGrAMReader` | Backend d'ingestion officiel EPyGrAM pour la lecture native des formats Météo-France (FA, LFA), GRIB1/2 et NetCDF. | `epygram`, `numpy`, `pathlib`, `BaseReader` | `UniversalDataIngestionEngine`, Adaptateurs ARPEGE/AROME/ALADIN |
| `src/acf/data/detector.py` | `FormatDetector` | Détection automatique des formats scientifiques à partir de l'extension et des en-têtes binaire (`FA`, `LFA`, `GRIB1/2`, `NETCDF`, `BUFR`, etc.). | `pathlib` | `UniversalDataIngestionEngine`, `Dataset` |
| `src/acf/data/universal_ingestion.py` | `UniversalDataIngestionEngine` | Orchestrateur universel d'ingestion : sélection du lecteur, extraction des métadonnées spatio-temporelles, alignement CF/WMO et indexation dans le graphe de connaissances. | `FormatDetector`, `EPyGrAMReader`, `ParameterEngine`, `KnowledgeGraphEngine` | Pipelines de prévision NWP, Workflows HPC, Interface ESOC |
| `src/acf/data/dataset.py` | `Dataset` | Objet de données canonique ACF encapsulant variables, dimensions, attributs, métadonnées spatio-temporelles et statut de validation. | `datetime`, `uuid`, `pathlib` | Ensemble du framework ACF (MapEngine, IA, Solveurs, Analyse) |
| `src/acf/data/manager.py` | `DataManager` | Gestionnaire du cycle de vie des datasets locaux, indexation, recherche et mise en cache. | `Dataset`, `CacheManager`, `DataCatalogEngine` | Visualisation, GUI, Intelligence Engine |
| `src/acf/importers/base/base_reader.py` | `BaseReader` | Interface abstraite canonique de tous les lecteurs de données. | `abc.ABC` | `EPyGrAMReader`, `GRIBReader`, `NetCDFReader`, `BufrReader` |
| `src/acf/importers/readers/grib_reader.py` | `GRIBReader`, `GribReader` | Reader GRIB1/GRIB2 basé sur `xarray` et `cfgrib`. | `xarray`, `cfgrib`, `eccodes` | `UniversalDataIngestionEngine`, `GRIBAdapter` |
| `src/acf/importers/readers/netcdf_reader.py` | `NetCDFReader` | Reader NetCDF3/NetCDF4 basé sur `xarray` et `netCDF4`. | `xarray`, `netCDF4` | `UniversalDataIngestionEngine`, `NetCDFAdapter` |
| `src/acf/importers/readers/bufr_reader.py` | `BufrReader` | Reader binaire pour les observations d'assimilation BUFR. | `eccodes` | Modules d'assimilation de données |

---

### 1.2 Adaptateurs et Modèles NWP (`src/acf/models/`)

| Fichier / Module | Classe | Responsabilité | Modèle NWP Cible |
| :--- | :--- | :--- | :--- |
| `src/acf/models/arpege/ingestion_adapter.py` | `ARPEGEIngestionAdapter` | Conversion des sorties spectrales ARPEGE (FA) vers la grille canonique ACF (105 niveaux). | ARPEGE (Météo-France Global) |
| `src/acf/models/arome/ingestion_adapter.py` | `AROMEIngestionAdapter` | Ingestion des grilles AROME 1.3 km Lambert-93 (FA/LFA, 90 niveaux). | AROME (Météo-France Convectif) |
| `src/acf/models/aladin/ingestion_adapter.py` | `ALADINIngestionAdapter` | Ingestion du domaine régional ALADIN 7.5 km Lambert (FA, 70 niveaux). | ALADIN (Météo-France Régional) |
| `src/acf/models/implementations/arome.py` | `AROMEModel` | Driver d'exécution et de configuration du modèle AROME. | AROME Core |
| `src/acf/models/implementations/arpege.py` | `ARPEGEModel` | Driver d'exécution et de configuration du modèle ARPEGE. | ARPEGE Core |
| `src/acf/models/implementations/ifs.py` | `IFSModel` | Driver d'exécution pour ECMWF IFS. | ECMWF IFS |
| `src/acf/models/implementations/wrf.py` | `WRFModel` | Driver d'exécution pour NCAR WRF. | NCAR WRF |
| `src/acf/models/implementations/icon.py` | `ICONModel` | Driver d'exécution pour DWD ICON. | DWD ICON |

---

## 2. Détection des Duplications & Couches Legacy

1. **Lecteurs & Bridge Compatibility (`src/acf/importers/readers/__init__.py` & `src/acf/data/readers/__init__.py`)** :  
   `src/acf/data/readers/__init__.py` et `src/acf/importers/readers/__init__.py` ré-exportent les mêmes classes pour des raisons de rétrocompatibilité.  
   - *Canonique* : `src/acf/data/readers/epygram_reader.py`  
   - *Forwarder / Alias* : `src/acf/importers/readers/__init__.py`

2. **Interface de Base Historique (`src/acf/io/base_reader.py`)** :  
   Le package `src/acf/io/` contient des wrappers legacy (`IOManager`, `IORegistry`, `IOFactory`).  
   - *Canonique* : `src/acf/data/`  
   - *Legacy* : `src/acf/io/`

3. **Adaptateurs d'Intégration (`src/acf/data/integration/`)** :  
   `src/acf/data/integration/` fournit un `AdapterFactory` et des adaptateurs (`GRIBAdapter`, `NetCDFAdapter`, `BUFRAdapter`). Ils fonctionnent comme des wrappers au-dessus des readers bruts pour harmoniser l'API `Dataset`.

---

## 3. Architecture Cible & Flux d'Ingestion EPyGrAM

```
Fichier Météorologique (*.fa, *.lfa, *.grib, *.nc)
                       │
                       ▼
       ┌──────────────────────────────┐
       │        FormatDetector        │
       └──────────────┬───────────────┘
                      │ (Détecte FA / LFA)
                      ▼
       ┌──────────────────────────────┐
       │        EPyGrAMReader         │
       └──────────────┬───────────────┘
                      │ (Extrait grille, métadonnées & champs)
                      ▼
       ┌──────────────────────────────┐
       │ UniversalDataIngestionEngine │
       └──────────────┬───────────────┘
                      │ (Cartographie variables & graphe de connaissances)
                      ▼
       ┌──────────────────────────────┐
       │        Dataset (ACF)         │
       └──────────────┬───────────────┘
                      │
       ┌──────────────┴───────────────┐
       ▼                              ▼
Adaptateurs Modèles NWP       Workflows HPC & Visualisation
(ARPEGE / AROME / ALADIN)     (MapEngine / AWCI / ESOC)
```

---

## 4. Recommandations d'Architecture

1. **Centralisation dans `src/acf/data/readers/`** : Maintenir l'unique implémentation `EPyGrAMReader` dans `src/acf/data/readers/epygram_reader.py`.
2. **Isolation des Solveurs et des IHM** : Interdire tout import direct de la bibliothèque `epygram` dans `src/acf/gui/` et `src/acf/simulation_engine/`.
3. **Mise en Cache HPC** : Exploiter `CacheManager` pour éviter les ouvertures/lectures répétées des gros fichiers FA spectraux sur le réseau HPC NFS/Lustre.
