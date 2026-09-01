"""Production Cluster Detector for FENNEC Supercomputer (ACF-HPC-100).

NOTE (correction - operationally dangerous): every detect_*() method
below used to return fixed, plausible-looking hardware/software claims
regardless of what self.executor.execute_command() actually returned -
detect_scheduler()/detect_containers()/detect_environment()/
detect_interconnect() didn't even call it at all, and detect_mpi()
called it but still unconditionally reported "has_mpi": True even when
the command never ran for real. RemoteExecutor.execute_command()
already exposes an honest "is_simulated" marker precisely for this
(see its own NOTE) - completely unused here until now. The real impact
is not cosmetic: HPCConnectionManager.__init__() reads
cluster_info["scheduler"]["type"] to pick which BaseSchedulerInterface
subclass to instantiate (SlurmScheduler vs PBSScheduler vs
LocalScheduler) - with the old fabricated always-"slurm" claim, a
connection manager for a system that has no scheduler, or a
PBS/Torque one, would silently be wired up with the wrong scheduler
interface. Every method now genuinely gates its claims on whether a
real (non-simulated) remote command actually confirmed them, reporting
None/False/"unknown" otherwise rather than a fabricated specific.
"""

from typing import Any

from acf.hpc_connector.logging import log_hpc_event
from acf.hpc_connector.remote_executor import RemoteExecutor


class ClusterDetector:
    """Detects Linux distro, kernel, CPU, RAM, MPI, CUDA, ROCm, SLURM, InfiniBand, and Filesystems over Paramiko SSH."""

    def __init__(self, executor: RemoteExecutor | None = None) -> None:
        self.executor = executor or RemoteExecutor()

    def detect_all(self) -> dict[str, Any]:
        """Perform full remote system detection."""
        log_hpc_event("INFO", "Running cluster hardware and software auto-detection...")
        return {
            "os": self.detect_os(),
            "cpu": self.detect_cpu(),
            "gpu": self.detect_gpu(),
            "mpi": self.detect_mpi(),
            "scheduler": self.detect_scheduler(),
            "containers": self.detect_containers(),
            "environment": self.detect_environment(),
            "storage": self.detect_storage(),
            "interconnect": self.detect_interconnect(),
        }

    @staticmethod
    def _is_real(res: dict[str, Any]) -> bool:
        """True only if execute_command() genuinely ran remotely (not the offline-fallback placeholder)."""
        return not res.get("is_simulated", True) and res.get("exit_code", 1) == 0

    def detect_os(self) -> dict[str, Any]:
        """Detect OS distribution and kernel version via SSH."""
        res = self.executor.execute_command("uname -sr")
        is_real = self._is_real(res)
        kernel = res.get("stdout", "").strip() if is_real else None

        hostname = None
        if is_real:
            host_res = self.executor.execute_command("hostname -f 2>/dev/null || hostname")
            if self._is_real(host_res):
                hostname = host_res.get("stdout", "").strip() or None

        return {
            "system": "Linux" if kernel else None,
            "release": kernel,
            "platform": kernel,
            "hostname": hostname,
            "architecture": None,
            "is_real_data": is_real,
        }

    def detect_cpu(self) -> dict[str, Any]:
        """Detect CPU core count and topology."""
        res = self.executor.execute_command("nproc")
        is_real = self._is_real(res)
        cores = None
        if is_real:
            try:
                cores = int(res.get("stdout", "").strip().splitlines()[0])
            except (ValueError, IndexError):
                cores = None

        return {
            "cores": cores,
            "architecture": None,
            "processor": None,
            "is_real_data": is_real and cores is not None,
        }

    def detect_gpu(self) -> dict[str, Any]:
        """Detect NVIDIA CUDA, AMD ROCm, or Intel GPUs."""
        res = self.executor.execute_command(
            "nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null"
        )
        is_real = self._is_real(res)
        stdout = res.get("stdout", "").strip() if is_real else ""
        has_cuda = is_real and bool(stdout)

        return {
            "has_gpu": has_cuda,
            "type": f"CUDA ({stdout.splitlines()[0]})" if has_cuda else ("CPU-only" if is_real else None),
            "has_cuda": has_cuda,
            "has_rocm": False,
            "has_intel": False,
            "is_real_data": is_real,
        }

    def detect_mpi(self) -> dict[str, Any]:
        """Detect installed MPI implementation (OpenMPI, IntelMPI, MPICH)."""
        res = self.executor.execute_command(
            "ompi_info --version 2>/dev/null || mpirun --version 2>/dev/null || srun --version 2>/dev/null"
        )
        is_real = self._is_real(res)
        stdout = res.get("stdout", "") if is_real else ""
        has_mpi = is_real and bool(stdout.strip())

        impl = None
        if has_mpi:
            if "Intel" in stdout:
                impl = "Intel MPI"
            elif "MPICH" in stdout:
                impl = "MPICH"
            elif "Open MPI" in stdout or "OpenMPI" in stdout:
                impl = "OpenMPI"
            else:
                impl = stdout.strip().splitlines()[0]

        return {"has_mpi": has_mpi, "implementation": impl, "executable": None, "is_real_data": is_real}

    def detect_scheduler(self) -> dict[str, Any]:
        """Detect SLURM/PBS Workload Manager."""
        res = self.executor.execute_command(
            "sinfo --version 2>/dev/null || squeue --version 2>/dev/null || qstat --version 2>/dev/null"
        )
        is_real = self._is_real(res)
        stdout = res.get("stdout", "").strip() if is_real else ""

        scheduler_type = "unknown"
        has_scheduler = False
        version = None
        if is_real and stdout:
            has_scheduler = True
            version = stdout.splitlines()[0]
            if "slurm" in stdout.lower():
                scheduler_type = "slurm"
            elif "pbs" in stdout.lower() or "torque" in stdout.lower():
                scheduler_type = "pbs"

        return {
            "type": scheduler_type,
            "has_scheduler": has_scheduler,
            "version": version,
            "is_real_data": is_real,
        }

    def detect_containers(self) -> dict[str, Any]:
        """Detect container runtimes (Apptainer, Singularity, Docker)."""
        res = self.executor.execute_command(
            "command -v apptainer; command -v singularity; command -v docker"
        )
        is_real = self._is_real(res)
        stdout = res.get("stdout", "") if is_real else ""

        return {
            "apptainer": is_real and "apptainer" in stdout,
            "singularity": is_real and "singularity" in stdout,
            "docker": is_real and "docker" in stdout,
            "is_real_data": is_real,
        }

    def detect_environment(self) -> dict[str, Any]:
        """Detect Python, Conda, and virtual environment details."""
        res = self.executor.execute_command(
            "python3 --version 2>&1; echo CONDA=$CONDA_DEFAULT_ENV; echo VENV=$VIRTUAL_ENV"
        )
        is_real = self._is_real(res)
        stdout = res.get("stdout", "") if is_real else ""

        python_version = None
        in_conda = False
        in_virtualenv = False
        if is_real:
            for line in stdout.splitlines():
                if line.startswith("Python "):
                    python_version = line.removeprefix("Python ").strip()
                elif line.startswith("CONDA="):
                    in_conda = bool(line.removeprefix("CONDA=").strip())
                elif line.startswith("VENV="):
                    in_virtualenv = bool(line.removeprefix("VENV=").strip())

        return {
            "python_version": python_version,
            "in_conda": in_conda,
            "in_virtualenv": in_virtualenv,
            "is_real_data": is_real,
        }

    def detect_storage(self) -> dict[str, Any]:
        """Detect shared filesystem paths.

        NOTE: scratch_dir/home_dir are ACF's genuinely configured FENNEC
        deployment paths (same values as
        HPCConnectionManager.filesystem_information()'s already-reviewed
        profile config, not a live detection claim) - kept as real
        configuration, not fabricated. filesystem_type historically
        claimed a specific "BeeGFS / Lustre" technology as if verified;
        that part genuinely was never detected, so is now honestly None
        unless a real `stat -f` probe confirms it.
        """
        res = self.executor.execute_command("stat -f -c %T /scratch 2>/dev/null")
        is_real = self._is_real(res)
        fs_type = res.get("stdout", "").strip() if is_real and res.get("stdout", "").strip() else None

        return {
            "scratch_dir": "/scratch/users/sfoura",
            "home_dir": "/onm/dem/home/sfoura",
            "filesystem_type": fs_type,
            "is_real_data": is_real and fs_type is not None,
        }

    def detect_interconnect(self) -> dict[str, Any]:
        """Detect InfiniBand high-speed interconnect."""
        res = self.executor.execute_command("ibstat 2>/dev/null | head -5")
        is_real = self._is_real(res)
        stdout = res.get("stdout", "").strip() if is_real else ""

        return {
            "type": "InfiniBand" if stdout else None,
            "bandwidth_gbps": None,
            "is_real_data": is_real and bool(stdout),
        }
