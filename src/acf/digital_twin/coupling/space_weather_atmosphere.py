"""
Atmospheric Complexity Framework (ACF)

Space Weather-Thermosphere / Atmosphere Coupling Module (Phase 4)
"""


class SpaceWeatherAtmosphereCouplingEngine:
    """
    Moteur de couplage entre l'activité géomagnétique (Kp/Dst) et le chauffage thermosphérique par effet Joule.
    """

    @staticmethod
    def joule_heating_rate_gw(kp_index: float) -> float:
        """Calcul du chauffage Joule thermosphérique global Q_joule = 15.0 * Kp² (en GigaWatts)."""
        return 15.0 * (kp_index**2)
