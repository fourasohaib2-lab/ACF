"""HPC Workflow Scheduler for 00, 06, 12, 18 UTC Forecast Cycles (ACF-HPC-104)."""

from acf.hpc_workflow.workflow import BaseWorkflow


class WorkflowScheduler:
    """Schedules 00UTC, 06UTC, 12UTC, and 18UTC forecast cycles."""

    def schedule_cycle(self, workflow: BaseWorkflow, cycle: str = "00UTC") -> bool:
        """Schedule forecast workflow cycle."""
        workflow.context.cycle = cycle
        return True
