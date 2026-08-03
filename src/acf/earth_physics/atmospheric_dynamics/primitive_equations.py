"""
Atmospheric Primitive Equations Module
(Navier-Stokes Navier-Stokes for Atmosphere: du/dt, dv/dt, dp/dz = -rho*g)
"""

from typing import Dict


class AtmosphericPrimitiveEquations:
    """Équations primitives de la dynamique atmosphérique (Navier-Stokes en coordonnées de pression)."""

    @classmethod
    def solve_momentum(cls, u: float, v: float, f: float, dp_dx: float, rho: float = 1.225) -> Dict[str, float]:
        """Du/dt = f*v - (1/rho)*dp/dx."""
        du_dt = f * v - (1.0 / rho) * dp_dx
        return {"du_dt": du_dt}
