"""
Advection stencil operator (NumPy/CPU reference implementation).

NOTE (correction): this module and CUDAKernelManager's docstrings used
to claim a "Low-level CUDA kernel manager" that "Dispatch[es] CUDA
advection stencil operation[s]" - the implementation below is plain
vectorized NumPy (CPU), no CUDA kernel is compiled, launched, or even
referenced anywhere in this file (contrast with
hpc.simulation.gpu_solver.GPUSolver in the same package, which
genuinely dispatches to CuPy/CUDA when available and honestly falls
back to NumPy otherwise). Docstring-only fix: class/method names kept
for API compatibility, self.block_size kept as a declared target for
a future real CUDA dispatch, not a claim that one runs today.
"""

import numpy as np


class CUDAKernelManager:
    """NumPy/CPU reference implementation of the advection flux stencil (not a real CUDA dispatcher - see module docstring)."""

    def __init__(self) -> None:
        self.block_size = (16, 16)  # target CUDA block size for a future real GPU dispatch, unused by this CPU path

    def dispatch_advection_kernel(self, u: np.ndarray, v: np.ndarray, scalar: np.ndarray, dt: float) -> np.ndarray:
        """Compute one advection step on CPU via vectorized NumPy (not a real CUDA kernel dispatch).

        Args:
            u (np.ndarray): Eastward velocity.
            v (np.ndarray): Northward velocity.
            scalar (np.ndarray): Field to advect.
            dt (float): Timestep.

        Returns:
            np.ndarray: Updated scalar field after advection.
        """
        # Optimized vectorized 2D/3D stencil
        du_x = np.gradient(scalar, axis=-1)
        du_y = np.gradient(scalar, axis=-2)
        scalar_next = scalar - dt * (u * du_x + v * du_y)
        return scalar_next
