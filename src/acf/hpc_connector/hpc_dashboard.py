"""
Atmospheric Complexity Framework (ACF)

HPC CONNECTOR - Operations Center Dashboard Backend (ACF-HPC-003)

Provides aggregated status, health score calculation, and JSON serialization for ESOC GUI.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from acf.hpc_connector.hpc_monitor import HPCMonitor


class HPCDashboard:
    """
    Backend service aggregating HPC cluster metrics and health indicators for ESOC GUI.
    """

    def __init__(self, monitor: HPCMonitor | None = None) -> None:
        """
        Initialize HPCDashboard with an optional HPCMonitor instance.
        """
        self.monitor = monitor if monitor else HPCMonitor()
        self._cached_summary: dict[str, Any] = {}
        self._last_refresh: float = 0.0

    def refresh(self) -> dict[str, Any]:
        """
        Refreshes all cluster metrics from HPCMonitor and returns updated summary.
        """
        health = self.monitor.get_cluster_health()
        partitions = self.monitor.get_partition_status()
        node_health = self.monitor.get_node_health()
        jobs = self.monitor.list_jobs()
        cpu = self.monitor.get_cpu_usage()
        memory = self.monitor.get_memory_usage()
        stats = self.monitor.get_slurm_statistics()
        score = self.health_score()

        self._cached_summary = {
            "timestamp": time.time(),
            "cluster_health": health,
            "partitions": partitions,
            "nodes": node_health,
            "jobs": jobs,
            "cpu": cpu,
            "memory": memory,
            "slurm_statistics": stats,
            "health_score": score,
        }
        self._last_refresh = time.time()
        return self._cached_summary

    def summary(self) -> dict[str, Any]:
        """
        Returns cached summary or performs a refresh if empty.
        """
        if not self._cached_summary:
            return self.refresh()
        return self._cached_summary

    def health_score(self) -> float:
        """
        Calculates cluster health score from 0.0 (CRITICAL) to 100.0 (EXCELLENT).

        NOTE (correction): `cpu.get("cpu_load_pct", 50.0)` used to
        silently substitute a fabricated "moderate load" 50.0% whenever
        HPCMonitor had no real CPU data (no real scheduler backend
        connected - see hpc_monitor.py's NOTE (correction) docstring).
        Since HPCMonitor.get_cpu_usage() now honestly reports
        `cpu_load_pct: None` in that case instead of a fake number, this
        crashed on `None > 90.0`. Fixed to skip the CPU-load penalty
        entirely when the load is genuinely unknown, rather than
        crashing or assuming either a high or moderate load. The overall
        100.0 baseline in that case reflects "no known problems
        detected" rather than "verified excellent" - callers wanting to
        distinguish the two should check the `connected` flag already
        present in HPCMonitor.get_cluster_health()'s return (included in
        refresh()'s "cluster_health" field), not this bare float alone.
        """
        c_status = self.monitor.cluster_status()
        total_nodes = c_status.get("idle_nodes", 0) + c_status.get("allocated_nodes", 0) + c_status.get("down_nodes", 0)
        down_nodes = c_status.get("down_nodes", 0)

        score = 100.0

        # Penalize for down nodes
        if total_nodes > 0 and down_nodes > 0:
            score -= (down_nodes / total_nodes) * 50.0

        # Penalize for high CPU load (> 90%) - only when genuinely known.
        cpu = self.monitor.get_cpu_usage()
        cpu_load = cpu.get("cpu_load_pct")
        if cpu_load is not None and cpu_load > 90.0:
            score -= 15.0

        return max(0.0, min(100.0, round(score, 1)))

    def export_json(self, filepath: str | None = None) -> str:
        """
        Exports the current HPC dashboard summary to a JSON string or file.
        """
        data = self.summary()
        json_str = json.dumps(data, indent=2)

        if filepath:
            out_path = Path(filepath)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json_str, encoding="utf-8")

        return json_str
