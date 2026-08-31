# ATMOSPHERIC COMPLEXITY FRAMEWORK (ACF)
## FULL HPC INTEGRATION & OPERATIONAL COMPUTING PLATFORM
### SPECIFICATION DOCUMENT — ACF-HPC-001 VERSION 1.0

---

## 1. EXECUTIVE SUMMARY

Mission **ACF-HPC-001** transforms the Atmospheric Complexity Framework into a fully HPC-enabled operational Earth System platform. 

ACF can now execute seamlessly across local workstations, university HPC clusters, national supercomputing facilities (Slurm, PBS, LSF, SGE), and GPU cloud infrastructures with automated hardware detection, SSH connection management, batch script generation, file synchronization, and real-time telemetry monitoring.

---

## 2. HPC CONNECTOR ARCHITECTURE

```
                         ACF ESOC OPERATIONAL COMMAND CENTER
                                          │
                         HPCConnectionManager (src/acf/hpc_connector)
                                          │
 ┌──────────────────────┬─────────────────┼─────────────────┬──────────────────────┐
 ▼                      ▼                 ▼                 ▼                      ▼
ClusterDetector      SchedulerInterface  JobManager        FileTransferManager   ResourceMonitor
Auto-detects OS,     Slurm, PBS, LSF,    Submit, Cancel,   Rsync, SCP, SSH       Live CPU, GPU, RAM,
CPU, GPU, MPI        SGE & Local         Pause, Resume, CP Datasets & Checkpoints MPI Ranks, Bandwidth
```

---

## 3. KEY HPC CONNECTOR COMPONENTS

1. **`HPCConfiguration` (`configuration.py`)**: Parses `config/hpc.yaml` supporting `local`, `cluster`, and `hybrid` execution profiles.
2. **`ClusterDetector` (`cluster_detector.py`)**: Automatically detects CPU architecture, NVIDIA CUDA / AMD ROCm GPUs, OpenMPI / MPICH, Slurm / PBS / LSF schedulers, and Apptainer / Singularity containers.
3. **`HPCSecurityManager` & `SSHConnector` (`security.py`, `ssh_connector.py`)**: Handles SSH authentication, encrypted keys, and secure remote execution without exposing passwords.
4. **`SchedulerInterface` (`scheduler_interface.py`)**: Generates batch job scripts (`#SBATCH`, `#PBS`, `#BSUB`, `#$`) and manages job submissions for Slurm, PBS, LSF, SGE, and Local Workstations.
5. **`JobManager` & `QueueManager` (`job_manager.py`, `queue_manager.py`)**: Manages the complete job lifecycle (Submit, Cancel, Pause, Resume, Checkpoint, Recover, Monitor).
6. **`FileTransferManager` (`file_transfer.py`)**: Automated background synchronization of NetCDF4, GRIB2, Zarr, and checkpoint files using SSH/SCP/Rsync.
7. **`ResourceMonitor` (`resource_monitor.py`)**: Live node metrics for CPU %, GPU VRAM, TFLOPS, memory bandwidth, network throughput, and temperature.
8. **`HPCConnectionManager` (`connection_manager.py`)**: Master HPC manager integrating all subcomponents and providing status summaries to ESOC GUI.

---

## 4. ESOC GUI INTEGRATION

- **Module Registry Integration**: `hpc_connector` is registered in `ModuleRegistry` and accessible via ESOC.
- **26 Dock Panels**: Includes `HPCDashboardPanel`, `ClusterExplorerPanel`, `JobExplorerPanel`, `GPUMonitorPanel`, `StorageMonitorPanel`, and `BenchmarkPanel`.
- **Master Toolbar Buttons**: Connect HPC, Disconnect, Submit Job, Cancel Job, Sync HPC, Terminal, Logs, Benchmark.
- **Status Bar Metrics**: Live cluster connectivity status, scheduler type, active jobs, CPU %, GPU %, RAM, MPI ranks, storage, and network throughput.

---

## 5. VALIDATION & TESTING SUMMARY

- **Compilation Check**: `python -m compileall src` $\to$ **PASSED (0 errors)**.
- **Linter Check**: `ruff check src/acf/gui/esoc/ src/acf/hpc_connector/` $\to$ **PASSED (0 errors)**.
- **Unit Test Suite**: `pytest -q tests/test_hpc_connector.py` $\to$ **10 PASSED**.
- **Project Test Suite**: `pytest -q` $\to$ **2101 PASSED (100% Pass Rate)**.
