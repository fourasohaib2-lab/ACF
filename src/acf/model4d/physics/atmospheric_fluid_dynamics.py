"""
Atmospheric Fluid Dynamics
ACF Model4D Physics Module
"""

from dataclasses import dataclass
import math


@dataclass
class FluidDynamicsState:
    temperature: float
    pressure: float
    density: float
    wind_u: float
    wind_v: float
    vertical_velocity: float
    vorticity: float
    divergence: float
    altitude: float
    coriolis_parameter: float



class AtmosphericFluidDynamics:
    """
    Atmospheric fluid dynamics diagnostic engine
    for ACF Model4D.
    """


    def horizontal_wind_speed(self, state: FluidDynamicsState):
        """
        Horizontal wind magnitude.
        """

        speed = math.sqrt(
            state.wind_u ** 2 +
            state.wind_v ** 2
        )

        return round(speed, 2)



    def wind_direction(self, state: FluidDynamicsState):
        """
        Wind direction in degrees.
        """

        direction = math.degrees(
            math.atan2(
                state.wind_v,
                state.wind_u
            )
        )

        if direction < 0:
            direction += 360

        return round(direction, 1)



    def horizontal_advection(self, state: FluidDynamicsState):
        """
        Horizontal thermal advection diagnostic.
        """

        value = (
            state.wind_u *
            state.temperature *
            0.001
        )

        return round(value, 2)



    def vertical_motion(self, state: FluidDynamicsState):
        """
        Vertical atmospheric motion.
        """

        return round(
            state.vertical_velocity,
            2
        )



    def vorticity_dynamics(self, state: FluidDynamicsState):
        """
        Relative vorticity evolution.
        """

        return round(
            state.vorticity,
            2
        )



    def divergence_analysis(self, state: FluidDynamicsState):
        """
        Horizontal divergence.
        """

        return round(
            state.divergence,
            2
        )



    def coriolis_effect(self, state: FluidDynamicsState):
        """
        Coriolis acceleration diagnostic.
        """

        value = (
            state.coriolis_parameter *
            self.horizontal_wind_speed(state)
        )

        return round(value, 2)



    def pressure_gradient_force(self, state: FluidDynamicsState):
        """
        Pressure gradient diagnostic.
        """

        value = (
            state.pressure /
            state.density *
            0.001
        )

        return round(value, 2)



    def momentum_transfer(self, state: FluidDynamicsState):
        """
        Atmospheric momentum transport.
        """

        value = (
            state.density *
            self.horizontal_wind_speed(state)
        )

        return round(value, 2)



    def potential_vorticity(self, state: FluidDynamicsState):
        """
        Potential vorticity diagnostic.

        ACF calibrated formulation:
        combines relative vorticity,
        Coriolis contribution,
        and density correction.
        """

        value = (
            state.vorticity
            +
            state.coriolis_parameter
            +
            (state.density * 0.0165)
        )

        return round(value, 2)
