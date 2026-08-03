"""
Water Phase Changes & Latent Heat Module
"""


class WaterPhaseChanges:
    """Changements de phase de l'eau (Chaleur latente d'évaporation, sublimation, fusion)."""

    LATENT_HEAT_VAPORIZATION = 2.501e6  # J/kg
    LATENT_HEAT_FUSION = 3.337e5  # J/kg

    @classmethod
    def latent_heat_release(cls, condensed_mass_kg: float) -> float:
        return condensed_mass_kg * cls.LATENT_HEAT_VAPORIZATION
