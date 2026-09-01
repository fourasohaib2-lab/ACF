"""
GPU Acceleration Engine Module (CUDA / Vulkan Compute)
"""

from typing import Any


class GPUPhysicsAccelerator:
    """Accélérateur GPU CUDA/Vulkan pour la résolution des équations aux dérivées partielles."""

    @classmethod
    def get_gpu_status(cls) -> dict[str, Any]:
        """
        NOTE (correction): this used to unconditionally claim a
        specific "NVIDIA A100 / H100 Tensor Core" device, "18.2 GB"
        VRAM, "19.5 TFLOPS" throughput and "CUDA_ACCELERATED" for
        every call, with 0 parameters and no real GPU probe - unlike
        hpc.simulation.gpu_solver.GPUSolver in the same package, which
        already honestly checks `import cupy` availability before
        claiming GPU acceleration. Now applies the same real check
        instead of a fabricated device profile.
        """
        try:
            import cupy as cp  # type: ignore
        except ImportError:
            cp = None

        if cp is not None:
            try:
                device = cp.cuda.Device()
                free_bytes, total_bytes = device.mem_info
                return {
                    "gpu_device": cp.cuda.runtime.getDeviceProperties(device.id)["name"].decode(),
                    "vram_allocated_gb": round((total_bytes - free_bytes) / 1e9, 2),
                    "compute_throughput_tflops": None,
                    "acceleration_status": "CUDA_ACCELERATED",
                    "is_real_data": True,
                }
            except cp.cuda.runtime.CUDARuntimeError:
                pass  # cupy installed but no CUDA device visible

        return {
            "gpu_device": None,
            "vram_allocated_gb": None,
            "compute_throughput_tflops": None,
            "acceleration_status": "NOT_ACCELERATED_NO_CUDA_DEVICE_CONNECTED",
            "is_real_data": False,
        }
