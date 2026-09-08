# UNIFIED HPC EXECUTION ENGINE FOR NWP (ACF-HPC-004)

**Date :** 4 août 2026  
**Statut :** Spécification Technique & Guide Développeur  
**Packages Cibles :** `acf.hpc_connector`, `acf.gui.esoc`  

---

## 1. Vue d'Ensemble d'Architecture

Le sous-système d'exécution HPC unifié d'ACF permet d'exécuter, d'optimiser, d'orchestrer et de surveiller en temps réel l'ensemble des modèles numériques de prévision météorologique (ARPEGE, AROME, ALADIN, WRF, ICON, OpenIFS, IFS) directement depuis l'interface ESOC ou via l'API Python.

```
                      ESOC GUI Execution Control Center
                    (src/acf/gui/esoc/hpc_execution_panel.py)
                                       │
                                       ▼
                       HPC Workflow Manager (DAG Runner)
                    (src/acf/hpc_connector/workflow_manager.py)
                                       │
                                       ▼
                     Universal Model Runner Execution Engine
                     (src/acf/hpc_connector/model_runner.py)
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
  HPCResourceOptimizer             JobManager             HPCOutputManager
(Estimation & Scripting)        (Slurm sbatch/squeue)    (Outputs & Metadata)
```

---

## 2. Description des Modules et APIs

### 2.1 `UniversalModelRunner` (`src/acf/hpc_connector/model_runner.py`)
- `prepare_case(model_name, config)` : Préparation du cas de test.
- `submit(model_name, config)` : Soumission Slurm du job.
- `monitor(job_id)` : Métriques d'exécution live.
- `cancel(job_id)` : Annulation du job.
- `restart(job_id, checkpoint_step)` : Reprise sur checkpoint.
- `collect_outputs(job_id, target_dir)` : Rapatriement des sorties.
- `archive(job_id, archive_dir)` : Archivage définitif.

### 2.2 `HPCWorkflowManager` (`src/acf/hpc_connector/workflow_manager.py`)
- Moteur DAG gérant les 6 étapes : `PRE_PROCESSING`, `INITIALIZATION`, `FORECAST`, `POST_PROCESSING`, `VERIFICATION`, `ARCHIVING`.

### 2.3 `HPCResourceOptimizer` (`src/acf/hpc_connector/resource_optimizer.py`)
- Estimation automatique des nœuds, CPUs, mémoire, walltime et génération de scripts Slurm optimisés.

### 2.4 `HPCOutputManager` (`src/acf/hpc_connector/output_manager.py`)
- Gestion hiérarchique des répertoires `outputs/`, `logs/`, `checkpoints/`, `restart/`, `forecasts/` et génération de métadonnées JSON.

---

## 3. Exemples de Code Python

```python
from acf.hpc_connector import UniversalModelRunner, HPCWorkflowManager, HPCResourceOptimizer

# 1. Optimisation et génération de script Slurm
slurm_script = HPCResourceOptimizer.generate_slurm_script("AROME", {"grid_points": 1500000, "forecast_hours": 36})

# 2. Exécution d'un modèle NWP
runner = UniversalModelRunner()
run_info = runner.run_model("AROME", {"nodes": 4, "cpus_per_node": 32})
print(f"Submitted Job ID: {run_info['job_id']}")

# 3. Lancement d'un workflow complet DAG
wm = HPCWorkflowManager(runner)
wf = wm.create_workflow("AROME_Daily_00Z", "AROME", {"nodes": 4})
wm.execute_workflow(wf["workflow_id"])
```
