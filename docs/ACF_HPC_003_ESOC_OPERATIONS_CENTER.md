# ACF HPC OPERATIONS CENTER (ACF-HPC-003)

**Date :** 3 août 2026  
**Statut :** Spécification & Guide Opérationnel  
**Package Cible :** `acf.hpc_connector` & `acf.gui.esoc`  

---

## 1. Architecture du Centre d'Opérations HPC ESOC

Le centre d'opérations HPC d'ACF fournit un sous-système complet de suivi en temps réel du supercalculateur (Slurm / HPC Fennec ONM) relié à l'interface utilisateur ESOC (Earth System Operations Center).

```
                      ESOC Operations Center GUI (PySide6)
                                       │
                                       ▼
                         HPCDashboardPanel Widget
                     (src/acf/gui/esoc/hpc_dashboard_panel.py)
                                       │
                                       ▼
                          HPCDashboard Backend API
                     (src/acf/hpc_connector/hpc_dashboard.py)
                                       │
                                       ▼
                          HPCMonitor Engine (Slurm)
                     (src/acf/hpc_connector/hpc_monitor.py)
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
     squeue / sacct                 sinfo                   scontrol / sdiag
   (Jobs & Historique)        (Nœuds & Partitions)         (Santé & Métriques)
```

---

## 2. Description des Composants Majeurs

### 2.1 Moteur de Monitoring (`HPCMonitor`)
Localisé dans `src/acf/hpc_connector/hpc_monitor.py`, la classe `HPCMonitor` encapsule les utilitaires Slurm via `RemoteExecutor` distant ou sous-processus local :
- `list_jobs(user)` : Liste des travaux actifs/en attente via `squeue`.
- `get_job_history(job_id)` : Historique d'exécution et code de sortie via `sacct`.
- `cluster_status()` : Décompte des nœuds (`idle`, `allocated`, `down`) et partitions via `sinfo`.
- `node_status(node_name)` : Métriques détaillées CPU/RAM par nœud via `scontrol show node`.
- `get_cluster_health()` : Synthèse globale du cluster.
- `get_cpu_usage()` & `get_memory_usage()` : Métriques de charge matérielle.
- `get_slurm_statistics()` : Métriques internes du démon via `sdiag`.

### 2.2 Dashboard Backend (`HPCDashboard`)
Localisé dans `src/acf/hpc_connector/hpc_dashboard.py` :
- `refresh()` : Mise à jour de l'ensemble des données.
- `summary()` : Obtenir le dictionnaire résumé en cache.
- `health_score()` : Calcul de l'indice de santé global (0.0 à 100.0%).
- `export_json(filepath)` : Sérialisation JSON pour archivage ou API web.

### 2.3 Interface GUI ESOC (`HPCDashboardPanel`)
Localisé dans `src/acf/gui/esoc/hpc_dashboard_panel.py` :
- Widget PySide6 intégrant les cartes de statut Cluster, Nœuds, Travaux, et barres de progression CPU/RAM avec minuterie de rafraîchissement (10s).

---

## 3. Exemples d'Utilisation API

```python
from acf.hpc_connector import HPCMonitor, HPCDashboard

# 1. Utilisation directe de HPCMonitor
monitor = HPCMonitor(cluster_name="Fennec")
health = monitor.get_cluster_health()
print(f"Cluster: {health['cluster']}, Idle Nodes: {health['nodes_idle']}")

# 2. Utilisation du backend HPCDashboard
dashboard = HPCDashboard(monitor)
summary = dashboard.refresh()
print(f"Health Score: {summary['health_score']}%")

# 3. Export JSON
json_output = dashboard.export_json("hpc_status.json")
```
