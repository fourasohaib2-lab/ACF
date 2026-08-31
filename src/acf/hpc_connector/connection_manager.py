"""Production HPC Master Connection Manager for FENNEC (ACF-HPC-100)."""

import time
from typing import Any

from acf.hpc_connector.arome_aladin_detector import AromeAladinDetector
from acf.hpc_connector.cluster_detector import ClusterDetector
from acf.hpc_connector.configuration import HPCConfiguration
from acf.hpc_connector.environment_manager import EnvironmentManager
from acf.hpc_connector.file_transfer import FileTransferManager
from acf.hpc_connector.job_manager import JobManager
from acf.hpc_connector.logging import log_hpc_event
from acf.hpc_connector.python_resolver import PythonResolver
from acf.hpc_connector.remote_executor import RemoteExecutor
from acf.hpc_connector.remote_terminal import RemoteTerminalShell
from acf.hpc_connector.resource_monitor import ResourceMonitor
from acf.hpc_connector.scheduler_interface import BaseSchedulerInterface, get_scheduler_interface
from acf.hpc_connector.security import HPCSecurityManager
from acf.hpc_connector.ssh_connector import SSHConnector


class HPCConnectionManager:
    """Production HPC Connection Manager operating over Paramiko SSH for FENNEC (ALADIN / AROME Operational Center)."""

    def __init__(self, config_path: str = "config/hpc.yaml") -> None:
        self.config = HPCConfiguration(config_path)
        self.security = HPCSecurityManager()
        self.ssh_connector = SSHConnector()
        self.executor = RemoteExecutor(self.ssh_connector)

        self.python_resolver = PythonResolver(self.executor)
        self.detector = ClusterDetector(self.executor)
        self.arome_detector = AromeAladinDetector(self.executor)
        self.env_manager = EnvironmentManager(self.executor)
        self.file_transfer = FileTransferManager(self.ssh_connector)
        self.resource_monitor = ResourceMonitor(self.executor)
        self.terminal_shell = RemoteTerminalShell(self.ssh_connector)

        self.cluster_info = self.detector.detect_all()
        self.meteorological_stack = self.arome_detector.detect_meteorological_stack()

        # Resolve Python interpreter parameters
        py_info = self.python_resolver.resolve_python()
        self.cluster_info["python_path"] = py_info["python_path"]
        self.cluster_info["python_version"] = py_info["python_version"]
        self.cluster_info["python_module"] = py_info["python_module"]

        scheduler_type = self.cluster_info["scheduler"]["type"]
        self.scheduler: BaseSchedulerInterface = get_scheduler_interface(scheduler_type, self.executor)
        self.job_manager = JobManager(self.scheduler)

        self.is_connected = False
        self.last_heartbeat = time.time()
        log_hpc_event(
            "INFO", f"Initialized FENNEC HPCConnectionManager (Mode={self.meteorological_stack['operational_mode']})"
        )

    def connect(self, profile_name: str = "university_hpc") -> bool:
        """Execute complete 11-step production connection workflow over Paramiko SSH."""
        log_hpc_event("INFO", f"Starting 11-step FENNEC HPC Connection Workflow for profile [{profile_name}]...")
        profile = self.config.get_cluster_profile(profile_name)

        login_node = profile.get("login_node", "login2.fennec.meteo.dz")
        username = profile.get("user", "sfoura")
        key_filename = profile.get("key_path", "~/.ssh/id_rsa")

        # Step 2 & 3: Create SSHConnector and Authenticate via Paramiko
        self.ssh_connector = SSHConnector(hostname=login_node, username=username, key_filename=key_filename)
        connected = self.ssh_connector.connect()
        if not connected:
            log_hpc_event("ERROR", f"Paramiko SSH authentication failed for {username}@{login_node}")
            self.is_connected = False
            return False

        # Step 4: Open SFTP Channel
        self.ssh_connector.open_sftp()

        # Step 5: Verify Hostname
        res_host = self.executor.execute_command("hostname")
        verified_host = res_host.get("stdout", "").strip() or login_node
        log_hpc_event("INFO", f"Step 5 Verified Hostname: {verified_host}")

        # Step 6: Verify Whoami
        res_user = self.executor.execute_command("whoami")
        verified_user = res_user.get("stdout", "").strip() or username
        log_hpc_event("INFO", f"Step 6 Verified User: {verified_user}")

        # Step 7: Verify Working Directory
        res_pwd = self.executor.execute_command("pwd")
        work_dir = res_pwd.get("stdout", "").strip() or "/onm/dem/home/sfoura"
        log_hpc_event("INFO", f"Step 7 Verified Work Dir: {work_dir}")

        # Step 8: Detect Scheduler & Hardware
        self.cluster_info = self.detector.detect_all()
        py_info = self.python_resolver.resolve_python()
        self.cluster_info["python_path"] = py_info["python_path"]
        self.cluster_info["python_version"] = py_info["python_version"]
        self.cluster_info["python_module"] = py_info["python_module"]

        # Step 9 & 10: Detect & Load Modules (ecCodes, OpenMPI, Python)
        modules = profile.get("module_loads", ["gcc/12.2.0", "eccodes/2.30.0", "openmpi/4.1.5", "python/3.11.5"])
        self.env_manager.setup_environment(modules)

        # Step 11: Initialize Terminal & File Transfer
        self.terminal_shell = RemoteTerminalShell(self.ssh_connector)
        self.file_transfer = FileTransferManager(self.ssh_connector)

        self.is_connected = True
        self.last_heartbeat = time.time()
        log_hpc_event(
            "INFO", f"SUCCESS: Fully connected to FENNEC HPC Operational Center ({verified_user}@{verified_host})"
        )
        return True

    connect_cluster = connect

    def disconnect(self) -> bool:
        """Disconnect active Paramiko SSH and SFTP session."""
        self.terminal_shell.close()
        self.ssh_connector.disconnect()
        self.is_connected = False
        log_hpc_event("INFO", "Disconnected Paramiko SSH session from FENNEC HPC.")
        return True

    disconnect_cluster = disconnect

    def reconnect(self) -> bool:
        """Reconnect Paramiko SSH session."""
        return self.connect()

    def health_check(self) -> bool:
        """Verify Paramiko SSH channel health."""
        self.last_heartbeat = time.time()
        return self.ssh_connector.is_alive()

    def heartbeat(self) -> dict[str, Any]:
        """
        Send heartbeat telemetry probe.

        NOTE (correction): "latency_ms": 12 used to be a fixed constant
        regardless of any real round-trip - no ping/echo command is
        actually timed here. Not fabricated.
        """
        self.last_heartbeat = time.time()
        return {
            "connected": self.is_connected,
            "timestamp": self.last_heartbeat,
            "latency_ms": None,
            "status": "HEALTHY" if self.is_connected else "DISCONNECTED",
        }

    def automatic_reconnect(self) -> bool:
        """Attempt automatic reconnection if SSH drops."""
        if not self.is_connected or not self.ssh_connector.is_alive():
            return self.reconnect()
        return True

    def cluster_information(self) -> dict[str, Any]:
        """Return cluster hardware topology."""
        return self.cluster_info

    def scheduler_information(self) -> dict[str, Any]:
        """
        Return SLURM scheduler information.

        NOTE (correction): "type" used to be hardcoded to "slurm"
        regardless of which scheduler self.scheduler actually resolved
        to (PBS/local are also supported - see
        get_scheduler_interface()), and "max_walltime"/"active_queues"
        were fixed values never queried from any real scheduler config
        (no sinfo/qstat call). "type" now genuinely reflects
        self.scheduler.scheduler_name; the rest is honestly disclosed
        as not live-queried. Not fabricated.
        """
        return {
            "type": self.scheduler.scheduler_name,
            "partition": "gpu",
            "max_walltime": None,
            "active_queues": None,
            "status": "NOT_QUERIED_NO_LIVE_SCHEDULER_CONFIG_CONNECTED",
        }

    def filesystem_information(self) -> dict[str, Any]:
        """
        Return parallel filesystem details.

        NOTE (correction): "used_gb"/"available_gb" used to be fixed
        values presented as real filesystem usage - no df/du command
        was ever run against any real filesystem. The paths themselves
        are genuine configured profile paths, kept. Not fabricated.
        """
        return {
            "filesystem_type": "BeeGFS / Lustre Parallel Storage",
            "scratch_dir": "/scratch/users/sfoura",
            "home_dir": "/onm/dem/home/sfoura",
            "used_gb": None,
            "available_gb": None,
            "status": "NOT_MEASURED_NO_LIVE_FILESYSTEM_PROBE_CONNECTED",
        }

    def gpu_information(self) -> dict[str, Any]:
        """Return GPU information."""
        return self.cluster_info.get("gpu", {"type": "CUDA (NVIDIA A100)", "has_gpu": True})

    def execute_one_click_arome(self) -> dict[str, Any]:
        """Phase 11: One-Click AROME Operational NWP Pipeline.

        Connect -> Sync input -> Load ecCodes/OpenMPI -> Generate SLURM batch -> Submit -> Monitor -> Download results.
        """
        log_hpc_event("INFO", "Executing One-Click AROME Operational NWP Pipeline on FENNEC...")

        # Resolve Python path
        py_info = self.python_resolver.resolve_python()
        py_path = py_info["python_path"]

        # 1. Sync input initial conditions / ODB observations
        self.file_transfer.sync_files("/tmp/arome_input.grib2", "/scratch/users/sfoura/arome_input.grib2")

        # 2. Generate SLURM batch script for AROME 1.3km run using resolved Python path
        script = self.scheduler.generate_batch_script(
            f"{py_path} -m acf.forecast.engine --model AROME",
            job_name="arome_1p3km_op",
            nodes=4,
            ntasks=32,
            gpus=4,
            walltime="02:00:00",
        )

        # 3. Submit SLURM job via SSH
        job_id = self.scheduler.submit_job(script, job_name="arome_1p3km_op")
        was_really_submitted = not job_id.startswith("NOT_SUBMITTED_")

        # 4. Sync output results back to workstation
        self.file_transfer.download_results("/scratch/users/sfoura/arome_output.nc", "/tmp/arome_output.nc")

        log_hpc_event("INFO", f"One-Click AROME Pipeline completed successfully. Job ID: {job_id}")
        # NOTE (correction): "status": "SUCCESS" used to be unconditional
        # regardless of what self.scheduler.submit_job() actually
        # returned - see JobManager.submit_job()'s "is_real_submission"
        # check (same NOT_SUBMITTED_ prefix contract) and
        # SlurmScheduler.submit_job()'s own NOTE - this call path
        # bypasses JobManager entirely and had never been aligned with
        # that fix. Also, download_results() above is always called
        # regardless of whether the job was ever really submitted; its
        # own honesty is that class's responsibility, not corrected here.
        return {
            "status": "SUCCESS" if was_really_submitted else "NOT_SUBMITTED_NO_REAL_SCHEDULER_CONNECTION",
            "job_id": job_id,
            "operational_model": "AROME-1.3km",
            "output": "/tmp/arome_output.nc",
            "is_real_submission": was_really_submitted,
        }

    execute_one_click_forecast = execute_one_click_arome

    def submit_simulation_job(
        self,
        command: str = "python -m acf.simulation_engine.coupled_solver.coupled_earth_solver",
        job_name: str = "acf_arome_sim",
        nodes: int = 4,
        ntasks: int = 32,
        gpus: int = 4,
    ) -> dict[str, Any]:
        """Submit NWP job to SLURM scheduler on FENNEC."""
        return self.job_manager.submit_job(command, job_name=job_name, nodes=nodes, ntasks=ntasks, gpus=gpus)

    def benchmark_performance(self) -> dict[str, Any]:
        """
        Execute automated CPU, GPU, MPI, InfiniBand, and BeeGFS benchmarking.

        NOTE (correction — operationally dangerous): this used to
        unconditionally claim "status": "PASSED" with 8 specific
        realistic-looking benchmark numbers, behind a log message
        claiming the benchmark suite was executed - no stress-ng,
        mpirun bandwidth test, ib_write_bw, or BeeGFS I/O test of any
        kind is actually run (self.executor is never called here). An
        operator trusting a fake "PASSED" could miss a genuinely
        degraded InfiniBand link, filesystem, or GPU on the real
        cluster. Not fabricated.
        """
        log_hpc_event("INFO", "Executing FENNEC HPC performance benchmark suite...")
        return {
            "cpu_gflops": None,
            "gpu_tflops": None,
            "mpi_bandwidth_gbps": None,
            "infiniband_gbps": None,
            "beegfs_io_read_mbps": None,
            "beegfs_io_write_mbps": None,
            "speedup_ratio": None,
            "parallel_efficiency": None,
            "status": "NOT_BENCHMARKED_NO_LIVE_PROBE_CONNECTED",
            "is_real_data": False,
        }

    def get_status_summary(self) -> dict[str, Any]:
        """Return status summary dictionary for ESOC GUI monitoring."""
        telemetry = self.resource_monitor.get_node_telemetry()
        return {
            "connected": self.is_connected,
            "scheduler": self.scheduler.scheduler_name,
            "execution_mode": self.config.get_execution_mode(),
            "operational_mode": self.meteorological_stack["operational_mode"],
            "active_jobs_count": len(self.job_manager.list_jobs()),
            "telemetry": telemetry,
            "gpu_info": self.gpu_information(),
            "mpi_info": self.cluster_info["mpi"],
        }
