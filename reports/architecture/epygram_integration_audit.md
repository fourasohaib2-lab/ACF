# AUDIT DE L'ARCHITECTURE DE L'INTÉGRATION EPYGRAM (ACF-ARCH-EPYGRAM-001)

**Role :** Principal Software Architect & Principal HPC Architect  
**Statut :** Analyse d'Architecture Pure (Aucune modification de code de production)  
**Date :** 3 août 2026  
**Dépôt Cible :** Atmospheric Complexity Framework (ACF)  

---

## 1. Inventaire Exhaustif des Composants Données & NWP

### 1.1 Readers (Lecteurs de Données)
- **`src/acf/data/readers/epygram_reader.py`**
  - **Classe / Module** : `EPyGrAMReader` (et fonctions du module `open`, `close`, `metadata`, `geometry`, `list_fields`, `read_field`, `read_fields`, `vertical_levels`, `projection`, `time_validity`, `domain`).
  - **Responsabilité** : Backend d'ingestion EPyGrAM pour la lecture native des formats Météo-France FA et LFA, ainsi que GRIB et NetCDF.
  - **Dépendances** : `epygram`, `numpy`, `pathlib`, `acf.importers.base.base_reader.BaseReader`.
  - **Utilisateurs** : `UniversalDataIngestionEngine`, adaptateurs de modèles ARPEGE, AROME, ALADIN.

- **`src/acf/importers/readers/grib_reader.py`** (et `src/acf/data/readers/grib_reader.py`)
  - **Classe** : `GRIBReader`, `GribReader`.
  - **Responsabilité** : Lecture et conversion des fichiers GRIB1/GRIB2 via `xarray` et `cfgrib`.
  - **Dépendances** : `xarray`, `cfgrib`, `eccodes`.
  - **Utilisateurs** : `UniversalDataIngestionEngine`, `GRIBAdapter`.

- **`src/acf/importers/readers/netcdf_reader.py`** (et `src/acf/data/readers/netcdf_reader.py`)
  - **Classe** : `NetCDFReader`.
  - **Responsabilité** : Ingestion des datasets NetCDF3/NetCDF4 conformes aux conventions CF.
  - **Dépendances** : `xarray`, `netCDF4`.
  - **Utilisateurs** : `UniversalDataIngestionEngine`, `NetCDFAdapter`.

- **`src/acf/importers/readers/bufr_reader.py`**
  - **Classe** : `BufrReader`.
  - **Responsabilité** : Lecture des données d'observation au format binaire WMO BUFR.
  - **Dépendances** : `eccodes`.
  - **Utilisateurs** : Module d'ingestion d'observations (`data_assimilation`).

- **`src/acf/data/readers/geotiff_reader.py` / `csv_reader.py` / `json_reader.py`**
  - **Classes** : `GeoTIFFReader`, `CSVReader`, `JSONReader`.
  - **Responsabilité** : Ingestion des données matricielles géospatiales et des formats tabulaires/structurés.

---

### 1.2 Classes Dataset
- **`src/acf/data/dataset.py`**
  - **Classe** : `Dataset`.
  - **Responsabilité** : Représentation interne canonique d'un jeu de données météorologiques (variables, dimensions, attributs, métadonnées spatiales/temporelles, statut de validation).
  - **Dépendances** : `datetime`, `uuid`, `pathlib`.
  - **Utilisateurs** : Ensemble des composants ACF (`UniversalDataIngestionEngine`, `DataManager`, `MapEngine`, modules IA & Analyse).

- **`src/acf/data/engine/dataset_metadata.py`**
  - **Classe** : `DatasetMetadata`.
  - **Responsabilité** : Conteneur structuré des métadonnées de grille et du repère spatio-temporel.

- **`src/acf/data/engine/dataset_statistics.py`**
  - **Classe** : `DatasetStatistics`.
  - **Responsabilité** : Calcul et stockage des métriques statistiques (min, max, moyenne, variance).

---

### 1.3 Classes DataManager
- **`src/acf/data/manager.py`**
  - **Classe** : `DataManager`.
  - **Responsabilité** : Gestion du cycle de vie des jeux de données locaux, mise en cache, requêtes et recherche.
  - **Dépendances** : `Dataset`, `CacheManager`, `DataCatalogEngine`.

- **`src/acf/hpc_connector/data_management/data_manager.py`**
  - **Classe** : `HPCDataManager`.
  - **Responsabilité** : Gestion des transferts de fichiers volumineux, mise en cache et staging sur grappes HPC.

---

### 1.4 UniversalDataIngestionEngine
- **`src/acf/data/universal_ingestion.py`**
  - **Classe** : `UniversalDataIngestionEngine`.
  - **Responsabilité** : Moteur universel d'ingestion d'observations et de prévisions. Analyse le format via `FormatDetector`, aiguille vers le reader approprié (`EPyGrAMReader`, `GRIBReader`, `NetCDFReader`), mappe les variables physiques (`ParameterEngine`) et relie le dataset au graphe de connaissances (`KnowledgeGraphEngine`).

---

### 1.5 FormatDetector
- **`src/acf/data/detector.py`**
  - **Classe** : `FormatDetector`.
  - **Responsabilité** : Détection automatique des formats de fichiers à partir des extensions (`.fa`, `.lfa`, `.grib`, `.grib2`, `.nc`, `.bufr`, etc.) et des signatures d'en-tête.

---

### 1.6 Importeurs
- **`src/acf/importers/base/base_importer.py`** : Interface d'importation de base.
- **`src/acf/importers/cf/`** : Importer de métadonnées de la convention CF.
- **`src/acf/importers/ecmwf/`** : Importer pour les jeux de données ECMWF (IFS/ERA5).
- **`src/acf/importers/wmo/`** : Importer pour les standards WMO.

---

### 1.7 Utilisations des Bibliothèques Tierces

| Bibliothèque | Fichiers Repérés | Rôle dans ACF |
| :--- | :--- | :--- |
| **`xarray`** | `src/acf/importers/readers/grib_reader.py`<br>`src/acf/importers/readers/netcdf_reader.py`<br>`src/acf/simulation_engine/output/netcdf_writer.py`<br>`src/acf/simulation_engine/output/zarr_writer.py`<br>`src/acf/gui/map/renderers/awci_renderer.py` | Manipulation de grilles multidimensionnelles n-D et E/S de fichiers NetCDF/Zarr. |
| **`cfgrib`** | `src/acf/importers/readers/grib_reader.py` | Moteur d'ouverture des fichiers GRIB via `xarray.open_dataset(..., engine='cfgrib')`. |
| **`netCDF4`** | `src/acf/data/integration/netcdf_adapter.py`<br>`src/acf/simulation_engine/output/netcdf_writer.py` | Écriture binaire et lecture directe des fichiers NetCDF4. |
| **`eccodes`** | `src/acf/hpc_connector/environment_manager.py`<br>`src/acf/hpc_connector/arome_aladin_detector.py`<br>`src/acf/release/dependency_validator.py` | Décodage bas niveau C/Fortran des messages GRIB1, GRIB2 et BUFR sur HPC. |
| **`epygram`** | `src/acf/data/readers/epygram_reader.py` | Décodage binaire natif Météo-France des fichiers FA et LFA (ARPEGE, AROME, ALADIN). |

---

### 1.8 Pilotes de Modèles Météo (NWP)

- **AROME** :  
  - Fichiers : `src/acf/models/arome/ingestion_adapter.py`, `src/acf/models/implementations/arome.py`, `src/acf/hpc_workflow/arome/arome_workflow.py`.  
  - Spécificités : Modèle non-hydrostatique à 1.3 km sur grille Lambert-93, 90 niveaux hybrides.
- **ARPEGE** :  
  - Fichiers : `src/acf/models/arpege/ingestion_adapter.py`, `src/acf/models/implementations/arpege.py`.  
  - Spécificités : Modèle spectral global à grille gaussienne étirée/rotatée, 105 niveaux.
- **ALADIN** :  
  - Fichiers : `src/acf/models/aladin/ingestion_adapter.py`, `src/acf/models/implementations/aladin.py`, `src/acf/hpc_workflow/aladin/aladin_workflow.py`.  
  - Spécificités : Modèle régional à 7.5 km sur domaine Lambert conforme, 70 niveaux.
- **ICON** : `src/acf/models/implementations/icon.py` (DWD, grille icosaédrique).
- **IFS / ERA5** : `src/acf/models/implementations/ifs.py`, `era5.py` (ECMWF).
- **WRF** : `src/acf/models/implementations/wrf.py` (NCAR, grille Mercator/Lambert).

---

### 1.9 Tests Concernés
- `tests/test_epygram_reader.py` : Tests unitaires et d'intégration d'EPyGrAM (8 tests).
- `tests/test_universal_data_ingestion.py` : Tests d'ingestion universelle.
- `tests/test_grib_reader.py` & `tests/test_netcdf_reader.py` : Tests des lecteurs GRIB et NetCDF.
- `tests/test_workflow_engine.py` : Tests d'orchestration HPC (8 tests).

---

## 2. Recommandations d'Architecture & Plan de Migration

### 2.1 Emplacement et Intégration
- **Backend Unique** : `src/acf/data/readers/epygram_reader.py` doit demeurer le backend officiel unique.
- **Adaptateurs Modèles** : Les adaptateurs d'ingestion spécifiques dans `src/acf/models/arpege/`, `arome/`, `aladin/` convertissent les structures brutes d'EPyGrAM vers les représentations `Dataset` internes d'ACF.

### 2.2 Modules Inviolables (Ne surtout pas toucher)
- `src/acf/gui/` : L'interface graphique ESOC et le canvas de carte ne doivent pas dépendre directement de la bibliothèque `epygram`.
- `src/acf/simulation_engine/` : Le moteur de résolution physique reste indépendant des lecteurs de formats d'entrée.
- `src/acf/science/laws/` : Les lois physiques théoriques demeurent totalement découplées.

### 2.3 Impacts & Performance
- **API Publique** : Aucun changement d'API publique n'est requis ; `UniversalDataIngestionEngine` garantit l'isolation.
- **Performance HPC** : EPyGrAM s'appuie sur la bibliothèque Fortran Météo-France (`falfilfa4py`), offrant des débits d'ingestion très élevés sur grappes HPC parallelisées.
