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
        """Calcul de l'énergie de déplacement du fond marin transmise à la colonne d'eau."""
        return seismic_moment_m0_nm * coupling_efficiency
