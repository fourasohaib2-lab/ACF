"""
Equation of State Module (P = rho * R * T)
"""


class IdealGasEquationOfState:
    """Équation d'état des gaz parfaits pour l'air sec et l'air humide."""

    R_DRY = 287.058

    @classmethod
    def density(cls, pressure_pa: float, temp_k: float) -> float:
        return pressure_pa / (cls.R_DRY * temp_k)
