"""
Atmospheric Complexity Framework (ACF)

Production Dependency Validator Module
"""

import importlib.metadata
import importlib.util
import sys
from typing import Any


class DependencyValidator:
    """Validateur des dépendances matérielles et logicielles de production."""

    @classmethod
    def _check_package(cls, import_name: str, dist_name: str | None = None) -> str:
        if importlib.util.find_spec(import_name) is None:
            return "NOT_INSTALLED"
        try:
            version = importlib.metadata.version(dist_name or import_name)
            return f"{version} PRESENT"
        except importlib.metadata.PackageNotFoundError:
            return "PRESENT_VERSION_UNKNOWN"

    @classmethod
    def validate_all_dependencies(cls) -> dict[str, Any]:
        """
        NOTE (correction): this used to unconditionally claim every
        dependency PASSED, including "cuda: 12.4 PASS" and "mpi:
        OpenMPI 5.0 PASS" - false in most environments (this session's
        own environment has neither a GPU-enabled torch install nor
        mpi4py, verified earlier). Now genuinely checks each package
        via importlib (find_spec + real installed version), and
        honestly reports CUDA/MPI as NOT_INSTALLED where no
        torch.cuda / mpi4py is actually importable, instead of a
        fabricated PASS.
        """
        results: dict[str, Any] = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "numpy": cls._check_package("numpy"),
            "scipy": cls._check_package("scipy"),
            "netcdf4": cls._check_package("netCDF4", "netCDF4"),
            "grib_eccodes": cls._check_package("eccodes"),
        }

        if importlib.util.find_spec("torch") is not None:
            import torch  # type: ignore

            results["cuda"] = "AVAILABLE" if torch.cuda.is_available() else "TORCH_INSTALLED_NO_CUDA"
        else:
            results["cuda"] = "NOT_INSTALLED"

        results["mpi"] = "AVAILABLE" if importlib.util.find_spec("mpi4py") is not None else "NOT_INSTALLED"

        all_core_present = all(
            not str(v).startswith("NOT_INSTALLED") for k, v in results.items() if k in ("numpy", "scipy")
        )
        results["overall_status"] = "CORE_DEPENDENCIES_PRESENT" if all_core_present else "MISSING_CORE_DEPENDENCIES"
        results["is_real_data"] = True
        return results
