"""AROME Operational Workflow Package (ACF-HPC-104).

NOTE (correction — undisclosed no-op stubs, found during the
post-model4d audit, 2026-09-06): every one-method class below
(AROMERunner.run(), AROMEPreProcessor.preprocess(), AROMEExecution.
execute(), AROMEPostProcessor.postprocess(), AROMERestartManager.
checkpoint(), AROMEOutputManager.export()) unconditionally returned
`True`, and AROMEForecastCycle.cycle()/AROMEMonitoring.monitor()
unconditionally returned a fixed "00UTC"/"RUNNING" - none takes any
argument or does any real work (no real SLURM submission, no real
file I/O, no real process/queue check). The real, tested AROME
pipeline is `AROMEWorkflow` (this same package, delegating to
`BaseWorkflow`/`WorkflowExecutor`/`HPCConnectionManager` - a genuinely
different, already-audited code path) and `WorkflowEngine`
(workflow_engine.py) - these 8 classes are a separate, parallel set
with zero real callers anywhere in the codebase (verified via grep,
tests included). Kept (not deleted, per this session's standing rule)
but not wired to anything real here - inventing real SLURM/file-I/O
behavior for 8 unused classes without a real spec would itself be a
fabrication. Flagged rather than silently left as an undisclosed lie.
"""

from acf.hpc_workflow.arome.arome_workflow import AROMEWorkflow


class AROMEConfiguration:
    def __init__(self) -> None:
        self.resolution_km = 1.3
        self.domain = "Algerie_Nord"


class AROMERunner:
    def run(self) -> bool:
        """Unconditional stub - see package docstring. No real run performed."""
        return True


class AROMEPreProcessor:
    def preprocess(self) -> bool:
        """Unconditional stub - see package docstring. No real preprocessing performed."""
        return True


class AROMEExecution:
    def execute(self) -> bool:
        """Unconditional stub - see package docstring. No real execution performed."""
        return True


class AROMEPostProcessor:
    def postprocess(self) -> bool:
        """Unconditional stub - see package docstring. No real postprocessing performed."""
        return True


class AROMEForecastCycle:
    def cycle(self) -> str:
        """Unconditional stub - see package docstring. Not derived from any real clock/state."""
        return "00UTC"


class AROMERestartManager:
    def checkpoint(self) -> bool:
        """Unconditional stub - see package docstring. No real checkpoint written."""
        return True


class AROMEMonitoring:
    def monitor(self) -> str:
        """Unconditional stub - see package docstring. Not derived from any real job/queue state."""
        return "RUNNING"


class AROMEOutputManager:
    def export(self) -> bool:
        """Unconditional stub - see package docstring. No real export performed."""
        return True


__all__ = [
    "AROMEConfiguration",
    "AROMEExecution",
    "AROMEForecastCycle",
    "AROMEMonitoring",
    "AROMEOutputManager",
    "AROMEPostProcessor",
    "AROMEPreProcessor",
    "AROMERestartManager",
    "AROMERunner",
    "AROMEWorkflow",
]
