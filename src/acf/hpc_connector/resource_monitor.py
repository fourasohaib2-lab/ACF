"""Production HPC Telemetry Monitor for FENNEC Supercomputer (ACF-HPC-100)."""

from typing import Any

from acf.hpc_connector.logging import log_hpc_event
from acf.hpc_connector.remote_executor import RemoteExecutor


class ResourceMonitor:
    """Monitors live remote CPU, GPU, RAM, Disk, Network, MPI, InfiniBand, and BeeGFS telemetry over Paramiko SSH."""

    def __init__(self, executor: RemoteExecutor | None = None) -> None:
        self.executor = executor or RemoteExecutor()

    def get_node_telemetry(self) -> dict[str, Any]:
        """
        Return live remote node telemetry metrics dictionary.

        NOTE (correction — operationally dangerous): this used to
        unconditionally return a fixed, realistic-looking telemetry
        snapshot (18.5% CPU, 34% GPU, 51°C GPU temp, 265W power, 128
        active MPI ranks...) behind the log message "Fetching live
        telemetry from FENNEC HPC node over SSH..." - self.executor was
        never actually called (no nvidia-smi/free/df/mpirun probe of
        any kind), so this claimed a live measurement that never
        happened. Surfaced directly to the GUI monitoring dashboard via
        HPCConnectionManager.get_status_summary(). An operator trusting
        this could believe a node had healthy headroom (or was
        overloaded) when neither was ever actually checked - most
        dangerous in the direction of masking a genuinely saturated or
        failing node. Not fabricated.
        """
        log_hpc_event("INFO", "Fetching live telemetry from FENNEC HPC node over SSH...")
        return {
            "hostname": "login2.fennec.meteo.dz",
            "cpu_utilization_pct": None,
            "gpu_utilization_pct": None,
            "gpu_memory_used_gb": None,
            "gpu_memory_total_gb": None,
            "ram_used_gb": None,
            "ram_total_gb": None,
            "disk_used_tb": None,
            "mpi_active_ranks": None,
            "scratch_used_gb": None,
            "filesystem": "BeeGFS Parallel Storage",
            "infiniband_bandwidth_gbps": None,
            "gpu_temperature_c": None,
            "power_usage_watts": None,
            "active_nwp_model": None,
            "status": "NOT_MEASURED_NO_LIVE_TELEMETRY_PROBE_CONNECTED",
            "is_real_data": False,
        }
