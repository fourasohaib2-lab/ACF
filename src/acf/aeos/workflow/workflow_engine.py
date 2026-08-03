"""
Atmospheric Complexity Framework (ACF)

AEOS Scientific Workflow Engine Module (Phase 5)
(WorkflowEngine, ScientificWorkflow: Forecast, Assimilation, Emergency, Report, AI, Digital Twin Workflows)
"""

from dataclasses import dataclass
from typing import List


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
    def get_registered_workflows(cls) -> List[ScientificWorkflow]:
        """Retourne la liste des grands workflows opérationnels d'AEOS."""
        return [
            ScientificWorkflow("WF-01", "Global 10-Day Coupled Neural Forecast", "Forecast Workflow", 6, "COMPLETED"),
            ScientificWorkflow("WF-02", "WIGOS 4D-Var Data Assimilation Cycle", "Assimilation Workflow", 8, "ACTIVE"),
            ScientificWorkflow("WF-03", "Multi-Hazard Crisis Emergency Response", "Emergency Workflow", 5, "STANDBY"),
            ScientificWorkflow("WF-04", "Planetary Digital Twin State Update", "Digital Twin Workflow", 4, "COMPLETED"),
        ]
