# ACF OPERATIONAL MANUAL (ACF-POST-001)

**Role:** Lead Systems Engineer & Operational Chief  
**Target Release:** ACF v1.0.0 LTS (Global Earth System Operations Platform)  
**Workspace Root:** `/home/souhaib/ACF`  
**Git Branch:** `develop`  
**Date:** August 6, 2026  

---

## 1. OPERATIONAL WORKFLOW LAUNCH & CONTROL

To launch the Atmospheric Complexity Framework (ACF) ESOC Command Center and operational NWP pipeline:

```bash
# Activate Conda/Virtual Environment
source /home/souhaib/ACF/.venv/bin/activate

# Launch ESOC Command Center GUI
python -m acf.gui.esoc
```

### Operational Command Features:
- **HPC Execution Panel**: Select NWP model (`ARPEGE`, `AROME`, `ALADIN`, `WRF`, `ICON`, `OpenIFS`, `IFS`), configure case parameters, and launch 6-stage Slurm DAG workflows.
- **HPC Monitor Dashboard**: Real-time tracking of Slurm cluster queues (`squeue`), node health (`sinfo`), and hardware metrics.
- **NWP Verification Center**: Operational scorecard review, continuous/categorical metric curves, and inter-model comparison tables.
