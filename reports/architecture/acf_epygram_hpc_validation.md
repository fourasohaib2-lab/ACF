# VALIDATION DE L'ORCHESTRATION HPC & EPYGRAM (ACF-NWP-EPYGRAM-005)

**Role :** Chief HPC Architect & Principal QA Architect  
**Date :** 3 août 2026  
**Dépôt :** Atmospheric Complexity Framework (ACF)  

---

## 1. Audit & Qualification du Sous-Système HPC

L'ensemble des composants d'interfaçage HPC et de gestion de workflows a été audité et qualifié :

- **`WorkflowEngine` (`src/acf/hpc_workflow/workflow_engine.py`)** : Orchestration complète des 12 étapes opérationnelles (Initialisation, Pré-traitement, Observation Check, Assimilation, SURFEX, PREP, Exécution Modèle, Post-Processing, Génération de Produits, Contrôle Qualité, Archivage, Nettoyage) pour les cycles `00 UTC`, `06 UTC`, `12 UTC` et `18 UTC`.
- **`SchedulerInterface` (`src/acf/hpc_connector/scheduler_interface.py`)** : Interfaçage SLURM / PBS / LSF / SGE pour le soumission et le suivi des jobs.
- **`HPCDataManager` (`src/acf/hpc_connector/data_management/data_manager.py`)** : Gestionnaire de staging et de transfert de fichiers haut débit.
- **`RemoteExecutor` & `SSHConnector` (`src/acf/hpc_connector/`)** : Exécution distante sécurisée et monitoring des ressources de calcul.

---

## 2. Matrice de Validation des Modules HPC

| Composant HPC | Statut | Fonctionnalité Validée |
| :--- | :--- | :--- |
| **Workflow Engine** | **CERTIFIÉ** | Orchestration séquentielle des 12 stages et gestion d'erreurs. |
| **AROME Workflow** | **CERTIFIÉ** | Cycle de prévision AROME 1.3km à 90 niveaux hybrides. |
| **ALADIN Workflow** | **CERTIFIÉ** | Cycle de prévision ALADIN 7.5km à 70 niveaux hybrides. |
| **Scheduler** | **CERTIFIÉ** | Génération de scripts SLURM/PBS et détection de statut. |
| **Remote Executor** | **CERTIFIÉ** | Exécution distante via SSH et gestion des logs d'erreurs. |
| **HPC Data Manager** | **CERTIFIÉ** | Staging et conversion transparente des fichiers FA/LFA/GRIB via `EPyGrAMReader`. |

---

## 3. Gestion de la Tolérance aux Panne & Reprise sur Erreur

1. **Recovery après Échec de Stage** : Le `WorkflowEngine` enregistre l'état du contexte à chaque étape (`CycleContext`), permettant une reprise exacte au dernier point de contrôle (stage checkpoint).
2. **Fallback Gracieux** : Si `epygram` rencontre un problème binaire sur un nœud de calcul spécifique, le gestionnaire d'erreurs bascule automatiquement sur les logs explicites sans bloquer le scheduler global.
