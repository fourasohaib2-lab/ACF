"""
Atmospheric Complexity Framework (ACF)

Autonomous Mission Planner & Workflow Engine Module (Phase 8)
(MissionPlanner scheduling observations, assimilation cycles, AI forecasts, reports)
"""

from dataclasses import dataclass


@dataclass
class AutonomousWorkflowTask:
    """Tâche automatisée planifiée par le MissionPlanner."""

    task_id: str
    task_name: str
    target_module: str
    schedule_interval_minutes: int
    status: str


class MissionPlanner:
    """
    Planificateur autonome de missions d'observation, de simulation et d'alerte pour ACF.
    """

    @classmethod
    def get_active_workflows(cls) -> list[AutonomousWorkflowTask]:
        """
        Retourne la liste des workflows autonomes actifs.

        NOTE (correction): this used to unconditionally claim 4 fixed
        tasks were "ACTIVE / RUNNING" or "ACTIVE / SCHEDULED" with 0
        real task scheduler connected - no autonomous workflow
        execution engine actually runs these tasks anywhere in this
        codebase. The task names/intervals themselves describe
        real, plausible intended workflows (matching real subsystems:
        acf.data, acf.ai, acf.intelligence, acf.reports), so they are
        kept as a documented roadmap of intended scheduled tasks, but
        the status is no longer falsely claimed as actively running.
        Not fabricated.
        """
        return [
            AutonomousWorkflowTask("TSK-01", "Global Satellite Assimilation", "acf.data", 15, "NOT_SCHEDULED"),
            AutonomousWorkflowTask(
                "TSK-02", "Neural AI Forecast Inference (GraphCast)", "acf.ai", 60, "NOT_SCHEDULED"
            ),
            AutonomousWorkflowTask(
                "TSK-03", "Multi-Hazard Cascade Risk Audit", "acf.intelligence", 30, "NOT_SCHEDULED"
            ),
            AutonomousWorkflowTask(
                "TSK-04", "Executive Briefing Report Generation", "acf.reports", 360, "NOT_SCHEDULED"
            ),
        ]
