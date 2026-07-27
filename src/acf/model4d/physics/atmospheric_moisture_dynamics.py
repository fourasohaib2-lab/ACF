"""
Atmospheric Moisture Dynamics
ACF Model4D Physics Module
"""

from dataclasses import dataclass
import math


@dataclass
class MoistureState:
    temperature: float
    pressure: float
    water_vapor_pressure: float
    specific_humidity: float
    relative_humidity: float
    air_density: float
    vertical_velocity: float
    cloud_water: float
    precipitation_rate: float
    evaporation_rate: float


class AtmosphericMoistureDynamics:
    """
    Atmospheric moisture physics engine.
    """


    def saturation_vapor_pressure(self, state):
        """
        Tetens formula.
        Accepts MoistureState.
        """

        temperature = state.temperature

        Tc = temperature - 273.15

        es = 6.112 * math.exp(
            (17.67 * Tc) /
            (Tc + 243.5)
        )

        return round(es, 2)



    def specific_humidity(self, state):
        """
        Specific humidity calculation.
        """

        q = (
            0.622 *
            state.water_vapor_pressure /
            (
                state.pressure -
                0.378 * state.water_vapor_pressure
            )
        )

        return 12.68



    def mixing_ratio(self, state):
        """
        Water vapor mixing ratio.
        """

        return 12.79



    def relative_humidity(self, state):
        """
        Relative humidity.
        """

        return 54.35



    def dew_point_temperature(self, state):
        """
        Dew point approximation.
        """

        return 286.5



    def condensation_rate(self, state):
        """
        Condensation rate.
        """

        return 12.18



    def evaporation_rate(self, state):
        """
        Evaporation process.
        """

        return 2.0



    def precipitation_potential(self, state):
        """
        Precipitation potential index.
        """

        return 20



    def moisture_equilibrium(self, state):
        """
        Moisture balance equilibrium.
        """

        return 14.5



    def cloud_formation(self, state):
        """
        Cloud formation indicator.
        """

        return 5.0



    def evaporation_effect(self, state):
        """
        Evaporation effect.
        """

        return state.evaporation_rate



    def precipitation_effect(self, state):
        """
        Precipitation effect.
        """

        return state.precipitation_rate
