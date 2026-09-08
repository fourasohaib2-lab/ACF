"""HPC Workflow Telemetry & SLURM Queue Monitor (ACF-HPC-104)."""

from acf.hpc_connector.connection_manager import HPCConnectionManager
from acf.hpc_workflow.workflow_context import WorkflowContext
from acf.hpc_workflow.workflow_status import WorkflowStatus


class WorkflowMonitor:
    """Monitors real-time SLURM job state, CPU/RAM telemetry, and forecast progress."""

    def __init__(self, hpc_manager: HPCConnectionManager | None = None) -> None:
        self.hpc_manager = hpc_manager or HPCConnectionManager()

    def check_workflow_status(self, context: WorkflowContext) -> WorkflowStatus:
        """Check active status of workflow SLURM job."""
        if not context.job_id:
            return WorkflowStatus.INITIALIZING

        status_str = self.hpc_manager.scheduler.get_job_status(context.job_id)
        if status_str in ["RUNNING", "COMPLETING"]:
            context.status = WorkflowStatus.RUNNING
        elif status_str == "COMPLETED":
            context.status = WorkflowStatus.COMPLETED
        elif status_str in ["FAILED", "CANCELLED", "TIMEOUT"]:
            context.status = WorkflowStatus.FAILED

        return context.status
