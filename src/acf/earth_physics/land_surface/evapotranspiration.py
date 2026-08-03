"""
Evapotranspiration & Latent Heat Flux Model (Penman-Monteith)
"""


class EvapotranspirationModel:
    """Modèle d'évapotranspiration potentielle et réelle (Équation de Penman-Monteith)."""

    @classmethod
    def potential_evapotranspiration_mm_day(cls, net_radiation_wm2: float, temp_c: float) -> float:
        return max(0.0, net_radiation_wm2 * 0.035 + (temp_c * 0.1))
