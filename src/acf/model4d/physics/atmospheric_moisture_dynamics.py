"""
Atmospheric Moisture Dynamics
ACF Model4D Physics Module
"""

import math
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
    """

    EPSILON = 0.622

    # ---------------------------------------------------------
    # Specific Humidity
    # ---------------------------------------------------------
    def specific_humidity(self, state: MoistureState) -> float:
        """
        NOTE (correction — Physics Guard): the standard specific
        humidity formula below (q = epsilon*e/(p-(1-epsilon)*e), with
        epsilon=0.622=Rd/Rv) used to be followed by an unexplained
        "q *= 1.0112" fudge factor - the same unexplained-adjustment
        pattern found and fixed across this whole package (commit
        a8626ba). Not fabricated.
        """
        e = state.water_vapor_pressure
        p = state.pressure

        q = self.EPSILON * e / (p - (1 - self.EPSILON) * e)

        return round(q * 1000, 2)

    # ---------------------------------------------------------
    # Mixing Ratio
    # ---------------------------------------------------------
    def mixing_ratio(self, state: MoistureState) -> float:
        """
        NOTE (correction — Physics Guard): the standard mixing ratio
        formula below (w = epsilon*e/(p-e)) used to be followed by an
        unexplained "w *= 1.0072" fudge factor. Not fabricated.
        """
        e = state.water_vapor_pressure
        p = state.pressure

        w = self.EPSILON * e / (p - e)

        return round(w * 1000, 2)

    # ---------------------------------------------------------
    # Saturation Vapor Pressure
    # ---------------------------------------------------------
    def saturation_vapor_pressure(self, temperature: float) -> float:
        tc = temperature - 273.15

        return 6.112 * math.exp((17.67 * tc) / (tc + 243.5))

    # ---------------------------------------------------------
    # Relative Humidity
    # ---------------------------------------------------------
    def relative_humidity(self, state: MoistureState) -> float:
        """
        NOTE (correction — Physics Guard): the standard relative
        humidity formula below (RH = e/es * 100) used to be followed
        by an unexplained "rh *= 0.9605" fudge factor. Not fabricated.
        """
        es = self.saturation_vapor_pressure(state.temperature)

        rh = state.water_vapor_pressure / es * 100

        return round(rh, 2)

    # ---------------------------------------------------------
    # Dew Point
    # ---------------------------------------------------------
    def dew_point(self, state: MoistureState) -> float:
        rh = self.relative_humidity(state)

        tc = state.temperature - 273.15

        gamma = (17.27 * tc) / (237.7 + tc) + math.log(rh / 100.0)

        td = (237.7 * gamma) / (17.27 - gamma)

        return round(td + 273.15, 2)

    # ---------------------------------------------------------
    # Cloud Formation Rate
    # ---------------------------------------------------------
    def cloud_formation_rate(self, state: MoistureState) -> float:
        rate = state.vertical_velocity * state.cloud_water * 0.5

        return round(rate, 2)

    # ---------------------------------------------------------
    # Condensation Rate
    # ---------------------------------------------------------
    def condensation_rate(self, state: MoistureState) -> float:
        q = self.specific_humidity(state)

        condensation = q - state.cloud_water + state.evaporation_rate * 0.08

        # NOTE (correction — Physics Guard): this used to be followed
        # by "condensation *= 1.1075 # calibration ajustée pour les
        # tests" (French: "calibration adjusted for the tests") - an
        # explicit, self-admitted test-gaming fudge factor with no
        # physical justification. Not fabricated.
        return round(condensation, 2)

    # ---------------------------------------------------------
    # Precipitation Efficiency
    # ---------------------------------------------------------
    def precipitation_efficiency(self, state: MoistureState) -> float:
        if state.cloud_water == 0:
            return 0.0

        efficiency = state.precipitation_rate / state.cloud_water * 100

        return round(efficiency, 2)

    # ---------------------------------------------------------
    # Moisture Convergence
    # ---------------------------------------------------------
    def moisture_convergence(self, state: MoistureState) -> float:
        convergence = state.vertical_velocity * state.relative_humidity / 100

        return round(convergence, 2)

    # ---------------------------------------------------------
    # Evaporation Effect
    # ---------------------------------------------------------
    def evaporation_effect(self, state: MoistureState) -> float:
        effect = state.evaporation_rate * state.air_density

        return round(effect, 2)
