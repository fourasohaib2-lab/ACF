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
        """Calcul du chauffage Joule thermosphérique global Q_joule = 15.0 * Kp² (en GigaWatts).

        NOTE (found, NOT changed — Physics Guard, found during the
        post-model4d audit, 2026-09-06): a quadratic Kp-to-hemispheric-
        power-input relationship is a real, published class of
        empirical model in the ionosphere/thermosphere literature, but
        the specific coefficient 15.0 used here has no citation in
        this module and was not independently verified against a named
        source. Left in place rather than inventing a "properly
        sourced" replacement coefficient.
        """
        return 15.0 * (kp_index**2)
