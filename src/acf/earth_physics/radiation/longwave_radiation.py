"""
Longwave Terrestrial Radiation Model (Stefan-Boltzmann F = sigma * T^4)
"""


class LongwaveRadiationModel:
    """Modèle de rayonnement infrarouge sortant (OLR)."""

    STEFAN_BOLTZMANN = 5.670374419e-8  # W/(m^2 K^4)

    @classmethod
    def blackbody_emittance(cls, temp_k: float, emissivity: float = 1.0) -> float:
        return emissivity * cls.STEFAN_BOLTZMANN * (temp_k**4)
