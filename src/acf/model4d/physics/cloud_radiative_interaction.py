"""
ACF - Atmospheric Complexity Framework
Cloud Radiative Interaction Physics Module

Simulation simplifiée des interactions entre nuages,
rayonnement solaire et rayonnement infrarouge terrestre.
"""


class CloudRadiativeInteractionPhysics:
    """
    Modèle physique des interactions radiatives nuage-atmosphère.
    """

    @staticmethod
    def solar_reflection(incoming_radiation, cloud_albedo):
        """
        Calcul du rayonnement solaire réfléchi par les nuages.

        Parameters
        ----------
        incoming_radiation : float
            Rayonnement solaire incident (W/m²)

        cloud_albedo : float
            Albédo du nuage (0-1)

        Returns
        -------
        float
            Rayonnement réfléchi
        """
        return round(incoming_radiation * cloud_albedo, 10)

    @staticmethod
    def solar_absorption(incoming_radiation, cloud_albedo):
        """
        Calcul du rayonnement solaire absorbé.
        """
        return round(
            incoming_radiation * (1 - cloud_albedo),
            10
        )

    @staticmethod
    def infrared_trapping(emitted_radiation, cloud_emissivity):
        """
        Effet de serre des nuages.

        Plus l'émissivité est élevée,
        plus le rayonnement IR est retenu.
        """
        return round(
            emitted_radiation * cloud_emissivity,
            10
        )

    @staticmethod
    def cloud_radiative_forcing(
        shortwave_effect,
        longwave_effect
    ):
        """
        Forçage radiatif total des nuages.

        CRF = effet courte longueur d'onde
              + effet longue longueur d'onde
        """
        return round(
            shortwave_effect + longwave_effect,
            10
        )

    @staticmethod
    def cloud_temperature_response(
        surface_temperature,
        cloud_cover_fraction
    ):
        """
        Influence de la couverture nuageuse
        sur la température apparente.
        """
        return round(
            surface_temperature *
            (1 - 0.1 * cloud_cover_fraction),
            10
        )

    @staticmethod
    def outgoing_longwave_balance(
        emitted_energy,
        trapped_energy
    ):
        """
        Bilan énergétique infrarouge sortant.
        """
        return round(
            emitted_energy - trapped_energy,
            10
        )
