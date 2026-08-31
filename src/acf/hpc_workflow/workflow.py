"""Base Operational Workflow Class (ACF-HPC-104)."""

from acf.hpc_workflow.workflow_context import WorkflowContext
from acf.hpc_workflow.workflow_validator import WorkflowValidator


class BaseWorkflow:
    """Base operational workflow class handling 20 operational stages."""

    def __init__(
        self, workflow_id: str, model_name: str = "AROME", cycle: str = "00UTC", forecast_length: str = "24h"
    ) -> None:
        self.context = WorkflowContext(
            workflow_id=workflow_id, model_name=model_name, cycle=cycle, forecast_length=forecast_length
        )
        self.validator = WorkflowValidator()

    def run_stage(self, stage_name: str) -> bool:
        """Run operational workflow stage."""
        self.validator.validate_stage(stage_name, self.context)
        self.context.progress.current_stage = stage_name
        return True
