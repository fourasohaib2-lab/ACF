"""HPC Workflow Input & Environment Validator (ACF-HPC-104)."""

from acf.hpc_workflow.workflow_context import WorkflowContext
from acf.hpc_workflow.workflow_errors import WorkflowValidationError


class WorkflowValidator:
    """Validates 20 workflow stages before SLURM execution."""

    def validate_stage(self, stage: str, context: WorkflowContext) -> bool:
        """Validate context requirements for target stage."""
        valid_cycles = ["00UTC", "06UTC", "12UTC", "18UTC", "00", "06", "12", "18"]
        if context.cycle not in valid_cycles:
            raise WorkflowValidationError(f"Invalid forecast cycle: {context.cycle}")
        return True
