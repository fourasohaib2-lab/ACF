"""ALADIN Operational Workflow (ACF-HPC-104)."""

from acf.hpc_workflow.workflow import BaseWorkflow


class ALADINWorkflow(BaseWorkflow):
    """ALADIN 7.5km Operational Forecasting Workflow Subsystem."""

    def __init__(self, workflow_id: str = "aladin_op", cycle: str = "00UTC", forecast_length: str = "72h") -> None:
        super().__init__(workflow_id=workflow_id, model_name="ALADIN", cycle=cycle, forecast_length=forecast_length)
