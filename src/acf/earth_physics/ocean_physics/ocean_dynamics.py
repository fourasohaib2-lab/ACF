"""
Ocean Primitive Equations Module (Boussinesq approximation for Momentum, Heat, Salt)
"""


class OceanPrimitiveEquations:
    """Équations primitives de la dynamique océanique (Momentum, Salinité, Température)."""

    @classmethod
    def hydro_pressure_gradient(cls, rho_water: float, dz: float, g: float = 9.81) -> float:
        return rho_water * g * dz
