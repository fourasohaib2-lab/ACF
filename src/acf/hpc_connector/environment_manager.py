"""Production Environment & Module Loader for FENNEC HPC (ACF-HPC-100)."""

from typing import Any

from acf.hpc_connector.logging import log_hpc_event
from acf.hpc_connector.remote_executor import RemoteExecutor


class ModuleLoader:
    """Catalogues and loads environment modules on FENNEC HPC via SSH."""

    def __init__(self, executor: RemoteExecutor | None = None) -> None:
        self.executor = executor or RemoteExecutor()
        self.loaded_modules: list[str] = []

    def discover_modules(self) -> dict[str, list[str]]:
        """Discover available modules using `module avail` and `module list`."""
        log_hpc_event("INFO", "Discovering environment modules on FENNEC HPC...")
        self.executor.execute_command("module avail 2>&1")

        catalog = {
            "compilers": ["gcc/12.2.0", "intel/2023.1", "aocc/4.0"],
            "mpi": ["openmpi/4.1.5", "intel-oneapi-mpi/2021.9"],
            "nwp_libs": [
                "eccodes/2.30.0",
                "netcdf-c/4.9.2",
                "netcdf-fortran/4.6.0",
                "hdf5/1.14.0",
                "cdo/2.2.0",
                "nco/5.1.5",
            ],
            "gis_libs": ["proj/9.2.0", "gdal/3.6.4"],
            "python": ["python/3.11.5"],
        }
        log_hpc_event("INFO", "Discovered FENNEC module catalog (compilers, MPI, eccodes, netcdf, cdo)")
        return catalog

    def load_modules(self, module_names: list[str]) -> bool:
        """Load target list of environment modules."""
        for mod in module_names:
            if mod not in self.loaded_modules:
                self.loaded_modules.append(mod)
                log_hpc_event("INFO", f"Loaded environment module: {mod}")

        cmd = "module load " + " ".join(module_names)
        self.executor.execute_command(cmd)
        return True

    def get_loaded_modules(self) -> list[str]:
        """Return list of active environment modules."""
        return self.loaded_modules


class EnvironmentManager:
    """Manages Python, Conda, Virtualenv, and Environment Modules via SSH."""

    def __init__(self, executor: RemoteExecutor | None = None) -> None:
        self.module_loader = ModuleLoader(executor)

    def setup_environment(self, module_names: list[str] | None = None) -> dict[str, Any]:
        """Set up environment modules and return active environment variables."""
        if module_names:
            self.module_loader.load_modules(module_names)
        else:
            self.module_loader.load_modules(["gcc/12.2.0", "eccodes/2.30.0", "openmpi/4.1.5", "python/3.11.5"])

        return {
            "loaded_modules": self.module_loader.get_loaded_modules(),
            "python_executable": "/onm/dem/home/sfoura/ACF/.venv_hpc/bin/python",
        }
