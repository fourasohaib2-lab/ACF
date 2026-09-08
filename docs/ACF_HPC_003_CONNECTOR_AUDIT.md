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

# AUDIT D'ARCHITECTURE HPC CONNECTOR (ACF-HPC-003)

**Date :** 3 août 2026  
**Auteur :** Lead HPC Integration Architect  
**Package Audité :** `src/acf/hpc_connector/`  

---

## 1. Inventaire et Cohérence des Classes

L'analyse du sous-système `src/acf/hpc_connector/` confirme une structure modulaire bien organisée pour la connectivité et la gestion de calculs sur grappe HPC Fennec / Slurm :

- **`HPCConnectionManager`** (`connection_manager.py`) : Gestion des accès SSH, résilience des sessions, staging.
- **`SSHConnector`** (`ssh_connector.py`) : Connecteur SSH bas-niveau (Paramiko / subprocess fallback).
- **`RemoteExecutor` & `RemoteTerminalShell`** (`remote_executor.py`, `remote_terminal.py`) : Exécution distante de scripts.
- **`SlurmScheduler`, `PBSScheduler`, `LocalScheduler`** (`scheduler_interface.py`) : Drivers d'ordonnancement.
- **`JobManager` & `QueueManager`** (`job_manager.py`, `queue_manager.py`) : Soumission sbatch et suivi squeue.
- **`ClusterDetector` & `AromeAladinDetector`** (`cluster_detector.py`, `arome_aladin_detector.py`) : Détection d'environnement Slurm et logiciels météo.
- **`HPCMonitor`** (`hpc_monitor.py`) : Suivi des métriques de nœuds et jobs Slurm.

---

## 2. Dépendances et Absence d'Imports Circulaires

- **Imports Entrants** : `acf.hpc_connector` est consommé par `acf.hpc_workflow` et `acf.gui.esoc`.
- **Imports Sortants** : Le package utilise uniquement la bibliothèque standard Python et des bibliothèques optionnelles (`paramiko`, `pyyaml`).
- **Analyse Circulaire** : Aucun import circulaire n'a été détecté lors de la compilation et des tests.

---

## 3. Fichiers de Sauvegarde et Recommandations de Nettoyage

Les deux fichiers de sauvegarde ci-dessous ont été repérés :
1. `src/acf/hpc_connector/connection_manager.py.backup` (7 072 octets)
2. `src/acf/hpc_connector/ssh_connector.py.backup` (4 057 octets)

*Recommandation :* Conserver ces fichiers intacts si nécessaire ou les archiver en dehors du package actif pour éviter toute confusion.
