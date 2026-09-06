"""
Atmospheric Complexity Framework (ACF)

HPC Slurm Batch Support Module
"""

from typing import Any


class SlurmSupport:
    """Générateur de scripts Slurm sbatch pour grappes de calcul HPC."""

    @classmethod
    def generate_slurm_script(cls) -> dict[str, Any]:
        """
        NOTE (correction, 2026-09-06 Tier E sweep - same pattern as
        this module's already-fixed CloudSupport.get_cloud_config()):
        no sbatch script is written to disk here, and nodes/
        tasks_per_node/partition are illustrative example values, not
        a report of any real cluster's actual configuration (see
        acf.hpc_connector for ACF's real, already-audited Slurm
        integration). No file write exists anywhere in this method.
        """
        return {
            "planned_slurm_script": "slurm/acf_hpc_run.sh",
            "example_nodes": 16,
            "example_tasks_per_node": 32,
            "example_partition": "hpc-gpu-cluster",
            "status": "NOT_GENERATED_NO_SCRIPT_WRITTEN",
            "is_real_data": False,
        }
