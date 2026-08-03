"""
Thermodynamic Equations Module (First Law of Thermodynamics)
"""


class ThermodynamicEquations:
    """Équations de la thermodynamique atmosphérique (Theta, Theta_e, CP, CV)."""

    R_DRY = 287.058  # J / (kg K)
    CP_DRY = 1004.64  # J / (kg K)

    @classmethod
    def potential_temperature(cls, temp_k: float, pressure_pa: float, p0_pa: float = 100000.0) -> float:
        return temp_k * ((p0_pa / pressure_pa) ** (cls.R_DRY / cls.CP_DRY))
