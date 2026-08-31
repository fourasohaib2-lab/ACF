"""
Atmospheric Complexity Framework (ACF)

Performance Profiler Engine Module (Phase 13)
(PerformanceProfiler measuring CPU, RAM, GPU, Threads, MPI, Cluster, Execution time, Latency)
"""

import threading
import time
from typing import Any

try:
    import psutil  # type: ignore

    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False


class PerformanceProfiler:
    """
    Profileur de performance système et d'empreinte mémoire pour le Master Framework ACF.
    """

    @classmethod
    def profile_framework(cls) -> dict[str, Any]:
        """
        Retourne la télémétrie réelle de performance système (via psutil).

        NOTE (correction): this used to return fixed fake numbers
        (12.4% CPU, 4.2GB RAM, 16.0GB GPU memory, 64 threads, "HIGH
        PERFORMANCE / OPTIMAL") regardless of actual system state -
        same fake-stub pattern as this session's other findings. Now
        reports REAL measurements via psutil when it's installed (it
        is NOT a declared pyproject.toml dependency, so this degrades
        gracefully rather than crashing where it's absent) for
        CPU/RAM/threads. GPU memory and MPI process count are honestly
        reported as unavailable rather than fabricated, since no GPU
        library (torch/cupy) or mpi4py is installed in this
        environment to query them from.
        """
        start = time.perf_counter()
        if _PSUTIL_AVAILABLE:
            cpu_pct = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            ram_used_gb = mem.used / (1024**3)
            ram_available_gb = mem.available / (1024**3)
            ram_pct = mem.percent
        else:
            cpu_pct = None
            ram_used_gb = ram_available_gb = ram_pct = None
        elapsed = time.perf_counter() - start

        gpu_available = False
        gpu_memory_gb = None
        try:
            import torch  # type: ignore

            gpu_available = torch.cuda.is_available()
            if gpu_available:
                gpu_memory_gb = torch.cuda.memory_allocated() / (1024**3)
        except ImportError:
            pass

        try:
            from mpi4py import MPI  # type: ignore

            mpi_procs = MPI.COMM_WORLD.Get_size()
        except ImportError:
            mpi_procs = 1  # no MPI runtime active -> genuinely running as 1 process

        if not _PSUTIL_AVAILABLE:
            status = "UNKNOWN_PSUTIL_NOT_INSTALLED"
        elif cpu_pct < 50 and ram_pct < 80:
            status = "NORMAL"
        elif cpu_pct < 85 and ram_pct < 95:
            status = "ELEVATED"
        else:
            status = "HIGH_LOAD"

        return {
            "cpu_utilization_pct": cpu_pct,
            "ram_used_gb": ram_used_gb,
            "ram_available_gb": ram_available_gb,
            "ram_utilization_pct": ram_pct,
            "gpu_available": gpu_available,
            "gpu_memory_allocated_gb": gpu_memory_gb,
            "active_threads": threading.active_count(),
            "mpi_procs": mpi_procs,
            "measurement_time_sec": elapsed,
            "performance_status": status,
            "is_real_data": _PSUTIL_AVAILABLE,
        }
