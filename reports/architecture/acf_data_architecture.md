# ARCHITECTURE UNIFIÉE D'INGESTION DE DONNÉES ACF (ACF-DATA-001)

**Signataires :**
- Chief Software Architect
- Chief HPC Architect
- Chief Earth System Architect
- Chief Data Architect
- Chief NWP Architect
- Principal Python Architect

**Date :** 3 août 2026  
**Workspace :** `/home/souhaib/ACF` (obtenu via `git rev-parse --show-toplevel`)  
**Branche Git :** `develop`  

---

## 1. Vue d'Ensemble & Stratégie d'Ingestion Unifiée

L'architecture d'ingestion de données de l'Atmospheric Complexity Framework (ACF) repose sur un modèle canonique unifié permettant de traiter indifféremment des données **Météorologiques**, d'**Observation de la Terre**, **Satellitaires** et **Radar**.

Tous les lecteurs spécialisés s'appuient sur l'interface canonique `BaseReader` (`src/acf/importers/base/base_reader.py`) et sont orchestrés de manière transparente par `UniversalDataIngestionEngine` (`src/acf/data/universal_ingestion.py`) pour produire exclusivement des objets uniques `acf.data.Dataset`.

```
Formats d'Entrée Multi-Domaines (FA, GRIB2, BUFR, NetCDF4, GeoTIFF, Zarr, ODIM H5...)
                                     │
                                     ▼
                     FormatDetector (src/acf/data/detector.py)
                                     │
                                     ▼
                API Canonique BaseReader & Lecteurs Dediés
                                     │
                                     ▼
         UniversalDataIngestionEngine + ParameterEngine + KnowledgeGraph
                                     │
                                     ▼
                       Objet Canonique Dataset (ACF)
                                     │
     ┌───────────────────┬───────────┴───────────┬───────────────────┐
     ▼                   ▼                       ▼                   ▼
Adaptateurs NWP     Moteur IA &      Solveurs & Moteur       Visualisation ESOC
 (ARPEGE/AROME)    Décisionnel      Physique Terre System      & MapEngine Canvas
```

---

## 2. Périphérie des Formats Pris en Charge

### 2.1 Météorologie & NWP
- **Météo-France FA / LFA / LFI** : Ingestion native via `EPyGrAMReader` (ARPEGE, AROME, ALADIN).
- **WMO GRIB1 / GRIB2** : Ingestion via `GRIBReader` (`xarray` + `cfgrib` + `eccodes`).
- **WMO BUFR** : Ingestion d'observations d'assimilation via `BufrReader` (`eccodes`).
- **NetCDF3 / NetCDF4 / HDF5 / Zarr** : Ingestion matricielle et multidimensionnelle CF-compliant via `NetCDFReader` et `ZarrWriter`.

### 2.2 Observation de la Terre (EO)
- **GeoTIFF / COG** : Ingestion de rasters géospatiaux et d'altimétrie via `GeoTIFFReader` et `GeoTIFFAdapter`.
- **HDF / HDF-EOS / CSV / JSON / GeoJSON / XML / Parquet / Arrow** : Ingestion tabulaire et vectorielle via la suite d'adaptateurs (`csv_adapter.py`, `json_adapter.py`, `xml_adapter.py`, `hdf5_adapter.py`).

### 2.3 Données Satellitaires & Radars Météo
- **Satellites (Sentinel, MSG, MTG, GOES, Himawari)** : Traités via `NetCDFReader` et `GeoTIFFAdapter`.
- **Radars (ODIM H5, Rainbow, NEXRAD)** : Traités via `HDF5Adapter` et `NetCDFReader`.

---

## 3. Composants Structurants de la Couche Données

1. **`FormatDetector` (`src/acf/data/detector.py`)** : Détection automatique universelle du format scientifique à partir de l'extension et des en-têtes binaires.
2. **`EPyGrAMReader` (`src/acf/data/readers/epygram_reader.py`)** : Lecteur officiel Météo-France (FA, LFA, LFI, GRIB, NetCDF).
3. **`UniversalDataIngestionEngine` (`src/acf/data/universal_ingestion.py`)** : Moteur d'extraction spatio-temporelle, d'alignement physique (`ParameterEngine`) et d'indexation dans le Graphe de Connaissances.
4. **`Dataset` (`src/acf/data/dataset.py`)** : Structure de données unique encapsulant variables, dimensions, coordonnées, attributs et statut de validation QC.
