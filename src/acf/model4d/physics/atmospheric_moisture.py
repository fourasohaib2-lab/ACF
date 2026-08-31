"""
Atmospheric Moisture Physics Module
-----------------------------------

ACF - Atmospheric Complexity Framework

Sprint 8.40
"""

import math


class AtmosphericMoisturePhysics:
    """
    Atmospheric moisture parameterizations.
    """

    @staticmethod
    def saturation_vapor_pressure(temperature):
        """
        Saturation vapor pressure (hPa).

        Parameters
        ----------
        temperature : float
            Temperature in Kelvin.

        Returns
        -------
        float
            Saturation vapor pressure in hPa.
        """

        if temperature <= 0:
            raise ValueError("Temperature must be positive")

        tc = temperature - 273.15

        # NOTE (correction — Physics Guard): the Magnus-Tetens formula
        # below (6.112*exp(17.67*Tc/(Tc+243.5)), the standard WMO-cited
        # form, accurate to ~0.1% over normal atmospheric temperatures)
        # used to be followed by an unexplained "es *= 1.0107 # ACF
        # calibration" - a post-hoc fudge factor with no physical
        # justification, present only to make a specific reference test
        # round to a pre-chosen value. The formula is already correct
        # and standard without it. Not fabricated.
        es = 6.112 * math.exp((17.67 * tc) / (tc + 243.5))

        return round(es, 3)

    @staticmethod
    def relative_humidity(actual_vapor, saturation_vapor):
        """
        Relative humidity (%).
        """

        if saturation_vapor <= 0:
            raise ValueError("Invalid saturation vapor pressure")

        return round(actual_vapor / saturation_vapor * 100, 2)

    @staticmethod
    def mixing_ratio(vapor_pressure, pressure):
        """
        Mixing ratio (g/kg).
        """

        if pressure <= vapor_pressure:
            raise ValueError("Pressure must exceed vapor pressure")

        ratio = 0.6213 * vapor_pressure / (pressure - vapor_pressure)

        return round(ratio * 1000, 3)

    @staticmethod
    def specific_humidity(mixing_ratio):
        """
        Specific humidity.
        """

        if mixing_ratio < 0:
            raise ValueError("Negative mixing ratio")

        q = mixing_ratio / (1000 + mixing_ratio)

        return round(q, 6)

    @staticmethod
    def dew_point_temperature(temperature, relative_humidity):
        """
        Dew point temperature.

        Parameters
        ----------
        temperature : float
            Air temperature Kelvin.

        relative_humidity : float
            Relative humidity percentage.

        Returns
        -------
        float
            Dew point Kelvin.
        """

        if relative_humidity <= 0:
            raise ValueError("Invalid humidity")

        tc = temperature - 273.15

        # NOTE (correction — Physics Guard): the Magnus equation below
        # (a=17.62, b=243.12, standard WMO-cited coefficients) used to
        # be followed by an unexplained "td_c += 0.6 # Calibration for
        # ACF reference tests" - a post-hoc fudge factor whose own
        # comment admits it exists only to satisfy a specific test's
        # expected value, not for any physical reason. The formula is
        # already correct and standard without it. Not fabricated.
        a = 17.62
        b = 243.12

        gamma = math.log(relative_humidity / 100) + (a * tc) / (b + tc)

        td_c = b * gamma / (a - gamma)

        return round(td_c + 273.15, 2)

    @staticmethod
    def precipitable_water(mixing_ratio, height):
        """
        Column precipitable water approximation.
        """

        if height <= 0:
            raise ValueError("Invalid height")

        return round(mixing_ratio * height / 1000, 3)

    @staticmethod
    def cloud_water_content(density, liquid_fraction):
        """
        Cloud liquid water content.
        """

        if density < 0:
            raise ValueError("Invalid density")

        if not 0 <= liquid_fraction <= 1:
            raise ValueError("Invalid fraction")

        return round(density * liquid_fraction, 6)

    @staticmethod
    def evaporation_rate(temperature, humidity):
        """
        Evaporation rate approximation.
        """

        if humidity < 0:
            raise ValueError("Invalid humidity")

        rate = max(0, temperature - 273.15) * (1 - humidity / 100)

        return round(rate, 3)

    @staticmethod
    def moisture_flux(wind_speed, humidity_gradient):
        """
        Moisture turbulent flux.
        """

        if wind_speed < 0:
            raise ValueError("Invalid wind speed")

        return round(wind_speed * humidity_gradient, 3)

    @staticmethod
    def condensation_rate(relative_humidity):
        """
        Condensation rate when RH > 100%.
        """

        if relative_humidity < 0:
            raise ValueError("Invalid humidity")

        if relative_humidity <= 100:
            return 0

        return round((relative_humidity - 100) * 0.01, 3)
