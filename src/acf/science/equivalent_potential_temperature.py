"""
Equivalent Potential Temperature
================================

Two implementations are provided, per ACF's single-source-of-truth
policy (one file per physical quantity, canonical + documented
alternatives — never parallel files for the same formula):

- ``calculate()``           : simple exp(Lv*q/(Cp*T)) approximation.
  Kept as-is (legacy/approximation) — existing callers and tests rely
  on its exact behaviour, and it needs only temperature + humidity.
- ``calculate_bolton_1980()``: CANONICAL reference formula, requires
  temperature, dewpoint and pressure. This is the empirical fit from
  Bolton (1980) in the form used operationally (e.g. MetPy, SHARPpy),
  accurate to within ~0.3 K over the meteorological range.

Reference:
    Bolton, D. (1980). "The Computation of Equivalent Potential
    Temperature". Monthly Weather Review, 108(7), 1046-1053.
    https://doi.org/10.1175/1520-0493(1980)108<1046:TCOEPT>2.0.CO;2
"""

from math import exp, log

from acf.science.constants import CP, DEWPOINT_EXCEEDS_TEMPERATURE_TOLERANCE_K, KAPPA, LV
from acf.science.saturation_mixing_ratio import SaturationMixingRatio
from acf.science.saturation_vapor_pressure import SaturationVaporPressure


class EquivalentPotentialTemperature:
    """Equivalent potential temperature calculator."""

    @staticmethod
    def calculate(
        temperature_k: float,
        specific_humidity: float,
    ) -> float:
        """
        Calculate equivalent potential temperature (simple approximation).

        This is the exp(Lv*q/(Cp*T)) form: it ignores the LCL correction
        and pressure dependence that Bolton (1980) accounts for, so it
        is only a rough estimate. Use calculate_bolton_1980() for the
        accurate, referenced formula. Kept for backward compatibility.

        Parameters
        ----------
        temperature_k : float
            Temperature (K)

        specific_humidity : float
            Specific humidity (kg/kg)

        Returns
        -------
        float
            Equivalent potential temperature (K)
        """

        if temperature_k <= 0:
            raise ValueError("temperature must be positive.")

        if specific_humidity < 0:
            raise ValueError("specific_humidity must be non-negative.")

        return temperature_k * exp(LV * specific_humidity / (CP * temperature_k))

    @staticmethod
    def lcl_temperature_bolton_1980(temperature_k: float, dewpoint_k: float) -> float:
        """
        LCL (lifting condensation level) temperature, Bolton (1980) eq.

        T_L = 56 + 1 / (1/(Td-56) + ln(T/Td)/800)

        Parameters
        ----------
        temperature_k : float
            Air temperature (K).
        dewpoint_k : float
            Dewpoint temperature (K).

        Returns
        -------
        float
            Temperature at the LCL (K).

        Raises
        ------
        ValueError
            If temperature/dewpoint are non-positive or dewpoint
            exceeds temperature.

        Notes
        -----
        Reused by calculate_bolton_1980() and by science.lcl.LCL's
        Bolton-based height method — factored out here so the formula
        has exactly one implementation (single source of truth).
        """
        if temperature_k <= 0 or dewpoint_k <= 0:
            raise ValueError("temperature and dewpoint must be positive.")
        # Real, disclosed floating-point tolerance (see
        # acf.science.constants.DEWPOINT_EXCEEDS_TEMPERATURE_TOLERANCE_K's
        # own docstring) - a genuinely saturated point (RH clipped to
        # exactly 100%) can round-trip through the Magnus-Tetens
        # dewpoint inversion a few ULPs above the input temperature;
        # only a real, meaningfully larger excess is treated as a
        # genuine caller-input error.
        if dewpoint_k > temperature_k + DEWPOINT_EXCEEDS_TEMPERATURE_TOLERANCE_K:
            raise ValueError("dewpoint cannot exceed temperature.")
        dewpoint_k = min(dewpoint_k, temperature_k)

        return 56.0 + 1.0 / (1.0 / (dewpoint_k - 56.0) + log(temperature_k / dewpoint_k) / 800.0)

    @staticmethod
    def calculate_bolton_1980(
        temperature_k: float,
        dewpoint_k: float,
        pressure_hpa: float,
    ) -> float:
        """
        Calculate equivalent potential temperature (canonical, Bolton 1980).

        Parameters
        ----------
        temperature_k : float
            Air temperature (K)
        dewpoint_k : float
            Dewpoint temperature (K)
        pressure_hpa : float
            Atmospheric pressure (hPa)

        Returns
        -------
        float
            Equivalent potential temperature (K)

        Raises
        ------
        ValueError
            If temperature/pressure are non-positive or dewpoint exceeds
            temperature (physically impossible).

        Notes
        -----
        Formula (T, T_L in K; p in hPa; r = mixing ratio in kg/kg):

            T_L    = 56 + 1 / (1/(Td - 56) + ln(T/Td) / 800)
            theta_L = T * (1000 / (p - e))**kappa * (T / T_L)**(0.28*r)
            theta_E = theta_L * exp(r * (1 + 0.448*r) * (3036/T_L - 1.78))

        where e is the actual vapor pressure (= saturation vapor pressure
        at the dewpoint) and kappa = Rd/Cp. This is the widely used
        operational form of Bolton's eq. (43) (as implemented by e.g.
        MetPy / SHARPpy), reusing ACF's own SaturationVaporPressure
        (already Bolton's es formula) and SaturationMixingRatio.
        """
        if pressure_hpa <= 0:
            raise ValueError("pressure must be positive.")

        t_l = EquivalentPotentialTemperature.lcl_temperature_bolton_1980(temperature_k, dewpoint_k)

        e = SaturationVaporPressure.calculate(dewpoint_k, is_kelvin=True)
        r = SaturationMixingRatio.calculate(e, pressure_hpa)

        theta_l = (
            temperature_k * (1000.0 / (pressure_hpa - e)) ** KAPPA * (temperature_k / t_l) ** (0.28 * r)
        )

        return theta_l * exp(r * (1.0 + 0.448 * r) * (3036.0 / t_l - 1.78))
