"""Production Environment & Module Loader for FENNEC HPC (ACF-HPC-100)."""

import re
from typing import Any

from acf.hpc_connector.logging import log_hpc_event
from acf.hpc_connector.remote_executor import RemoteExecutor

# NOTE: ACF's genuinely known/configured FENNEC module catalog - kept as
# a labeled fallback (see discover_modules()) when no real remote
# transport is available, not fabricated content.
_KNOWN_FENNEC_MODULE_CATALOG: dict[str, list[str]] = {
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


class ModuleLoader:
    """Catalogues and loads environment modules on FENNEC HPC via SSH."""

    def __init__(self, executor: RemoteExecutor | None = None) -> None:
        self.executor = executor or RemoteExecutor()
        self.loaded_modules: list[str] = []

    def discover_modules(self) -> dict[str, Any]:
        """Discover available modules using `module avail`.

        NOTE (correction): used to run `module avail` and then
        completely discard its result, returning a hardcoded catalog
        as if it had genuinely been discovered. Now genuinely parses
        real `module avail` output when a live remote transport is
        connected; falls back to the known FENNEC catalog (clearly
        labeled, not fabricated content) otherwise.
        """
        log_hpc_event("INFO", "Discovering environment modules on FENNEC HPC...")
        res = self.executor.execute_command("module avail 2>&1")
        is_real = not res.get("is_simulated", True)

        if is_real:
            stdout = res.get("stdout", "") + res.get("stderr", "")
            discovered = sorted(set(re.findall(r"[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+", stdout)))
            log_hpc_event("INFO", f"Discovered {len(discovered)} real environment module(s).")
            return {"available_modules": discovered, "is_real_data": True}

        log_hpc_event(
            "WARNING",
            "No real remote transport connected - returning the known FENNEC module catalog as an "
            "unverified fallback, not live detection.",
        )
        return {**_KNOWN_FENNEC_MODULE_CATALOG, "is_real_data": False}

    def load_modules(self, module_names: list[str]) -> bool:
        """Load target list of environment modules.

        NOTE (correction): used to append every requested module name to
        self.loaded_modules and return True unconditionally, regardless
        of whether the `module load` command genuinely succeeded
        remotely - the executor's result was fired off and discarded.
        get_loaded_modules()'s own docstring promises "active" modules,
        not merely requested ones. A real HPC job proceeding on the
        false assumption that eccodes/openmpi were loaded (when the
        load silently failed) would crash far downstream instead of
        failing fast here. Now only marks modules loaded when the
        combined `module load` command was genuinely confirmed (a real,
        non-simulated, exit_code 0 remote execution) - `module load`
        doesn't report clean per-module success/failure in its own
        output, so success/failure is tracked for the whole requested
        batch together, the same granularity the command itself has.
        """
        cmd = "module load " + " ".join(module_names)
        res = self.executor.execute_command(cmd)
        success = not res.get("is_simulated", True) and res.get("exit_code", 1) == 0

        if success:
            for mod in module_names:
                if mod not in self.loaded_modules:
                    self.loaded_modules.append(mod)
                    log_hpc_event("INFO", f"Loaded environment module: {mod}")
        else:
            log_hpc_event("WARNING", f"Could not confirm module load for: {module_names}")

        return success

    def get_loaded_modules(self) -> list[str]:
        """Return list of genuinely-confirmed-active environment modules."""
        return self.loaded_modules


class EnvironmentManager:
    """Manages Python, Conda, Virtualenv, and Environment Modules via SSH."""

    def __init__(self, executor: RemoteExecutor | None = None) -> None:
        self.module_loader = ModuleLoader(executor)

    def setup_environment(self, module_names: list[str] | None = None) -> dict[str, Any]:
        """Set up environment modules and return active environment variables.

        NOTE (correction): "loaded_modules" used to reflect merely-
        requested module names regardless of whether the load was
        confirmed (see ModuleLoader.load_modules()'s own NOTE), and
        python_executable was a hardcoded specific path presented as
        fact regardless of whether it actually exists on the connected
        system - it's ACF's genuinely configured FENNEC venv path (the
        same value PythonResolver.discover_python_executables() only
        ever treats as one unverified candidate among several), not
        fabricated, but stating it here as if confirmed was misleading.
        load_success now genuinely reflects whether the module load was
        confirmed; python_executable_candidate is documented as the
        configured candidate path it is, not a verified fact - see
        PythonResolver for a genuinely resolved, remote-verified
        interpreter.
        """
        requested = module_names or ["gcc/12.2.0", "eccodes/2.30.0", "openmpi/4.1.5", "python/3.11.5"]
        load_success = self.module_loader.load_modules(requested)

        return {
            "loaded_modules": self.module_loader.get_loaded_modules(),
            "load_success": load_success,
            "python_executable_candidate": "/onm/dem/home/sfoura/ACF/.venv_hpc/bin/python",
        }
