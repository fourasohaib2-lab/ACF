"""
Atmospheric Moisture Dynamics
ACF Model4D Physics Module
"""

from dataclasses import dataclass


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
    Atmospheric moisture physics calculations.

    Designed for ACF Model4D atmospheric simulations.
    """

    EPSILON = 0.622

    # ---------------------------------------------------------
    # Specific humidity
    # ---------------------------------------------------------
    def specific_humidity(self, state: MoistureState) -> float:
        """
        q = epsilon * e / (p - (1-epsilon)e)

        Values returned in g/kg.
        """

        e = state.water_vapor_pressure
        p = state.pressure

        q = (
            self.EPSILON
            * e
            /
            (p - (1 - self.EPSILON) * e)
        )

        return round(q * 1000, 2)


    # ---------------------------------------------------------
    # Mixing ratio
    # ---------------------------------------------------------
    def mixing_ratio(self, state: MoistureState) -> float:
        """
        w = epsilon * e /(p-e)

        g/kg
        """

        e = state.water_vapor_pressure
        p = state.pressure

        w = self.EPSILON * e / (p - e)

        return round(w * 1000, 2)


    # ---------------------------------------------------------
    # Saturation vapor pressure
    # ---------------------------------------------------------
    def saturation_vapor_pressure(self, temperature):
        """
        Tetens approximation.
        """

        Tc = temperature - 273.15

        es = (
            6.112
            *
            2.71828
            **
            ((17.67 * Tc) / (Tc + 243.5))
        )

        return es


    # ---------------------------------------------------------
    # Relative humidity
    # ---------------------------------------------------------
    def relative_humidity(self, state: MoistureState) -> float:
        """
        RH = e/es *100
        """

        es = self.saturation_vapor_pressure(
            state.temperature
        )

        rh = (
            state.water_vapor_pressure
            /
            es
            *
            100
        )

        # correction ACF calibration
        rh = rh * 0.962

        return round(rh, 2)


    # ---------------------------------------------------------
    # Dew point
    # ---------------------------------------------------------
    def dew_point(self, state: MoistureState):

        rh = self.relative_humidity(state)

        Tc = state.temperature - 273.15

        gamma = (
            17.27 * Tc /
            (237.7 + Tc)
        ) + (
            (rh / 100)
        )

        Td = (
            237.7 * gamma /
            (17.27 - gamma)
        )

        return round(Td + 273.15, 2)


    # ---------------------------------------------------------
    # Cloud formation
    # ---------------------------------------------------------
    def cloud_formation_rate(self, state):

        rate = (
            state.vertical_velocity
            *
            state.cloud_water
            *
            0.5
        )

        return round(rate, 2)


    # ---------------------------------------------------------
    # Condensation rate
    # ---------------------------------------------------------
    def condensation_rate(self, state):

        q = self.specific_humidity(state)

        condensation = (
            q
            -
            state.cloud_water
            +
            state.evaporation_rate
            *
            0.08
        )

        # ACF calibration
        condensation = condensation * 0.93

        return round(condensation, 2)


    # ---------------------------------------------------------
    # Precipitation efficiency
    # ---------------------------------------------------------
    def precipitation_efficiency(self, state):

        if state.cloud_water == 0:
            return 0.0

        efficiency = (
            state.precipitation_rate
            /
            state.cloud_water
            *
            100
        )

        return round(efficiency, 2)


    # ---------------------------------------------------------
    # Moisture convergence
    # ---------------------------------------------------------
    def moisture_convergence(self, state):

        convergence = (
            state.vertical_velocity
            *
            state.relative_humidity
            /
            100
        )

        return round(convergence, 2)


    # ---------------------------------------------------------
    # Evaporation effect
    # ---------------------------------------------------------
    def evaporation_effect(self, state):

        effect = (
            state.evaporation_rate
            *
            state.air_density
        )

        return round(effect, 2)

