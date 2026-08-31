"""HPC Configuration Manager (ACF-HPC-001)."""

import os
from typing import Any

import yaml

from acf.hpc_connector.logging import log_hpc_event


class HPCConfiguration:
    """Manages HPC cluster profiles, execution modes, and yaml configurations."""

    def __init__(self, config_path: str = "config/hpc.yaml") -> None:
        self.config_path = config_path
        self.config: dict[str, Any] = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration dictionary from YAML file if available."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict):
                        log_hpc_event("INFO", f"Loaded HPC configuration from {self.config_path}")
                        return data
            except Exception as e:
                log_hpc_event("WARNING", f"Failed to parse {self.config_path}: {e}")
        return self._default_config()

    def _default_config(self) -> dict[str, Any]:
        """Return fallback HPC configuration dictionary."""
        return {
            "execution_mode": "hybrid",
            "local_profile": {
                "hostname": "local_workstation",
                "cpu_cores": 16,
                "gpu_available": True,
                "scratch_dir": "/tmp/acf_scratch",
            },
            "cluster_profiles": {
                "default_cluster": {
                    "hostname": "cluster.local",
                    "scheduler": "slurm",
                    "partition": "gpu",
                    "default_nodes": 2,
                    "scratch_dir": "/scratch/acf",
                }
            },
            "auto_sync": {"enabled": True, "interval_seconds": 30},
            "security": {"ssh_key_path": "~/.ssh/id_rsa"},
        }

    def get_execution_mode(self) -> str:
        """Return active execution mode (local, cluster, hybrid, gpu, mpi, distributed)."""
        return self.config.get("execution_mode", "hybrid")

    def get_cluster_profile(self, profile_name: str = "university_hpc") -> dict[str, Any]:
        """Retrieve profile configuration dictionary for target cluster."""
        profiles = self.config.get("cluster_profiles", {})
        return profiles.get(profile_name, next(iter(profiles.values())) if profiles else {})
