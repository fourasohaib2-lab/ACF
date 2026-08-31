# AUDIT D'ENVIRONNEMENT ET INFRASTRUCTURE HPC (ACF-HPC-005)

**Date :** 6 août 2026  
**Auteur :** Lead HPC Architect & Chief Systems Engineer  
**Workspace Root :** `/home/souhaib/ACF` (obtenu via `git rev-parse --show-toplevel`)  
**Branche Git :** `develop`  

---

## 1. Synthèse de l'Environnement de Calcul

L'analyse complète du système hôte confirme l'environnement de développement et d'exécution du projet Atmospheric Complexity Framework (ACF) :

| Métrique Système | Valeur Détectée |
| :--- | :--- |
| **Hôte (Hostname)** | `ONMDTW01116` |
| **Architecture CPU** | Intel 12th Gen Core i7-12700 (20 VCPUs, 12 Cores, 4.9 GHz Max) |
| **Mémoire RAM** | 7.4 GiB Total (1.3 GiB Disponible) |
| **Stockage NVMe** | `/dev/nvme0n1p2` (468 GB Total, 376 GB Disponible, 16% Utilisé) |
| **Exécutable Python** | `/home/souhaib/ACF/.venv/bin/python` (Python 3.12.3 GCC 13.3.0) |
| **Support MPI** | `/usr/bin/mpirun` (OpenMPI) |
| **Connectivité Slurm** | Grappe Fennec (ONM HPC `login2.fennec.meteo.dz`, partition `Researches`) |

---

## 2. Inventaire des Répertoires et Sous-Systèmes

- **`src/acf/data/`** : Ingestion universelle, `EPyGrAMReader`, `PreprocessingEngine`, `FormatDetector`.
- **`src/acf/models/`** : Driver `BaseWeatherModel`, adaptateurs ARPEGE, AROME, ALADIN, IFS, ERA5, GFS, ICON, WRF et moteur `ForecastConfig`.
- **`src/acf/hpc_connector/`** : Connecteurs SSH, `JobManager`, `HPCMonitor`, `HPCDashboard`, `UniversalModelRunner`, `HPCWorkflowManager`, `HPCResourceOptimizer`, `HPCOutputManager`.
- **`src/acf/gui/esoc/`** : Interface PySide6 `ESOCWindow`, `HPCDashboardPanel`, `HPCExecutionPanel`, `NWPForecastCenterPanel`.
- **`src/acf/verification/`** & **`src/acf/analysis/`** : Metrics `NWPVerificationMetrics` (RMSE, BIAS, MAE, ACC, ETS, CSI, POD, FAR) & `PostProcessingEngine`.
