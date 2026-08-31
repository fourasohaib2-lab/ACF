"""
Atmospheric Complexity Framework (ACF)

Digital Twin Experiment Manager Module (Phase 10)
"""

from typing import Any


class ExperimentManager:
    """Gestionnaire des expériences numériques et des bacs à sable du Jumeau Numérique."""

    @classmethod
    def create_experiment(
        cls, exp_id: str = "EXP-2026-001", parameters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        NOTE (correction): exp_id/parameters were genuinely echoed, but
        duration_years/results_summary/uncertainty_range/status used to
        unconditionally claim a fixed "100"-year "Experiment Initialized
        and Run Complete" with "±0.25 K" uncertainty for ANY exp_id or
        parameters, with no real digital-twin simulation ever run. Not
        fabricated.
        """
        if parameters is None:
            parameters = {"co2_doubling": True, "sasi_active": False}
        return {
            "experiment_id": exp_id,
            "parameters": parameters,
            "duration_years": None,
            "results_summary": None,
            "uncertainty_range": None,
            "status": "NOT_EXECUTED_NO_SIMULATION_RUN_CONNECTED",
            "is_real_data": False,
        }
