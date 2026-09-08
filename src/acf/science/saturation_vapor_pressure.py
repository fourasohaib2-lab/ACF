"""
Saturation Vapor Pressure
=========================

Formula (Tetens):
    es = 6.112 * exp((17.67 * T) / (T + 243.5))

where:
    es = saturation vapor pressure (hPa)
    T = temperature (°C)

For T in Kelvin: T_celsius = T - 273.15
"""

import math


class SaturationVaporPressure:
    """Saturation vapor pressure calculator."""

    @staticmethod
    def calculate(temperature: float, is_kelvin: bool = True) -> float:
        """
        Calculate saturation vapor pressure using Tetens formula.

        Parameters
        ----------
        temperature : float
            Temperature (Kelvin if is_kelvin=True, else Celsius)
        is_kelvin : bool
            If True, temperature is in Kelvin; else Celsius

        Returns
        -------
        float
            Saturation vapor pressure (hPa)
        """
        if is_kelvin:
            T_celsius = temperature - 273.15
        else:
            T_celsius = temperature

        # Tetens formula
        return 6.112 * math.exp((17.67 * T_celsius) / (T_celsius + 243.5))

    @staticmethod
    def calculate_tetens(temperature: float, is_kelvin: bool = True) -> float:
        """
        Alias for calculate() - for backward compatibility.
        """
        return SaturationVaporPressure.calculate(temperature, is_kelvin)

    @staticmethod
    def calculate_golf(temperature: float, is_kelvin: bool = True) -> float:
        """
        Calculate saturation vapor pressure using the Goff-Gratch formula.
        More accurate for low temperatures.

        NOTE (correction): despite the name and this docstring's own
        accuracy claim, this used to just call the plain Tetens
        calculate() again - not Goff-Gratch at all (the one-line comment
        "Simplified version using Tetens for now" hinted at the gap, but
        the misleading docstring above it was left uncorrected, and
        Tetens is NOT more accurate at low temperatures - if anything
        it's the opposite). Now implements the real Goff-Gratch (1946)
        equation over liquid water, verified via WebFetch against
        Wikipedia's Goff-Gratch equation article and numerically
        cross-checked: log(es) = -7.90298*(Tst/T - 1)
        + 5.02808*log10(Tst/T) - 1.3816e-7*(10^(11.344*(1-T/Tst)) - 1)
        + 8.1328e-3*(10^(-3.49149*(Tst/T - 1)) - 1) + log10(es_st),
        with Tst = 373.15 K (steam point) and es_st = 1013.25 hPa
        (steam-point saturation pressure). At T = Tst this correctly
        reduces to es = es_st exactly (all four correction terms vanish).
        """
        T_kelvin = temperature if is_kelvin else temperature + 273.15
        t_st = 373.15  # steam-point temperature (K)
        es_st = 1013.25  # saturation vapor pressure at steam point (hPa)

        log_es = (
            -7.90298 * (t_st / T_kelvin - 1.0)
            + 5.02808 * math.log10(t_st / T_kelvin)
            - 1.3816e-7 * (10.0 ** (11.344 * (1.0 - T_kelvin / t_st)) - 1.0)
            + 8.1328e-3 * (10.0 ** (-3.49149 * (t_st / T_kelvin - 1.0)) - 1.0)
            + math.log10(es_st)
        )
        return 10.0**log_es
