"""
Atmospheric Complexity Framework (ACF)

Boundary Conditions Manager Module
"""

from typing import Any


class BoundaryConditionsManager:
    """Gestionnaire des conditions aux limites du modèle planétaire."""

    @classmethod
    def get_boundary_conditions(cls) -> dict[str, Any]:
        """
        NOTE (correction): solar_constant_w_m2 is a genuine physical
        constant (the standard TSI value, ~1361 W/m2 - kept as-is),
        but "ghg_forcing": "ACTIVE" and "status": "BOUNDARIES_SET"
        claimed real boundary conditions were actively driving a
        running simulation - no simulation/coupled solver is connected
        here (0 parameters). Not fabricated.
        """
        return {
            "solar_constant_w_m2": 1361.0,
            "ghg_forcing": "NOT_SET_NO_SIMULATION_CONNECTED",
            "status": "NOT_SET_NO_SIMULATION_CONNECTED",
            "is_real_data": False,
        }
