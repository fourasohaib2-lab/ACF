"""ACF SURFEX Operational Subsystem Package (ACF-HPC-105).

NOTE (correction — fabricated success/status/telemetry/results,
whole-package pattern, same as engine.py's own already-fixed
run_simulation()): every class below used to unconditionally return a
fixed, plausible-looking value regardless of any real HPC scheduler,
job, or physics backend being connected - SurfexScheduler.schedule()
always claimed job ID "17216", SurfexMonitor.check() always claimed
"RUNNING" (even for a job that failed, finished, or was never
submitted), SurfexTelemetry.get_metrics() always claimed the exact
same {"cpu": 15.2, "ram_gb": 12.4}, and SurfexDiagnostics.compute()
always claimed the exact same {"skin_temp_k": 298.15,
"snow_depth_m": 0.45} for any run. None of this is wired to
engine.py's real (if honestly "not connected") HPCConnectionManager.
Fixed to honestly report that instead of a specific fake value or a
fake success flag, matching the "no fabricated success" convention
already used in acf.models.base_model.BaseWeatherModel.
"""

from acf.surfex.engine import SurfexEngine


class SurfexRunner:
    def run(self) -> bool:
        return False


class SurfexConfiguration:
    def __init__(self) -> None:
        self.mode = "operational"


class SurfexWorkflow:
    def run(self) -> bool:
        return False


class SurfexManager:
    def execute(self) -> bool:
        return False


class SurfexScheduler:
    def schedule(self) -> str:
        raise NotImplementedError(
            "SurfexScheduler.schedule() needs a real HPC scheduler connection to "
            "submit to - none is connected here (see engine.py's HPCConnectionManager "
            "for the real, honestly-disclosed submission path). Previously returned "
            "a hard-coded fake job ID '17216' regardless of what was submitted; "
            "removed rather than left silently wrong."
        )


class SurfexMonitor:
    def check(self) -> str:
        return "UNKNOWN_NO_REAL_MONITORING_CONNECTED"


class SurfexTelemetry:
    def get_metrics(self) -> dict:
        raise NotImplementedError(
            "SurfexTelemetry.get_metrics() needs a real HPC telemetry feed to read "
            "from - none is connected. Previously returned a hard-coded fake "
            "{'cpu': 15.2, 'ram_gb': 12.4} regardless of any actual job; removed "
            "rather than left silently wrong."
        )


class SurfexValidator:
    def validate(self) -> bool:
        return False


class SurfexLogger:
    def log(self, msg: str) -> None:
        pass


class SurfexArchive:
    @staticmethod
    def archive() -> bool:
        return False


class SurfexRestart:
    @staticmethod
    def checkpoint() -> bool:
        return False


class SurfexHistory:
    @staticmethod
    def history() -> list:
        return []


class SurfexDiagnostics:
    @staticmethod
    def compute() -> dict:
        raise NotImplementedError(
            "SurfexDiagnostics.compute() needs a real SURFEX solver run to diagnose "
            "from - none is connected. Previously returned a hard-coded fake "
            "{'skin_temp_k': 298.15, 'snow_depth_m': 0.45} regardless of any actual "
            "run; removed rather than left silently wrong."
        )


class SurfexException(Exception):
    pass


class SurfexEvent:
    pass


class SurfexResources:
    pass


class SurfaceTypes:
    pass


class SurfexPhysics:
    pass


class SurfexForcing:
    pass


class SurfexOutputs:
    pass


class SurfexUtilities:
    pass


__all__ = [
    "SurfaceTypes",
    "SurfexArchive",
    "SurfexConfiguration",
    "SurfexDiagnostics",
    "SurfexEngine",
    "SurfexEvent",
    "SurfexException",
    "SurfexForcing",
    "SurfexHistory",
    "SurfexLogger",
    "SurfexManager",
    "SurfexMonitor",
    "SurfexOutputs",
    "SurfexPhysics",
    "SurfexResources",
    "SurfexRestart",
    "SurfexRunner",
    "SurfexScheduler",
    "SurfexTelemetry",
    "SurfexUtilities",
    "SurfexValidator",
    "SurfexWorkflow",
]
