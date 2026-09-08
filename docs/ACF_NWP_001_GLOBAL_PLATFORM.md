# ACF GLOBAL NUMERICAL WEATHER PREDICTION PLATFORM (ACF-NWP-001)

**Date :** 6 août 2026  
**Statut :** Spécification Globale & Manuel d'Ingénierie  
**Packages Cibles :** `acf.models`, `acf.data`, `acf.analysis`, `acf.verification`, `acf.gui.esoc`  

---

## 1. Vue d'Ensemble de l'Architecture NWP

La plateforme de prévision numérique du temps (NWP) globale d'ACF harmonise l'intégration, l'exécution, le post-traitement et la vérification statistique de l'ensemble des modèles météorologiques mondiaux et régionaux (**ARPEGE**, **AROME**, **ALADIN**, **WRF**, **ICON**, **OpenIFS**, **IFS**, **FV3**, **MPAS**, **GFS**, **ECMWF**).

```
[MÉTEO-FRANCE / ECMWF / NOAA / DWD / NCAR DATASETS]
  │ (GRIB, GRIB2, BUFR, NetCDF, HDF5, GeoTIFF, FA, LFI, SYNOP, TEMP, AMDAR, Satellite, Radar)
  ▼
[AUTOMATED PREPROCESSING ENGINE] (src/acf/data/preprocessing.py)
  │
  ▼
[UNIVERSAL BASE MODEL API & FORECAST CONFIG ENGINE] (src/acf/models/)
  │  ├── BaseWeatherModel (prepare, configure, run, restart, stop, resume, collect_outputs, verify)
  │  └── ForecastConfig (domain, resolution, nesting, forecast length, initial/boundary conditions)
  │
  ▼
[HPC EXECUTION ENGINE & SLURM SCHEDULER] (src/acf/hpc_connector/)
  │
  ▼
[POST-PROCESSING & PRODUCT GENERATION] (src/acf/analysis/postprocessing.py)
  │  ├── 2D Spatial Maps & GeoTIFF Export
  │  ├── Time Series & Vertical Profiles
  │  └── NetCDF4 CF Export & JSON Metadata
  │
  ▼
[NWP VERIFICATION SYSTEM] (src/acf/verification/nwp_metrics.py)
  │  ├── Continuous Metrics: RMSE, BIAS, MAE, ACC
  │  └── Categorical Metrics: POD, FAR, CSI, ETS
  │
  ▼
[ESOC NWP FORECAST CENTER COMMAND PANEL] (src/acf/gui/esoc/nwp_forecast_center_panel.py)
```

---

## 2. Description des Modules et APIs

### 2.1 `BaseWeatherModel` (`src/acf/models/base_model.py`)
- `prepare(config)` : Préparation des conditions aux limites et initiales.
- `configure(domain, resolution, forecast_hours)` : Configuration du domaine et de la durée.
- `run()` : Lancement du noyau dynamique.
- `restart(checkpoint_step)` : Reprise sur arrêt.
- `stop()` / `resume()` : Contrôle du cycle.
- `collect_outputs(target_dir)` : Extraction des produits bruts.
- `verify()` : Évaluation statistique automatique.

### 2.2 `ForecastConfig` (`src/acf/models/forecast_config.py`)
- Dataclass de configuration (domaine, résolution, emboîtemens, durée de prévision, schémas physiques, fréquence des sorties et intervalles de restart).

### 2.3 `PreprocessingEngine` (`src/acf/data/preprocessing.py`)
- Validation et pré-traitement automatique pour tous les conteneurs et types d'observations (SYNOP, TEMP, AMDAR, Satellites, Radars).

### 2.4 `PostProcessingEngine` (`src/acf/analysis/postprocessing.py`)
- Génération des cartes, coupes verticales, séries temporelles, métadonnées JSON, exports NetCDF/GeoTIFF.

### 2.5 `NWPVerificationMetrics` (`src/acf/verification/nwp_metrics.py`)
- Calculateur complet des métriques de vérification : **RMSE**, **BIAS**, **MAE**, **ACC**, **ETS**, **CSI**, **POD**, **FAR**.

---

## 3. Exemples d'Utilisation API

```python
from acf.models import ForecastConfig
from acf.data.preprocessing import PreprocessingEngine
from acf.analysis.postprocessing import PostProcessingEngine
from acf.verification.nwp_metrics import NWPVerificationMetrics

# 1. Configuration de la prévision
cfg = ForecastConfig(model_name="AROME", domain="Algeria", forecast_hours=48, hpc_nodes=4)
print(f"Configured {cfg.model_name} for {cfg.forecast_hours}h forecast.")

# 2. Validation du fichier d'entrée
preproc = PreprocessingEngine()
val = preproc.validate_file("ICMSHAROME+0000.fa")

# 3. Calcul des métriques de vérification (ex: T2M)
fcst_t2m = [288.5, 290.1, 293.4, 291.2]
obs_t2m = [288.1, 290.5, 293.0, 291.5]
metrics = NWPVerificationMetrics.evaluate_all(fcst_t2m, obs_t2m)
print(f"RMSE: {metrics['rmse']:.3f} K | BIAS: {metrics['bias']:.3f} K | ACC: {metrics['acc']:.3f}")
```
