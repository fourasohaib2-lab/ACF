"""
Atmospheric Complexity Framework (ACF)

HPC Slurm Batch Support Module
"""

from typing import Any


class SlurmSupport:
    """Générateur de scripts Slurm sbatch pour grappes de calcul HPC."""

    @classmethod
    def generate_slurm_script(cls) -> dict[str, Any]:
        return {
            "slurm_script": "slurm/acf_hpc_run.sh",
            "nodes": 16,
            "tasks_per_node": 32,
            "partition": "hpc-gpu-cluster",
        }
