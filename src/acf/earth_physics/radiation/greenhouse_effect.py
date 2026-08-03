"""
Greenhouse Gas Forcing Model (CO2, CH4, N2O, O3, H2O)
"""

import math


class GreenhouseEffectModel:
    """Modèle de forçage radiatif des gaz à effet de serre (Myhre et al. formula)."""

    @classmethod
    def co2_radiative_forcing(cls, co2_ppm: float, co2_base_ppm: float = 280.0) -> float:
        """Delta F = 5.35 * ln(C / C0) W/m^2."""
        return 5.35 * math.log(co2_ppm / co2_base_ppm)
