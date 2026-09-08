"""HPC Workflow Manager (ACF-HPC-104)."""

from typing import Any

from acf.hpc_workflow.workflow import BaseWorkflow
from acf.hpc_workflow.workflow_executor import WorkflowExecutor
from acf.hpc_workflow.workflow_monitor import WorkflowMonitor
from acf.hpc_workflow.workflow_registry import WorkflowHistory


class WorkflowManager:
    """Manages workflow submission, monitoring, and historical tracking."""

    def __init__(self) -> None:
        self.executor = WorkflowExecutor()
        self.monitor = WorkflowMonitor()
        self.history = WorkflowHistory()

    def run_workflow(self, workflow: BaseWorkflow) -> dict[str, Any]:
        """Execute workflow and record run in history."""
        res = self.executor.execute_workflow(workflow)
        self.history.record_run(workflow.context)
        return res
