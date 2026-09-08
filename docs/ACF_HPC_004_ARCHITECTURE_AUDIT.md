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

# AUDIT D'ARCHITECTURE HPC EXECUTION ENGINE (ACF-HPC-004)

**Date :** 4 août 2026  
**Auteur :** Lead HPC Architect & Chief NWP Engineer  
**Workspace :** `/home/souhaib/ACF` (Branche `develop`)  

---

## 1. Synthèse de l'Audit des Sous-Systèmes

### 1.1 `src/acf/hpc_connector/`
- **Composants Prétendants :** `ConnectionManager`, `SSHConnector`, `SlurmScheduler`, `JobManager`, `QueueManager`, `HPCMonitor`, `HPCDashboard`.
- **Besoins Constatés :** Manque d'une API unifiée d'exécution des modèles numériques (ARPEGE, AROME, ALADIN, WRF, ICON, IFS) et d'un optimiseur de ressources Slurm automatique.

### 1.2 `src/acf/models/`
- **Adaptateurs Modèles :** `ARPEGEIngestionAdapter`, `AROMEIngestionAdapter`, `ALADINIngestionAdapter`, `IFSModel`, `ERA5Model`, `GFSModel`, `ICONModel`, `WRFModel`.
- **Besoins Constatés :** Harmonisation de la préparation des cas de test (`prepare_case`), de la soumission Slurm dédiée et de la collecte des sorties (`collect_outputs`).

### 1.3 `src/acf/data/`
- **Moteur d'Ingestion :** `UniversalDataIngestionEngine` & `EPyGrAMReader`.
- **Besoins Constatés :** Organisation automatique des dossiers de sortie (`outputs/`, `logs/`, `checkpoints/`, `restart/`, `forecasts/`) et génération de résumés JSON.

### 1.4 `src/acf/gui/esoc/`
- **Panneaux ESOC :** `HPCTerminalPanel`, `HPCDashboardPanel`, `PanelManager`.
- **Besoins Constatés :** Intégration d'un panneau d'exécution et de contrôle des prévisions (`hpc_execution_panel.py`) avec actions Start, Pause, Resume, Cancel, Restart.

---

## 2. Plan d'Action d'Ingénierie (ACF-HPC-004)

1. **`model_runner.py`** : Exécuteur universel de modèles NWP.
2. **`workflow_manager.py`** : Gestionnaire de workflows avec graphes de dépendance et reprise après panne.
3. **`resource_optimizer.py`** : Estimateur automatique de nœuds/CPUs/RAM/walltime et générateur de scripts Slurm.
4. **`output_manager.py`** : Structuration hiérarchique et métadonnées JSON des sorties.
5. **`hpc_execution_panel.py`** : Panneau GUI ESOC d'exécution et de contrôle temps-réel.
6. **Suites de Tests & Documentation** : 100% de validation `compileall` et `pytest`.
