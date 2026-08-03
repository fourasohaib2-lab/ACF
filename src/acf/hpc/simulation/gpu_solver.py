"""GPU solver acceleration layer using CuPy or NumPy fallback."""

from typing import Any
import numpy as np

try:
    import cupy as cp  # type: ignore

    HAS_CUPY = True
except ImportError:
    cp = None
    HAS_CUPY = False


class GPUSolver:
    """GPU acceleration interface for atmospheric & oceanic tensor stencils."""

    def __init__(self, use_gpu: bool = True) -> None:
        self.gpu_enabled = use_gpu and HAS_CUPY

    def to_device(self, array: np.ndarray) -> Any:
        """Transfer NumPy array to GPU memory if CuPy is available."""
        if self.gpu_enabled:
            return cp.asarray(array)
        return array

    def to_host(self, array: Any) -> np.ndarray:
        """Transfer GPU array back to CPU host memory."""
        if self.gpu_enabled and hasattr(array, "get"):
            return array.get()
        return np.asarray(array)

    def accelerated_matmul(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Execute GPU matrix multiplication or CPU fallback."""
        a_dev = self.to_device(a)
        b_dev = self.to_device(b)

        if self.gpu_enabled:
            c_dev = cp.matmul(a_dev, b_dev)
        else:
            c_dev = np.matmul(a_dev, b_dev)

        return self.to_host(c_dev)
