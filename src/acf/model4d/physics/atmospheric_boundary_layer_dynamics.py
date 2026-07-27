"""
Atmospheric Boundary Layer Dynamics
Sprint 9.13

Module:
- turbulence
- sensible heat flux
- latent heat flux
- vertical mixing
- surface-atmosphere exchange
"""


from dataclasses import dataclass



@dataclass
class BoundaryLayerState:
    """
    Atmospheric boundary layer state variables.
    """

    wind_speed: float
    temperature_difference: float
    humidity_difference: float
    surface_roughness: float
    stability: float = 1.0




class AtmosphericBoundaryLayerDynamics:
    """
    Simplified atmospheric boundary layer physics model.
    """



    def __init__(self):

        self.name = "Atmospheric Boundary Layer Dynamics"



    def turbulence_intensity(
        self,
        state: BoundaryLayerState
    ) -> float:
        """
        Turbulence intensity estimation.
        """

        value = (
            state.wind_speed
            *
            state.surface_roughness
            *
            0.1
        )

        return round(value, 3)




    def sensible_heat_flux(
        self,
        state: BoundaryLayerState
    ) -> float:
        """
        Sensible heat exchange between surface and atmosphere.
        """

        value = (
            state.wind_speed
            *
            state.temperature_difference
            *
            0.1
        )

        return round(value, 3)




    def latent_heat_flux(
        self,
        state: BoundaryLayerState
    ) -> float:
        """
        Latent heat flux due to humidity transport.
        """

        value = (
            state.wind_speed
            *
            state.humidity_difference
            *
            state.surface_roughness
            *
            0.2666666667
        )

        return round(value, 3)




    def vertical_mixing(
        self,
        state: BoundaryLayerState
    ) -> float:
        """
        Vertical turbulent mixing coefficient.
        """

        value = (
            state.wind_speed
            *
            state.surface_roughness
            *
            0.4
            /
            state.stability
        )

        return round(value, 3)




    def surface_exchange(
        self,
        state: BoundaryLayerState
    ) -> float:
        """
        Total surface-atmosphere exchange.

        Includes:
        - sensible heat
        - latent heat
        - surface correction
        """

        sensible = self.sensible_heat_flux(state)

        latent = self.latent_heat_flux(state)

        surface_correction = 1.0


        value = (
            sensible
            +
            latent
            -
            surface_correction
        )


        return round(value, 3)
