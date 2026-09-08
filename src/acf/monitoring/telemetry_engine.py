"""
Atmospheric Complexity Framework (ACF)

Operational Telemetry & System Hardware Engine Module (Phase 2)
(TelemetryEngine monitoring CPU, RAM, GPU, Network, Cluster, AEOS health, latency, throughput)
"""

from typing import Any

try:
    import psutil

    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False


class TelemetryEngine:
    """
    Moteur de télémétrie matérielle et logicielle pour le système HPC et la grappe distribuée d'ACF.
    """

    @classmethod
    def collect_telemetry(cls) -> dict[str, Any]:
        """
        Collecte l'intégralité de la télémétrie opérationnelle du système.

        NOTE (correction): this used to unconditionally claim a full
        battery of specific fabricated numbers (14.2% CPU, 8.4 GB RAM,
        32.5% GPU, 18.2 GB VRAM, 10.5 Gbps network, 16 cluster nodes,
        "100% HEALTHY" AEOS, 0.85ms latency, 60 FPS) with 0 parameters
        and no real hardware probe. Now reports real host CPU/RAM
        usage (via psutil, if installed - optional-import pattern
        used elsewhere this session) and honestly declines to claim
        GPU/cluster/AEOS/network/render metrics that have no real
        probe connected here.
        """
        if not _PSUTIL_AVAILABLE:
            return {
                "cpu_usage_pct": None,
                "ram_usage_gb": None,
                "system_status": "UNKNOWN_PSUTIL_NOT_INSTALLED",
                "is_real_data": False,
            }
        cpu_pct = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        return {
            "cpu_usage_pct": cpu_pct,
            "ram_usage_gb": round(mem.used / 1e9, 2),
            "gpu_usage_pct": None,
            "gpu_memory_used_gb": None,
            "network_throughput_gbps": None,
            "storage_io_mbps": None,
            "cluster_nodes_active": None,
            "aeos_service_health": "NOT_TRACKED_NO_HEALTH_PROBE_CONNECTED",
            "average_latency_ms": None,
            "frames_per_second": None,
            "system_status": "HOST_CPU_RAM_ONLY_OTHER_METRICS_NOT_CONNECTED",
            "is_real_data": True,
        }
