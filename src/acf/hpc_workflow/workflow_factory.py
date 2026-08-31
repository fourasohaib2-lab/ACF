"""HPC Workflow Factory (ACF-HPC-104)."""

import uuid

from acf.hpc_workflow.workflow import BaseWorkflow


class WorkflowFactory:
    """Factory instantiating AROME or ALADIN operational workflows."""

    def create_workflow(
        self, model_name: str = "AROME", cycle: str = "00UTC", forecast_length: str = "24h"
    ) -> BaseWorkflow:
        """Create workflow instance."""
        wf_id = f"wf_{model_name.lower()}_{uuid.uuid4().hex[:8]}"
        return BaseWorkflow(workflow_id=wf_id, model_name=model_name, cycle=cycle, forecast_length=forecast_length)
