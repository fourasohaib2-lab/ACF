"""HPC Workflow Registry & History Tracker (ACF-HPC-104)."""

from typing import Any

from acf.hpc_workflow.workflow_context import WorkflowContext


class WorkflowRegistry:
    """Registry maintaining active and registered workflow definitions."""

    def __init__(self) -> None:
        self.registry: dict[str, Any] = {}

    def register(self, name: str, workflow_cls: Any) -> None:
        """Register workflow class."""
        self.registry[name] = workflow_cls

    def get(self, name: str) -> Any | None:
        """Retrieve registered workflow class."""
        return self.registry.get(name)


class WorkflowHistory:
    """Tracks historical workflow execution runs and telemetry statistics."""

    def __init__(self) -> None:
        self.history: list[WorkflowContext] = []

    def record_run(self, context: WorkflowContext) -> None:
        """Record completed or failed workflow run context."""
        self.history.append(context)

    def get_runs(self) -> list[WorkflowContext]:
        """Return history list."""
        return self.history
