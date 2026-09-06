"""
Atmospheric Complexity Framework (ACF)

Earthquake-Tsunami Solid Earth-Ocean Coupling Module (Phase 4)
"""


class EarthquakeTsunamiCouplingEngine:
    """
    Moteur de couplage entre la rupture sismique sous-marine et l'initialisation du tsunami.
    """

    @staticmethod
    def seafloor_uplift_energy_joules(seismic_moment_m0_nm: float, coupling_efficiency: float = 0.05) -> float:
        """Calcul de l'énergie de déplacement du fond marin transmise à la colonne d'eau.

        NOTE (found, NOT changed — Physics Guard, found during the
        post-model4d audit, 2026-09-06): the relationship itself
        (seafloor uplift energy scales with seismic moment M0) is
        physically sound, but the default coupling_efficiency=0.05 has
        no cited source in this module - it is not verified against a
        specific published tsunami-energy-partition study. It IS a
        caller-overridable keyword argument, not a hidden internal
        constant, which limits the blast radius. Left in place rather
        than inventing a "properly sourced" replacement number.
        """
        return seismic_moment_m0_nm * coupling_efficiency
