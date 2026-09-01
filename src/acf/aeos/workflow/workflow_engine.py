"""
Atmospheric Complexity Framework (ACF)

AEOS Scientific Workflow Engine Module (Phase 5)
(WorkflowEngine, ScientificWorkflow: Forecast, Assimilation, Emergency, Report, AI, Digital Twin Workflows)
"""

from dataclasses import dataclass


@dataclass
class ScientificWorkflow:
    """Description d'un workflow scientifique complet AEOS."""

    workflow_id: str
    name: str
    workflow_type: str  # Forecast, Assimilation, Data Ingestion, Emergency, Report, AI, Digital Twin
    steps_count: int
    status: str


class WorkflowEngine:
    """
    Moteur d'orchestration des workflows scientifiques autonomes.
    """

    @classmethod
    def get_registered_workflows(cls) -> list[ScientificWorkflow]:
        """
        Retourne la liste des grands workflows opérationnels d'AEOS.

        NOTE (correction): workflow_id/name/workflow_type/steps_count
        are a genuine static catalog of the workflow types ACF is
        designed to support (same kind of catalog as
        aeos.services.service_registry.ServiceRegistry.SERVICES), but
        status used to claim a specific fabricated per-instance runtime
        state ("COMPLETED"/"ACTIVE"/"STANDBY") for each - no real
        workflow orchestration run, transition, or tracking exists
        anywhere in this codebase (aeos.scheduler.task_scheduler.
        TaskScheduler, the only task runner in this package, does not
        actually execute anything either - see its own NOTE). Not
        fabricated.
        """
        return [
            ScientificWorkflow(
                "WF-01", "Global 10-Day Coupled Neural Forecast", "Forecast Workflow", 6, "NOT_TRACKED_NO_ORCHESTRATION_RUN"
            ),
            ScientificWorkflow(
                "WF-02", "WIGOS 4D-Var Data Assimilation Cycle", "Assimilation Workflow", 8, "NOT_TRACKED_NO_ORCHESTRATION_RUN"
            ),
            ScientificWorkflow(
                "WF-03", "Multi-Hazard Crisis Emergency Response", "Emergency Workflow", 5, "NOT_TRACKED_NO_ORCHESTRATION_RUN"
            ),
            ScientificWorkflow(
                "WF-04", "Planetary Digital Twin State Update", "Digital Twin Workflow", 4, "NOT_TRACKED_NO_ORCHESTRATION_RUN"
            ),
        ]
