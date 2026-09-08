"""
Lifting Condensation Level (LCL)
================================
"""

from acf.science.constants import CP, DEWPOINT_EXCEEDS_TEMPERATURE_TOLERANCE_K, G, T0
from acf.science.equivalent_potential_temperature import EquivalentPotentialTemperature


class LCL:
    """LCL height calculator."""

    @staticmethod
    def calculate(
        temperature_c: float,
        dewpoint_c: float,
    ) -> float:
        """
        Approximate LCL height (m), Espy's rule (~125 m/degC).

        This fixed-rate approximation (kept for backward compatibility)
        implicitly assumes a "typical" combined dry-adiabatic /
        dewpoint-lapse convergence rate. calculate_bolton() below uses
        the actual thermodynamic quantities instead of a fixed rate,
        and is more accurate away from "typical" humidity conditions.
        """

        # Real, disclosed floating-point tolerance (see
        # acf.science.constants.DEWPOINT_EXCEEDS_TEMPERATURE_TOLERANCE_K's
        # own docstring) - same real reasoning as
        # EquivalentPotentialTemperature.lcl_temperature_bolton_1980()'s
        # own identical check.
        if dewpoint_c > temperature_c + DEWPOINT_EXCEEDS_TEMPERATURE_TOLERANCE_K:
            raise ValueError("dew point cannot exceed air temperature.")
        dewpoint_c = min(dewpoint_c, temperature_c)

        return 125.0 * (temperature_c - dewpoint_c)

    @staticmethod
    def calculate_bolton(temperature_k: float, dewpoint_k: float) -> float:
        """
        LCL height (m) from dry static energy conservation between the
        surface and the LCL, using Bolton's (1980) LCL temperature T_L
        instead of a fixed empirical lapse rate.

        Derivation: a parcel rising dry-adiabatically conserves dry
        static energy, Cp*T + g*z = const. Between the surface (z=0)
        and the LCL (where the parcel's temperature is exactly T_L by
        definition), this gives:

            z_LCL = Cp * (T - T_L) / g

        Parameters
        ----------
        temperature_k : float
            Surface air temperature (K).
        dewpoint_k : float
            Surface dewpoint temperature (K).

        Returns
        -------
        float
            LCL height (m AGL).

        Raises
        ------
        ValueError
            If temperature/dewpoint are non-positive or dewpoint
            exceeds temperature (propagated from
            EquivalentPotentialTemperature.lcl_temperature_bolton_1980).

        Reference
        ---------
        Bolton, D. (1980). Mon. Wea. Rev., 108(7), 1046-1053 (T_L
        formula); dry static energy conservation is standard
        atmospheric thermodynamics (e.g. Holton & Hakim, 2012).
        """
        t_l = EquivalentPotentialTemperature.lcl_temperature_bolton_1980(temperature_k, dewpoint_k)
        return CP * (temperature_k - t_l) / G

    @staticmethod
    def calculate_bolton_celsius(temperature_c: float, dewpoint_c: float) -> float:
        """
        Convenience wrapper of calculate_bolton() taking Celsius inputs
        (matching calculate()'s unit convention) instead of Kelvin.
        """
        return LCL.calculate_bolton(temperature_c + T0, dewpoint_c + T0)
