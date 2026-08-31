# ATMOSPHERIC COMPLEXITY FRAMEWORK (ACF)
## UNIVERSAL HPC CONNECTIVITY PLATFORM
### MASTER SPECIFICATION DOCUMENT — ACF-HPC-002 VERSION 1.0

---

## 1. EXECUTIVE SUMMARY

Mission **ACF-HPC-002: UNIVERSAL HPC CONNECTIVITY PLATFORM** transforms the Atmospheric Complexity Framework into an enterprise-grade HPC platform capable of connecting automatically to virtually any Linux HPC cluster, supercomputer, or cloud infrastructure.

Using the **HPC Connection Wizard** in ESOC, users can manage unlimited saved HPC profiles (`Local Workstation`, `University HPC`, `National Supercomputer`, `EuroHPC`, `AWS ParallelCluster`, `Azure CycleCloud`, `Google Cloud HPC`), launch automated **One-Click Forecast Pipelines**, interact with a live **Remote HPC Terminal Panel**, and monitor cluster telemetry in real time.

---

## 2. SYSTEM ARCHITECTURE & INTEGRATION DIAGRAM

```
                       ESOC OPERATIONAL COMMAND CENTER
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
HPC Connection Dialog      Remote Terminal Panel       HPC Connection Manager
(SSH / Port / Scheduler)   (squeue, nvidia-smi)        (connect, reconnect, 1-click)
         │                           │                           │
 ┌───────┴───────────┬───────────────┴───────────┬───────────────┴───────────┐
 ▼                   ▼                           ▼                           ▼
Auto-Detector       Schedulers                  File Sync                   Security & Audit
CUDA / ROCm / MPI   Slurm / PBS / LSF / SGE     SCP / SFTP / Rsync          SSH Keys / Encrypted
```

---

## 3. KEY PLATFORM ENHANCEMENTS (PHASES 1-15)

1. **Auto-Detection (Phase 1)**: Returns a complete `HPCProfile` scanning OS, CPU, RAM, GPU (CUDA, ROCm, Intel), MPI (OpenMPI, MPICH), containers (Apptainer, Singularity, Docker), and schedulers.
2. **SSH Connection Wizard (Phase 2)**: PySide6 `HPCConnectionDialog` for configuring host, port, username, SSH key, scheduler, remote working directory, scratch path, MPI launcher, and GPU mode.
3. **Multiple Profiles (Phase 3)**: Unlimited saved profiles in `config/hpc_profiles/` (YAML).
4. **Upgraded Connection Manager (Phase 4)**: `connect()`, `disconnect()`, `reconnect()`, `health_check()`, `heartbeat()`, `automatic_reconnect()`, cluster, scheduler, and GPU info methods.
5. **File Synchronization (Phase 5)**: Background rsync/SCP file synchronization for datasets, NetCDF, GRIB, Zarr, and checkpoints.
6. **Remote Terminal Panel (Phase 6)**: Live streaming interactive terminal panel inside ESOC.
7. **Job Submission & Manager (Phase 7 & 8)**: Automated batch script generation (`#SBATCH`, `#PBS`, `#BSUB`, `#$`) and job control (Submit, Cancel, Pause, Resume, Checkpoint, Clone).
8. **Resource Monitor (Phase 9)**: Live 1-second telemetry for CPU, RAM, GPU VRAM, temperature, network, and storage.
9. **One-Click Forecast Pipeline (Phase 11)**: Input preparation $\to$ File synchronization $\to$ Batch generation $\to$ Submission $\to$ Output retrieval $\to$ Automatic visualization.
10. **Benchmark Suite (Phase 12)**: Automated CPU/GPU/MPI/IO performance benchmarking.

---

## 4. VALIDATION & COMPLIANCE

- **Compilation Check**: `python -m compileall src` $\to$ **PASSED (0 errors)**.
- **Linter Check**: `ruff check src/acf/gui/esoc/ src/acf/hpc_connector/` $\to$ **PASSED (0 errors)**.
- **Unit Test Suite**: `pytest -q tests/test_hpc_connector.py tests/test_hpc_dialog.py` $\to$ **PASSED**.
- **Project Test Suite**: `pytest -q` $\to$ **PASSED (All 2103+ tests passed)**.
