"""Universal HPC Python Resolver & Environment Bootstrapper (ACF-HPC-101)."""

import os
import re
import sys
from typing import Any

from acf.hpc_connector.logging import log_hpc_event
from acf.hpc_connector.remote_executor import RemoteExecutor


class PythonResolver:
    """Automatically resolves the best Python interpreter across compute nodes and HPC clusters."""

    def __init__(self, executor: RemoteExecutor | None = None) -> None:
        self.executor = executor or RemoteExecutor()

    def discover_python_modules(self) -> list[str]:
        """Dynamically scan `module avail` for Python modules without hardcoding names."""
        log_hpc_event("INFO", "Scanning cluster environment modules for Python installations...")
        res = self.executor.execute_command("module avail 2>&1")
        output = res.get("stdout", "") + res.get("stderr", "")

        found_modules: list[str] = []
        pattern = re.compile(r"\b(Python|python|py3)/?[\w\.-]*", re.IGNORECASE)

        for line in output.splitlines():
            matches = pattern.findall(line)
            if matches:
                # Find full token matching the pattern
                tokens = line.split()
                for t in tokens:
                    if re.search(r"\b(Python|python|py3)", t, re.IGNORECASE):
                        clean_mod = t.strip()
                        if clean_mod and clean_mod not in found_modules:
                            found_modules.append(clean_mod)

        if not found_modules:
            # Fallback candidate patterns discovered across FENNEC, Jean Zay, ECMWF, and University HPCs
            found_modules = ["Python/3.11.5", "python/3.11", "Python/3.10", "Python/3.9", "python3"]

        log_hpc_event("INFO", f"Discovered Python cluster modules: {found_modules}")
        return found_modules

    def discover_python_executables(self) -> list[str]:
        """Discover Python executable candidates on the system."""
        candidates = [
            "python3.12",
            "python3.11",
            "python3.10",
            "python3.9",
            "python3.8",
            "python3",
            "python",
        ]

        # Check active virtual environment
        if "VIRTUAL_ENV" in os.environ:
            candidates.insert(0, os.path.join(os.environ["VIRTUAL_ENV"], "bin", "python"))

        # Check standard ACF HPC virtual environment paths
        acf_venv = "/onm/dem/home/sfoura/ACF/.venv_hpc/bin/python"
        if os.path.exists(acf_venv):
            candidates.insert(0, acf_venv)

        return candidates

    def _parse_version_tuple(self, ver_str: str) -> tuple:
        """Parse version string into a numeric tuple for comparison."""
        try:
            parts = [int(p) for p in re.findall(r"\d+", ver_str)[:3]]
            return tuple(parts) if parts else (0, 0, 0)
        except Exception:
            return (0, 0, 0)

    def resolve_python(self, preferred_module: str | None = None) -> dict[str, Any]:
        """Resolve the optimal Python executable and environment module."""
        log_hpc_event("INFO", "Resolving optimal Python interpreter for HPC execution...")

        best_resolution: dict[str, Any] = {
            "python_path": sys.executable,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "python_module": "",
            "is_virtualenv": hasattr(sys, "real_prefix")
            or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix),
            "is_valid": True,
        }

        # 1. Inspect Python Modules
        modules = self.discover_python_modules()
        selected_module = preferred_module or (modules[0] if modules else "")

        # 2. Test Executables via RemoteExecutor
        executables = self.discover_python_executables()
        highest_version = (0, 0, 0)

        for exe in executables:
            cmd = f"{exe} -c \"import sys; print(f'{{sys.version_info.major}}.{{sys.version_info.minor}}.{{sys.version_info.micro}}')\""
            res = self.executor.execute_command(cmd)

            if res.get("exit_code") == 0:
                ver_str = res.get("stdout", "").strip()
                if "REMOTE STDOUT" in ver_str:
                    ver_str = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

                ver_tuple = self._parse_version_tuple(ver_str)

                if ver_tuple > highest_version:
                    highest_version = ver_tuple

                    # Resolve absolute path
                    res_path = self.executor.execute_command(f"which {exe} 2>/dev/null || echo '{exe}'")
                    abs_path = res_path.get("stdout", "").strip()
                    if "REMOTE STDOUT" in abs_path or not abs_path:
                        abs_path = exe if not exe.startswith("python") else sys.executable

                    best_resolution = {
                        "python_path": abs_path,
                        "python_version": ver_str if ver_str else f"{ver_tuple[0]}.{ver_tuple[1]}.{ver_tuple[2]}",
                        "python_module": selected_module,
                        "is_virtualenv": ".venv" in abs_path or "venv" in abs_path,
                        "is_valid": True,
                    }

        log_hpc_event(
            "INFO",
            f"Python Resolved: Executable={best_resolution['python_path']} (Version {best_resolution['python_version']}, Module={best_resolution['python_module']})",
        )
        return best_resolution

    def print_python_info(self) -> None:
        """CLI diagnostic summary output."""
        info = self.resolve_python()
        print("\n========================================================")
        print("     ACF UNIVERSAL HPC PYTHON RESOLVER DIAGNOSTIC       ")
        print("========================================================")
        print(f"Python Executable      : {info['python_path']}")
        print(f"Python Version         : {info['python_version']}")
        print(f"Python Module          : {info['python_module'] if info['python_module'] else 'None (Direct Binary)'}")
        print(
            f"Virtualenv Status      : {'Active (' + info['python_path'] + ')' if info['is_virtualenv'] else 'System / Module Python'}"
        )
        print(
            f"Compute Node Status    : {'COMPATIBLE (Python >= 3.8)' if self._parse_version_tuple(info['python_version']) >= (3, 8) else 'INCOMPATIBLE (Legacy Python < 3.8)'}"
        )
        print("========================================================\n")


def main() -> None:
    """CLI entry point for `python -m acf.hpc_connector.python_resolver`."""
    resolver = PythonResolver()
    resolver.print_python_info()


if __name__ == "__main__":
    main()
