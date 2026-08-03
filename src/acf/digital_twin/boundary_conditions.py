"""
Atmospheric Complexity Framework (ACF)

Boundary Conditions Manager Module
"""

from typing import Any, Dict


class BoundaryConditionsManager:
    """Gestionnaire des conditions aux limites du modèle planétaire."""

    @classmethod
    def get_boundary_conditions(cls) -> Dict[str, Any]:
        return {"solar_constant_w_m2": 1361.0, "ghg_forcing": "ACTIVE", "status": "BOUNDARIES_SET"}
