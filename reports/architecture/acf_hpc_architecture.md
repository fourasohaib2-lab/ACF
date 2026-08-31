# ARCHITECTURE DE LA PLATEFORME HPC UNIFIÉE ACF (ACF-HPC-001)

**Signataires :**
- Chief HPC Architect
- Chief Distributed Systems Architect
- Chief Software Architect
- Chief Python Architect
- Chief Scientific Computing Architect

**Date :** 3 août 2026  
**Workspace :** `/home/souhaib/ACF` (obtenu via `git rev-parse --show-toplevel`)  
**Branche Git :** `develop`  

---

## 1. Vue d'Ensemble & Objectifs

La plateforme d'exécution HPC de l'Atmospheric Complexity Framework (ACF) fournit une couche d'abstraction agnostique permettant de soumettre, surveiller, orchestrer et rapatrier les calculs scientifiques sur n'importe quel cluster HPC (FENNEC, Météo-France, ECMWF, Supercalculateurs Nationaux/Européens) indépendamment du système de gestion de files d'attente sous-jacent (SLURM, PBS, LSF, SGE).

```
                      Workstation Client ACF / ESOC GUI
                                      │
                                      ▼
                        HPC Platform Access Layer
                                      │
             ┌────────────────────────┴────────────────────────┐
             ▼                                                 ▼
   HPC Connector Subsystem                           HPC Workflow Subsystem
(src/acf/hpc_connector/)                           (src/acf/hpc_workflow/)
  ├── ConnectionManager                              ├── WorkflowEngine
  ├── RemoteExecutor                                 ├── WorkflowExecutor
  ├── SchedulerInterface (SLURM/PBS/LSF)             ├── WorkflowScheduler
  ├── QueueManager & JobManager                      ├── WorkflowMonitor
  └── HPCDataManager                                 └── WorkflowArchive / History
             │                                                 │
             └────────────────────────┬────────────────────────┘
                                      ▼
                           Grappes HPC Distantes
```

---

## 2. Inventaire Canonique des Composants HPC

### 2.1 Subsystem Connector (`src/acf/hpc_connector/`)
1. **`ConnectionManager`** : Gestion des sessions SSH sécurisées et persistance de la connexion.
2. **`RemoteExecutor`** : Exécution distante de commandes shell, scripts et binaires scientifiques.
3. **`SchedulerInterface`** : Interfaçage agnostique des ordonnanceurs (SLURM, PBS, LSF, SGE).
4. **`JobManager`** : Soumission, annulation, mise en pause et récupération de statut des jobs.
5. **`QueueManager`** : Inspection et régulation des queues de calcul.
6. **`ClusterDetector`** : Détection automatique de l'environnement matériel, des nœuds MPI et des compilateurs.
7. **`EnvironmentManager` & `ModuleLoader`** : Découverte et chargement dynamique des modules HPC (`eccodes`, `netcdf`, `epygram`, `openmpi`).
8. **`HPCDataManager` & `FileTransfer`** : Staging et transfert haut débit (SFTP/rsync) des datasets.
9. **`SecurityManager`** : Authentification par clés SSH et chiffrement des identifiants.
10. **`ResourceMonitor`** : Suivi de la consommation mémoire, CPU, GPU et bande passante réseau.

### 2.2 Subsystem Workflow (`src/acf/hpc_workflow/`)
1. **`WorkflowEngine`** : Moteur maître d'orchestration des 12 étapes opérationnelles (cycles AROME/ALADIN 00, 06, 12, 18 UTC).
2. **`WorkflowExecutor`** : Moteur d'exécution des stages de prévision.
3. **`WorkflowScheduler`** : Planification temporelle des runs opérationnels.
4. **`WorkflowMonitor`** : Suivi temps-réel de l'avancement et des métriques.
5. **`WorkflowArchive` & `WorkflowHistory`** : Archivage et traçabilité des exécutions.
6. **`WorkflowContext`** : Contexte partagé entre stages garantissant la reprise sur erreur (checkpoint/restart).

---

## 3. Reprise sur Erreur & Robustesse HPC

- **Heartbeat & Monitoring** : Détection automatique de perte de connexion SSH avec reconnexion transparente.
- **Job Cleanup** : Nettoyage automatique des fichiers temporaires en cas d'annulation ou d'expiration (timeout).
- **Stage Checkpointing** : Chaque stage valide son contexte dans `WorkflowContext` avant le passage à l'étape suivante, permettant la reprise exacte au dernier checkpoint.
