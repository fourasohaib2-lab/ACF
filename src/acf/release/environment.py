"""
Atmospheric Complexity Framework (ACF)

Production Environment Detector Module
"""

import os
import platform
import shutil
from typing import Any


class EnvironmentDetector:
    """Détecteur d'environnement d'exécution (Workstation, Slurm, Kubernetes, Cloud)."""

    @classmethod
    def detect_environment(cls) -> dict[str, Any]:
        """
        Détecte l'environnement d'exécution réel du processus courant.

        NOTE (correction): this used to unconditionally claim
        "HPC / CLOUD DISTRIBUTED" with slurm/kubernetes/gpu all True,
        regardless of the actual machine ACF is running on (0
        parameters, no real probing). Now genuinely probes: SLURM via
        the standard SLURM_JOB_ID env var (set by srun/sbatch),
        Kubernetes via the standard KUBERNETES_SERVICE_HOST env var
        (injected into every pod by the API server), and GPU presence
        via whether an `nvidia-smi` binary is on PATH (a real but
        imperfect signal - it detects an NVIDIA driver install, not
        necessarily a usable/free GPU; AMD/ROCm GPUs are not detected
        by this check).
        """
        slurm_detected = "SLURM_JOB_ID" in os.environ
        kubernetes_detected = "KUBERNETES_SERVICE_HOST" in os.environ
        gpu_detected = shutil.which("nvidia-smi") is not None

        if kubernetes_detected:
            execution_mode = "KUBERNETES"
        elif slurm_detected:
            execution_mode = "HPC_SLURM"
        else:
            execution_mode = "WORKSTATION"

        return {
            "os": f"{platform.system()} {platform.machine()}",
            "execution_mode": execution_mode,
            "slurm_detected": slurm_detected,
            "kubernetes_detected": kubernetes_detected,
            "gpu_detected": gpu_detected,
            "is_real_data": True,
        }
