"""Meteorological Operational Model & Library Detector for FENNEC Supercomputer (ACF-HPC-100).

NOTE (correction - operationally dangerous, same class as
ClusterDetector's own NOTE): detect_meteorological_stack() used to
fabricate "detection" in three compounding ways:
1. Every shell command embedded its OWN guaranteed-success fallback
   (`which arome ... || echo 'AROME_FOUND'`) - when the real binary
   genuinely wasn't found, the shell's own `echo` ran instead, printing
   text containing the exact substring being searched for and exiting
   0, so the command could never actually report "not found".
2. Even independent of that, the Python-side check
   `"AROME" in stdout or exit_code == 0` treated ANY successful shell
   invocation (including the guaranteed-success echo above) as
   detection - doubly self-defeating.
3. has_canari/has_odb/has_eccodes were hardcoded True with zero
   detection attempted at all, eccodes_version was a hardcoded
   "2.30.0" (the grib_dump command's own result wasn't even captured
   into a variable), and models_detected was a fixed 5-item list
   returned regardless of what has_arome/has_aladin/has_surfex/
   has_bator actually resolved to.
Every field is now genuinely derived from a real (non-simulated)
command's actual exit code, with no shell-embedded fallback biasing
the result toward "found".
"""

from typing import Any

from acf.hpc_connector.logging import log_hpc_event
from acf.hpc_connector.remote_executor import RemoteExecutor


class AromeAladinDetector:
    """Detects ALADIN, AROME, SURFEX, BATOR, CANARI, ODB, ECCODES, and ECMWF tools on FENNEC HPC."""

    def __init__(self, executor: RemoteExecutor) -> None:
        self.executor = executor

    @staticmethod
    def _is_real(res: dict[str, Any]) -> bool:
        """True only if execute_command() genuinely ran remotely (not the offline-fallback placeholder)."""
        return not res.get("is_simulated", True)

    def _which(self, binary: str) -> bool:
        """True only if a real remote `which` genuinely found the binary (exit_code 0)."""
        res = self.executor.execute_command(f"which {binary} 2>/dev/null")
        return self._is_real(res) and res.get("exit_code") == 0

    def detect_meteorological_stack(self) -> dict[str, Any]:
        """Perform automatic discovery of operational NWP models and libraries."""
        log_hpc_event("INFO", "Detecting ALADIN/AROME/SURFEX meteorological stack on FENNEC...")

        has_arome = self._which("arome") or self._which("MASTERODB")
        has_aladin = self._which("aladin")
        has_surfex = self._which("surfex")
        has_bator = self._which("bator")
        has_canari = self._which("canari")
        has_odb = self._which("odb_tools") or self._which("odbtogrib")
        has_ecflow = self._which("ecflow_client")

        res_eccodes = self.executor.execute_command("grib_dump --version 2>/dev/null")
        has_eccodes = self._is_real(res_eccodes) and res_eccodes.get("exit_code") == 0
        eccodes_version = res_eccodes.get("stdout", "").strip() if has_eccodes else None

        operational_mode = "STANDARD_NWP"
        if has_arome:
            operational_mode = "AROME_OPERATIONAL_MODE"
        elif has_aladin:
            operational_mode = "ALADIN_OPERATIONAL_MODE"

        models_detected = []
        if has_arome:
            models_detected.append("AROME")
        if has_aladin:
            models_detected.append("ALADIN")
        if has_surfex:
            models_detected.append("SURFEX")
        if has_bator:
            models_detected.append("BATOR")
        if has_canari:
            models_detected.append("CANARI")

        log_hpc_event(
            "INFO",
            f"Meteorological Stack Detection Complete: Mode={operational_mode}, AROME={has_arome}, ALADIN={has_aladin}, SURFEX={has_surfex}",
        )

        return {
            "operational_mode": operational_mode,
            "has_arome": has_arome,
            "has_aladin": has_aladin,
            "has_surfex": has_surfex,
            "has_bator": has_bator,
            "has_canari": has_canari,
            "has_odb": has_odb,
            "has_eccodes": has_eccodes,
            "has_ecflow": has_ecflow,
            "eccodes_version": eccodes_version,
            "models_detected": models_detected,
        }
