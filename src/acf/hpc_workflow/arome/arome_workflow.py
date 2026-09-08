"""AROME Operational Workflow (ACF-HPC-104)."""

from acf.hpc_workflow.workflow import BaseWorkflow


class AROMEWorkflow(BaseWorkflow):
    """AROME 1.3km Operational Forecasting Workflow Subsystem."""

    def __init__(self, workflow_id: str = "arome_op", cycle: str = "00UTC", forecast_length: str = "24h") -> None:
        super().__init__(workflow_id=workflow_id, model_name="AROME", cycle=cycle, forecast_length=forecast_length)
