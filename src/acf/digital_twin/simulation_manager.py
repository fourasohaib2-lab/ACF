"""
Atmospheric Complexity Framework (ACF)

Digital Twin Simulation Manager Module
"""

from typing import Any


class SimulationManager:
    """Gestionnaire d'exécution des simulations numériques du Jumeau Numérique."""

    @classmethod
    def execute_simulation(cls, sim_name: str = "Global 100-Year Climate") -> dict[str, Any]:
        """
        NOTE (correction): sim_name was genuinely echoed, but this used
        to unconditionally claim "execution_status": "RUNNING_COMPUTE"
        together with "progress_pct": 100.0 - self-contradictory on its
        face (100% progress on a run supposedly still "RUNNING") - with
        0 parameters and no real simulation engine ever invoked.
        """
        return {
            "simulation": sim_name,
            "execution_status": "NOT_EXECUTED_NO_SIMULATION_ENGINE_CONNECTED",
            "progress_pct": None,
            "is_real_data": False,
        }
