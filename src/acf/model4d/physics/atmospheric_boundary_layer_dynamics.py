"""
ACF Model4D Physics

Atmospheric Boundary Layer Dynamics Module

Sprint 9.13

Simplified representation of:
- boundary layer height
- turbulence
- surface-atmosphere exchanges
"""

from dataclasses import dataclass


@dataclass
class BoundaryLayerState:
    """
    Atmospheric boundary layer parameters.
    """

    surface_temperature_difference: float
    wind_speed: float
    surface_roughness: float
    moisture_flux: float
    mixing_coefficient: float


class AtmosphericBoundaryLayerDynamics:
    """
    Simplified atmospheric boundary layer model.
    """


    def boundary_layer_height(
        self,
        state: BoundaryLayerState
    ) -> float:
        """
        Estimate boundary layer height.

        Height increases with:
        - surface heating
        - turbulence
        """

        value = (
            state.surface_temperature_difference
            * state.wind_speed
            * 10
        )

        return round(value, 6)


    def turbulence_intensity(
        self,
        state: BoundaryLayerState
    ) -> float:
        """
        Estimate turbulence intensity.
        """

        value = (
            state.wind_speed
            * state.surface_roughness
        )

        return round(value, 6)


    def heat_flux_exchange(
        self,
        state: BoundaryLayerState
    ) -> float:
        """
        Estimate surface-atmosphere heat exchange.

        Depends on:
        - moisture
        - mixing
        """

        value = (
            state.moisture_flux
            * state.mixing_coefficient
        )

        return round(value, 6)


    def boundary_layer_state(
        self,
        state: BoundaryLayerState
    ) -> str:
        """
        Classify boundary layer regime.
        """

        turbulence = self.turbulence_intensity(state)

        if turbulence > 1:
            return "turbulent_boundary_layer"

        return "stable_boundary_layer"
