"""HPC Workflow Executor executing SLURM jobs via HPC Connector (ACF-HPC-104)."""

from typing import Any

from acf.hpc_connector.connection_manager import HPCConnectionManager
from acf.hpc_workflow.workflow import BaseWorkflow
from acf.hpc_workflow.workflow_status import WorkflowStatus


class WorkflowExecutor:
    """Executes workflows over SLURM HPC Cluster using HPCConnectionManager."""

    def __init__(self, hpc_manager: HPCConnectionManager | None = None) -> None:
        self.hpc_manager = hpc_manager or HPCConnectionManager()

    def execute_workflow(self, workflow: BaseWorkflow) -> dict[str, Any]:
        """Execute workflow stages and submit to SLURM scheduler."""
        workflow.run_stage("Initialization")
        workflow.run_stage("SLURM Generation")

        # Submit job to SLURM
        job = self.hpc_manager.submit_simulation_job(
            command=f"python -m acf.forecast.engine --model {workflow.context.model_name}",
            job_name=f"acf_{workflow.context.model_name.lower()}_run",
            nodes=4,
            ntasks=32,
            gpus=4,
        )

        # NOTE (correction): status used to be unconditionally SUCCESS/
        # RUNNING regardless of what submit_simulation_job() -> JobManager
        # .submit_job() actually reported - that call already honestly
        # distinguishes a real SLURM submission from one that never
        # reached a real scheduler (see its "is_real_submission" field),
        # but this wrapper was silently discarding that signal. Not
        # fabricated.
        was_really_submitted = bool(job.get("is_real_submission", False))
        workflow.context.job_id = job.get("job_id") or ""
        workflow.context.status = WorkflowStatus.RUNNING if was_really_submitted else WorkflowStatus.FAILED
        workflow.run_stage("Queue Monitoring")
        return {
            "status": "SUCCESS" if was_really_submitted else job.get("status", "NOT_SUBMITTED_NO_REAL_SCHEDULER_CONNECTION"),
            "job_id": workflow.context.job_id,
            "is_real_submission": was_really_submitted,
        }
