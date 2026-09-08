"""ALADIN Operational Workflow Package (ACF-HPC-104).

NOTE (correction — undisclosed no-op stubs, found during the
post-model4d audit, 2026-09-06): same pattern as
acf.hpc_workflow.arome's own package docstring - every one-method
class below unconditionally returns a fixed True/"00UTC"/"RUNNING"
with no argument and no real work performed. The real, tested ALADIN
pipeline is `ALADINWorkflow` (this same package) and `WorkflowEngine`
(workflow_engine.py); these 5 classes have zero real callers anywhere
in the codebase (verified via grep, tests included). Kept, not deleted,
but flagged rather than silently left as an undisclosed lie.
"""

from acf.hpc_workflow.aladin.aladin_workflow import ALADINWorkflow


class ALADINConfiguration:
    def __init__(self) -> None:
        self.resolution_km = 7.5
        self.domain = "Algerie_Global"


class ALADINRunner:
    def run(self) -> bool:
        """Unconditional stub - see package docstring. No real run performed."""
        return True


class ALADINForecastCycle:
    def cycle(self) -> str:
        """Unconditional stub - see package docstring. Not derived from any real clock/state."""
        return "00UTC"


class ALADINRestartManager:
    def checkpoint(self) -> bool:
        """Unconditional stub - see package docstring. No real checkpoint written."""
        return True


class ALADINMonitoring:
    def monitor(self) -> str:
        """Unconditional stub - see package docstring. Not derived from any real job/queue state."""
        return "RUNNING"


class ALADINPostProcessor:
    def postprocess(self) -> bool:
        """Unconditional stub - see package docstring. No real postprocessing performed."""
        return True


class ALADINOutputManager:
    def export(self) -> bool:
        """Unconditional stub - see package docstring. No real export performed."""
        return True


__all__ = [
    "ALADINConfiguration",
    "ALADINForecastCycle",
    "ALADINMonitoring",
    "ALADINOutputManager",
    "ALADINPostProcessor",
    "ALADINRestartManager",
    "ALADINRunner",
    "ALADINWorkflow",
]
