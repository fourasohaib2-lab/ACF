"""
ACF - Atmospheric Complexity Framework
Model4D Moisture Physics Module

Atmospheric moisture calculations.
"""

import math


class Moisture:
    """
    Atmospheric moisture physics.

    Provides basic humidity diagnostics:
    - relative humidity
    - vapor pressure
    - mixing ratio
    - specific humidity
    - dew point
    """

    @staticmethod
    def vapor_pressure(relative_humidity: float, saturation_pressure: float) -> float:
        """
        Calculate vapor pressure.

        e = RH * es / 100
        """

        return round((relative_humidity / 100.0) * saturation_pressure, 10)

    @staticmethod
    def relative_humidity(vapor_pressure: float, saturation_pressure: float) -> float:
        """
        Calculate relative humidity.

        RH = e / es * 100
        """

        if saturation_pressure == 0:
            return 0.0

        return round((vapor_pressure / saturation_pressure) * 100, 6)

    @staticmethod
    def mixing_ratio(vapor_pressure: float, pressure: float) -> float:
        """
        Mixing ratio.

        w = 0.622 e / (p-e)
        """

        if pressure <= vapor_pressure:
            return 0.0

        return round(0.622 * vapor_pressure / (pressure - vapor_pressure), 10)

    @staticmethod
    def specific_humidity(mixing_ratio: float) -> float:
        """
        Specific humidity.

        q = w/(1+w)
        """

        return round(mixing_ratio / (1 + mixing_ratio), 10)

    @staticmethod
    def dew_point(temperature: float, relative_humidity: float) -> float:
        """
        Magnus formula.

        Temperature in Celsius.
        """

        if relative_humidity <= 0:
            return temperature

        a = 17.27
        b = 237.7

        alpha = (a * temperature) / (b + temperature) + math.log(relative_humidity / 100)

        return round((b * alpha) / (a - alpha), 6)

    @staticmethod
    def category(relative_humidity: float) -> str:
        """
        Humidity classification.
        """

        if relative_humidity < 30:
            return "Dry"

        if relative_humidity < 60:
            return "Moderate"

        if relative_humidity < 80:
            return "Humid"

        return "Very Humid"
