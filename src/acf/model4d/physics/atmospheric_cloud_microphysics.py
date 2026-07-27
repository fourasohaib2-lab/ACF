from dataclasses import dataclass


@dataclass
class CloudMicrophysicsState:
    liquid_water_content: float
    ice_content: float
    temperature: float
    droplet_radius: float
    ice_nuclei: float
    updraft_velocity: float


class AtmosphericCloudMicrophysics:
    """
    Simplified cloud microphysics model
    for ACF Model 4D physics engine.
    """

    def droplet_growth(self, state: CloudMicrophysicsState) -> float:
        """
        Liquid droplet growth by condensation.
        """

        return round(
            state.liquid_water_content
            * state.droplet_radius,
            2
        )

    def ice_crystal_formation(self, state: CloudMicrophysicsState) -> float:
        """
        Ice crystal nucleation process.
        """

        return round(
            state.ice_nuclei
            * abs(state.temperature) / 10,
            2
        )

    def bergeron_process(self, state: CloudMicrophysicsState) -> float:
        """
        Bergeron-Findeisen ice growth process.
        """

        return round(
            state.ice_content
            * state.liquid_water_content,
            2
        )

    def collision_coalescence(self, state: CloudMicrophysicsState) -> float:
        """
        Warm rain collision-coalescence.
        """

        return round(
            state.droplet_radius
            * state.updraft_velocity,
            2
        )

    def precipitation_efficiency(self, state: CloudMicrophysicsState) -> float:
        """
        Conversion efficiency from cloud water
        to precipitation.
        """

        return round(
            (
                state.liquid_water_content
                + state.ice_content
            )
            /
            10,
            2
        )

    def phase_transition(self, state: CloudMicrophysicsState) -> float:
        """
        Liquid/ice phase conversion.
        """

        return round(
            (
                state.liquid_water_content
                - state.ice_content
            )
            *
            state.ice_nuclei,
            2
        )

