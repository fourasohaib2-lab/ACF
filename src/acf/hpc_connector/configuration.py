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

    def get_cluster_profile(self, profile_name: str = "fennec") -> dict[str, Any]:
        """
        Retrieve profile configuration dictionary for target cluster.

        NOTE (correction — operationally dangerous): this used to
        silently substitute an ARBITRARY different real cluster's full
        profile (next(iter(profiles.values()))) whenever the requested
        profile_name wasn't found in config/hpc.yaml's cluster_profiles
        - and the default profile_name itself was "university_hpc",
        which does not exist there (only "fennec" does; the actual
        University HPC profile lives in a separate, unrelated file,
        config/hpc_profiles/University_HPC.yaml, never read by this
        class). In practice this meant the default no-argument call
        (used by HPCConnectionManager.connect(), this same package)
        always silently resolved to the real production FENNEC cluster
        (hostname, SSH username, working directory all genuine) instead
        of honestly failing to find "university_hpc" - a caller
        requesting a specific cluster by name could silently connect to
        an entirely different one. Fixed: the default now matches what
        is actually configured ("fennec", consistent with this whole
        class/package being built specifically for FENNEC), and an
        unmatched profile_name now honestly returns {} instead of a
        different cluster's real connection details.
        """
        profiles = self.config.get("cluster_profiles", {})
        return profiles.get(profile_name, {})
