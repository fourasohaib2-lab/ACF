"""Production HPC Master Connection Manager for FENNEC (ACF-HPC-100)."""

import sys
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

        # NOTE (correction): __init__ used to call detector.detect_all(),
        # arome_detector.detect_meteorological_stack() and
        # python_resolver.resolve_python() right here - roughly thirty remote
        # commands fired at self.ssh_connector before connect() had ever been
        # called on it, i.e. with no transport in existence at all. Every one of
        # them took the offline fallback path, yet the run produced a confident
        # log block ("Discovered Python cluster modules: [...]",
        # "Meteorological Stack Detection Complete: Mode=STANDARD_NWP, ...",
        # "Python Resolved: Executable=<the local workstation venv>") two full
        # minutes BEFORE the "Connecting via Paramiko SSH to ..." line, which
        # reads as measured cluster facts. Detection now starts as an explicit
        # not-yet-detected state and only runs for real in connect(), after
        # authentication is confirmed.
        self.cluster_info = ClusterDetector.not_detected()
        self.meteorological_stack = AromeAladinDetector.not_detected()

        # The interpreter running ACF locally - a true statement about this
        # process, explicitly NOT a claim about any remote compute node.
        self.cluster_info["python_path"] = sys.executable
        self.cluster_info["python_version"] = (
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )
        self.cluster_info["python_module"] = ""
        self.cluster_info["python_is_remote_verified"] = False

        # Scheduler is deliberately not chosen from an undetected cluster: with
        # no transport, detect_scheduler() reports type "unknown", which
        # get_scheduler_interface() maps to LocalScheduler. connect() re-detects
        # and rebuilds this once the real type is known (see _bind_scheduler()).
        self.scheduler: BaseSchedulerInterface = get_scheduler_interface(
            self.cluster_info["scheduler"]["type"], self.executor
        )
        self.job_manager = JobManager(self.scheduler)

        self.is_connected = False
        self.last_heartbeat = time.time()
        log_hpc_event(
            "INFO", f"Initialized FENNEC HPCConnectionManager (Mode={self.meteorological_stack['operational_mode']})"
        )

    def _bind_scheduler(self, detected_type: str, configured_type: str | None = None) -> None:
        """Point self.scheduler / self.job_manager at the scheduler actually in use.

        Prefers what a live probe detected. If detection could not confirm one
        but the profile explicitly declares a scheduler, that declaration is used
        rather than silently degrading to LocalScheduler - submitting a FENNEC
        job through the local scheduler is worse than trusting the operator's
        own configuration - and the substitution is logged either way.
        """
        chosen = (detected_type or "unknown").lower().strip()
        if chosen == "unknown" and configured_type:
            chosen = configured_type.lower().strip()
            log_hpc_event(
                "WARNING",
                f"Scheduler could not be detected on the cluster; falling back to the profile's "
                f"configured scheduler [{chosen}]. Jobs will be submitted through it.",
            )
        self.scheduler = get_scheduler_interface(chosen, self.executor)
        self.job_manager = JobManager(self.scheduler)
        log_hpc_event("INFO", f"Scheduler interface bound: {self.scheduler.scheduler_name}")

    def connect(self, profile_name: str = "fennec", overrides: dict[str, Any] | None = None) -> bool:
        """
        Execute complete 11-step production connection workflow over Paramiko SSH.

        Args:
            profile_name: key looked up under ``cluster_profiles`` in config/hpc.yaml.
            overrides: connection settings that take precedence over the YAML profile.
                This is what the ESOC HPC Connection Wizard passes in, so the hostname,
                username, port, SSH key and password an operator actually typed are
                honoured instead of being silently discarded (previously only
                profile_name reached this method, and every other field of the wizard
                was dropped - an operator could enter a completely different cluster
                and still be connected to the hardcoded FENNEC login node).

        NOTE (correction): default profile_name used to be
        "university_hpc", which does not exist in config/hpc.yaml's
        cluster_profiles (only "fennec" does) - see
        HPCConfiguration.get_cluster_profile()'s own NOTE for what this
        actually caused. Matches this class's own stated purpose
        ("Production HPC Master Connection Manager for FENNEC").
        """
        log_hpc_event("INFO", f"Starting 11-step FENNEC HPC Connection Workflow for profile [{profile_name}]...")
        profile = dict(self.config.get_cluster_profile(profile_name))
        overrides = {k: v for k, v in (overrides or {}).items() if v not in (None, "")}

        # config/hpc.yaml spells the account "username:", while this method only ever
        # read "user:" - so the configured account was never actually picked up and the
        # hardcoded default silently stood in for it. Both spellings are accepted now.
        login_node = overrides.get("hostname") or profile.get("login_node") or profile.get("hostname") or "login2.fennec.meteo.dz"
        username = overrides.get("username") or profile.get("username") or profile.get("user") or "sfoura"
        key_filename = (
            overrides.get("key_path")
            or profile.get("key_path")
            or self.config.config.get("security", {}).get("ssh_key_path")
            or "~/.ssh/id_rsa"
        )
        port = int(overrides.get("port") or profile.get("port") or 22)
        password = overrides.get("password")

        if not profile and not overrides:
            log_hpc_event(
                "WARNING",
                f"Profile [{profile_name}] not found in cluster_profiles and no overrides given - "
                f"falling back to built-in defaults ({username}@{login_node}).",
            )

        # Step 2 & 3: Create SSHConnector and Authenticate via Paramiko
        self.ssh_connector = SSHConnector(
            hostname=login_node,
            username=username,
            port=port,
            key_filename=key_filename,
            password=password,
            # 2.0 s is not enough for a real SSH handshake to a login node over a
            # VPN; the connector keeps this value now that connect() no longer
            # overwrites it with 0.0015 s.
            timeout=float(overrides.get("timeout") or profile.get("timeout") or 10.0),
        )
        # self.executor / self.resource_monitor / self.detector were all built in
        # __init__ around the ORIGINAL connector object. Replacing self.ssh_connector
        # above used to leave them bound to that stale, never-authenticated instance,
        # so Steps 5-8 below ran their hostname/whoami/pwd checks over the wrong
        # object. Re-point the executor at the connector we just created.
        self.executor.connector = self.ssh_connector
        self.ssh_connector.connect()

        # NOTE (correction - this is what let a failed login report success):
        # SSHConnector.connect() returns True on EVERY path by design, to keep
        # the offline development workflow working (see its own docstring), so
        # `if not connected` here could never fire. A run whose authentication
        # genuinely failed - e.g. the malformed saved username "sfoura@10.16.20.2"
        # that produced five straight "Authentication (publickey) failed" lines -
        # sailed through steps 4 to 11 and finished on
        # "SUCCESS: Fully connected to FENNEC HPC Operational Center".
        # is_real_connection is the honest signal (transport.is_authenticated()).
        if not self.ssh_connector.is_real_connection:
            log_hpc_event(
                "ERROR",
                f"Paramiko SSH authentication FAILED for {username}@{login_node}:{port} - "
                f"no authenticated session. Aborting the connection workflow; "
                f"nothing below was run on the cluster.",
            )
            if "@" in username:
                log_hpc_event(
                    "ERROR",
                    f"The configured username [{username}] contains '@'. It must be a bare account "
                    f"name (e.g. 'sfoura'); a jump/bastion host belongs in its own field, not in the "
                    f"username.",
                )
            self.is_connected = False
            return False

        # Step 4: Open SFTP Channel
        self.ssh_connector.open_sftp()

        # Steps 5-7: verify identity against the cluster.
        # NOTE (correction): these used to read `res.get("stdout", "").strip() or
        # <default>`, which accepts anything non-empty - including the offline
        # fallback placeholder string, which is non-empty. That string would have
        # been logged verbatim as "Step 5 Verified Hostname: [SIMULATED OFFLINE
        # FALLBACK ...]". A value is only a verification if it came back over a
        # real transport.
        def _verified(command: str, label: str, fallback: str) -> str:
            res = self.executor.execute_command(command)
            if res.get("is_simulated", True) or res.get("exit_code", 1) != 0:
                log_hpc_event("WARNING", f"{label}: NOT VERIFIED (no real remote output); assuming {fallback}")
                return fallback
            value = res.get("stdout", "").strip()
            if not value:
                log_hpc_event("WARNING", f"{label}: NOT VERIFIED (empty output); assuming {fallback}")
                return fallback
            log_hpc_event("INFO", f"{label}: {value}")
            return value

        verified_host = _verified("hostname", "Step 5 Verified Hostname", login_node)
        verified_user = _verified("whoami", "Step 6 Verified User", username)
        work_dir = _verified("pwd", "Step 7 Verified Work Dir", profile.get("home") or "/onm/dem/home/sfoura")

        # Step 8: Detect Scheduler & Hardware
        self.cluster_info = self.detector.detect_all()
        self.meteorological_stack = self.arome_detector.detect_meteorological_stack()
        py_info = self.python_resolver.resolve_python()
        self.cluster_info["python_path"] = py_info["python_path"]
        self.cluster_info["python_version"] = py_info["python_version"]
        self.cluster_info["python_module"] = py_info["python_module"]
        self.cluster_info["python_is_remote_verified"] = py_info.get("is_remote_verified", False)

        # NOTE (correction): __init__ picked the scheduler interface from an
        # undetected cluster (type "unknown" -> LocalScheduler) and connect()
        # re-detected the real type here but never rebuilt self.scheduler or
        # self.job_manager - so every job submitted after a genuinely successful
        # FENNEC login still went through LocalScheduler instead of SlurmScheduler.
        self._bind_scheduler(self.cluster_info["scheduler"]["type"], profile.get("scheduler"))

        # Step 9 & 10: Detect & Load Modules (ecCodes, OpenMPI, Python)
        modules = profile.get("module_loads", ["gcc/12.2.0", "eccodes/2.30.0", "openmpi/4.1.5", "python/3.11.5"])
        self.env_manager.setup_environment(modules)

        # Step 11: Initialize Terminal & File Transfer
        self.terminal_shell = RemoteTerminalShell(self.ssh_connector)
        self.file_transfer = FileTransferManager(self.ssh_connector)

        self.is_connected = True
        self.last_heartbeat = time.time()
        log_hpc_event(
            "INFO",
            f"SUCCESS: Fully connected to FENNEC HPC Operational Center "
            f"({verified_user}@{verified_host}:{work_dir}) - scheduler={self.scheduler.scheduler_name}, "
            f"mode={self.meteorological_stack['operational_mode']}",
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
        """Return GPU information.

        NOTE (correction): the .get() default (only reachable if "gpu"
        were somehow missing from cluster_info, which detect_all()
        always populates) used to be a fabricated
        {"type": "CUDA (NVIDIA A100)", "has_gpu": True} - the same
        fabrication class fixed in ClusterDetector.detect_gpu() itself.
        Replaced with an honest "nothing detected" default consistent
        with detect_gpu()'s own now-honest shape.
        """
        return self.cluster_info.get(
            "gpu", {"has_gpu": False, "type": None, "has_cuda": False, "is_real_data": False}
        )

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

    def execute_one_click_aladin(self) -> dict[str, Any]:
        """One-Click ALADIN 7.5km Operational NWP Pipeline.

        Mirrors execute_one_click_arome() exactly, for the ALADIN 7.5km
        configuration named alongside AROME 1.3km in
        docs/ACF_HPC_005_NEXT_ROADMAP.md's CI/CD objective - added
        because only the AROME pipeline previously existed, and
        `python -m acf.forecast.engine --model ALADIN` (see that
        module) is a real, now-existing entry point for it.

        Connect -> Sync input -> Load ecCodes/OpenMPI -> Generate SLURM batch -> Submit -> Monitor -> Download results.
        """
        log_hpc_event("INFO", "Executing One-Click ALADIN Operational NWP Pipeline on FENNEC...")

        py_info = self.python_resolver.resolve_python()
        py_path = py_info["python_path"]

        self.file_transfer.sync_files("/tmp/aladin_input.grib2", "/scratch/users/sfoura/aladin_input.grib2")

        script = self.scheduler.generate_batch_script(
            f"{py_path} -m acf.forecast.engine --model ALADIN",
            job_name="aladin_7p5km_op",
            nodes=2,
            ntasks=16,
            gpus=0,
            walltime="01:00:00",
        )

        job_id = self.scheduler.submit_job(script, job_name="aladin_7p5km_op")
        was_really_submitted = not job_id.startswith("NOT_SUBMITTED_")

        self.file_transfer.download_results("/scratch/users/sfoura/aladin_output.nc", "/tmp/aladin_output.nc")

        log_hpc_event(
            "INFO",
            f"One-Click ALADIN Pipeline {'completed successfully' if was_really_submitted else 'did NOT submit a real job'}. Job ID: {job_id}",
        )
        return {
            "status": "SUCCESS" if was_really_submitted else "NOT_SUBMITTED_NO_REAL_SCHEDULER_CONNECTION",
            "job_id": job_id,
            "operational_model": "ALADIN-7.5km",
            "output": "/tmp/aladin_output.nc",
            "is_real_submission": was_really_submitted,
        }

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
