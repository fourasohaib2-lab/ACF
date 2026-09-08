"""HPC Workflow Input & Environment Validator (ACF-HPC-104)."""

from acf.hpc_workflow.workflow_context import WorkflowContext
from acf.hpc_workflow.workflow_errors import WorkflowValidationError


class WorkflowValidator:
    """Validates context before running an operational workflow stage.

    NOTE (found, NOT changed - Physics Guard, flagged by
    `ruff --select ARG`): despite the "20 workflow stages" framing,
    validate_stage() below performs exactly one check (forecast cycle
    format) identically regardless of `stage` - it never actually
    branches on which of the 20 stages is being validated, so `stage`
    goes unused. WorkflowContext (workflow_id/model_name/cycle/
    forecast_length/status/job_id/progress/created_at/attributes) has
    no per-stage fields to validate against (e.g. no
    "observation_data_ready" for ASSIMILATION, no "output_files" for
    ARCHIVING) - inventing stage-specific requirements without a real
    spec to validate against would be fabricating validation rules,
    the same risk this session has avoided elsewhere. Zero test
    coverage or other callers beyond BaseWorkflow.run_stage() (verified
    via grep), so flagged rather than "fixed" with unverified rules.
    """

    def validate_stage(self, stage: str, context: WorkflowContext) -> bool:
        """Validate the forecast cycle format in context (the only check currently performed, for any stage)."""
        valid_cycles = ["00UTC", "06UTC", "12UTC", "18UTC", "00", "06", "12", "18"]
        if context.cycle not in valid_cycles:
            raise WorkflowValidationError(f"Invalid forecast cycle: {context.cycle}")
        return True
