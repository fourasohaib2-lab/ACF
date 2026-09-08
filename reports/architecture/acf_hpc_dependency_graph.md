# GRAPHE DE DÉPENDANCES DU SOUS-SYSTÈME HPC ACF (ACF-HPC-001)

**Role :** Chief HPC Architect & Chief Distributed Systems Architect  
**Date :** 3 août 2026  
**Dépôt :** Atmospheric Complexity Framework (ACF)  

---

## 1. Graphe d'Architecture Globale (ASCII)

```
================================================================================
                    ACF UNIFIED HPC PLATFORM DEPENDENCY GRAPH
================================================================================

[USER / ESOC GUI / CLI TRIGGER]
  │
  ▼
[WORKFLOW ORCHESTRATION LAYER - src/acf/hpc_workflow/]
  │  ├── WorkflowEngine (Master Orchestration Class)
  │  ├── WorkflowExecutor (Stage Runner)
  │  ├── WorkflowScheduler (Cycle Timer 00Z-18Z)
  │  ├── WorkflowMonitor (Progress Metrics)
  │  ├── WorkflowContext (State & Checkpointing)
  │  └── WorkflowArchive / History (Persistent Audit)
  │
  ▼
[HPC CONNECTOR LAYER - src/acf/hpc_connector/]
  │  ├── ConnectionManager (SSH Persistence)
  │  ├── RemoteExecutor (Remote Command Execution)
  │  ├── SchedulerInterface (SLURM / PBS / LSF / SGE Driver)
  │  ├── JobManager (Submit / Cancel / Poll)
  │  ├── QueueManager (Queue Status & Slots)
  │  ├── EnvironmentManager & ModuleLoader (Lmod / Environment Modules)
  │  └── HPCDataManager & FileTransfer (SFTP / rsync / Staging)
  │
  ▼
[REMOTE HPC CLUSTER INFRASTRUCTURE]
     ├── Login Nodes (SSH Access)
     ├── Compute Nodes (MPI Parallel Runs)
     └── HPC High-Performance Filesystem (Lustre / NFS)

================================================================================
```
