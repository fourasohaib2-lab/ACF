"""HPC Workflow Scheduler for 00, 06, 12, 18 UTC Forecast Cycles (ACF-HPC-104)."""

from typing import Any

from acf.hpc_workflow.workflow import BaseWorkflow


class WorkflowScheduler:
    """Schedules 00UTC, 06UTC, 12UTC, and 18UTC forecast cycles.

    NOTE (correction — undisclosed no-op, found during the post-model4d
    audit, 2026-09-06): schedule_cycle() used to only ever set
    workflow.context.cycle and unconditionally return True - no real
    timer/cron/scheduler mechanism exists anywhere in this class to
    actually trigger execution at the requested cycle time; calling it
    has zero effect on when (or whether) `workflow` ever actually runs.
    Zero real callers anywhere in the codebase beyond this package's
    own re-export shim (verified via grep). Same undisclosed-no-op
    pattern already found and fixed elsewhere in this exact package
    (workflow_notifications.py's send_notification(),
    workflow_archive.py's archive_results()/cleanup_scratch()). The
    real, useful side effect (labeling the workflow's cycle) is kept;
    it no longer claims scheduling happened.
    """

    def schedule_cycle(self, workflow: BaseWorkflow, cycle: str = "00UTC") -> dict[str, Any]:
        """Label `workflow` with `cycle` (no real scheduling mechanism connected - see class docstring)."""
        workflow.context.cycle = cycle
        return {
            "cycle": cycle,
            "scheduled": False,
            "status": "NOT_SCHEDULED_NO_TIMER_CONNECTED",
        }
