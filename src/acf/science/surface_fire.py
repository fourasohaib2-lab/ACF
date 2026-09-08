"""
Surface Fire / Evapotranspiration
====================================

Reference evapotranspiration (FAO-56 Penman-Monteith) — verified.

NOT implemented here (documented gap, not fabricated): the Canadian
Forest Fire Weather Index (FWI) System (Van Wagner 1987) — FFMC, DMC,
DC, ISI, BUI, FWI. This is a 6-index, multi-step system where each
fuel moisture code has its own branching sub-formula (including a
day-length adjustment table that varies by calendar month and
hemisphere). Multiple searches for the exact primary-source equations
came back with only structural/conceptual descriptions, not the
numeric coefficients — implementing it from partial information would
misrepresent a system that is operationally used for real fire-danger
warnings as validated when it isn't. Flagged for a future pass with
Van Wagner (1987)'s original CFS Forestry Technical Report 35 (or Wang,
Anderson & Suddaby 2015's complete-equations report) in hand.

Reference:
    Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998). "Crop
    Evapotranspiration - Guidelines for Computing Crop Water
    Requirements". FAO Irrigation and Drainage Paper 56. Rome: FAO.
"""

import math

from acf.science.boundary_layer import BowenRatio


class SaturationVaporPressureFAO56:
    """
    FAO-56's own Tetens-form es(T), with FAO-56's specific constants
    (0.6108, 17.27, 237.3) — deliberately NOT reusing
    science/saturation_vapor_pressure.py's Bolton-form constants
    (17.67, 243.5): FAO-56 defines its own parametrization for the
    Penman-Monteith ET0 procedure specifically, and mixing the two
    would introduce a small but real inconsistency inside a single
    standardized calculation chain that FAO-56 itself keeps internally
    consistent.
    """

    @staticmethod
    def calculate(temperature_c: float) -> float:
        """es(T) = 0.6108 * exp(17.27*T / (T+237.3)), in kPa."""
        return 0.6108 * math.exp(17.27 * temperature_c / (temperature_c + 237.3))

    @staticmethod
    def slope(temperature_c: float) -> float:
        """
        Delta = d(es)/dT = 4098 * es(T) / (T+237.3)^2, in kPa/degC.

        Derived analytically from es(T) above (chain rule); 4098 =
        17.27*237.3, verified by re-derivation, not just quoted.
        """
        es = SaturationVaporPressureFAO56.calculate(temperature_c)
        return 4098.0 * es / (temperature_c + 237.3) ** 2


class PenmanMonteithFAO56:
    """FAO-56 reference evapotranspiration (ET0) for a hypothetical short reference crop."""

    @staticmethod
    def calculate(
        net_radiation_mj_m2_day: float,
        soil_heat_flux_mj_m2_day: float,
        temperature_c: float,
        wind_speed_2m_m_s: float,
        actual_vapor_pressure_kpa: float,
        pressure_hpa: float = 1013.25,
    ) -> float:
        """
        ET0 = [Delta*0.408*(Rn-G) + gamma*(900/(T+273))*u2*(es-ea)] / [Delta + gamma*(1+0.34*u2)]

        Parameters
        ----------
        net_radiation_mj_m2_day : float
            Net radiation Rn (MJ/m^2/day).
        soil_heat_flux_mj_m2_day : float
            Soil heat flux G (MJ/m^2/day). Often ~0 for daily timesteps.
        temperature_c : float
            Mean daily air temperature at 2m (degC).
        wind_speed_2m_m_s : float
            Mean daily wind speed at 2m height (m/s), >= 0.
        actual_vapor_pressure_kpa : float
            Actual vapor pressure ea (kPa), e.g. from relative
            humidity: ea = RH/100 * es(T).
        pressure_hpa : float
            Atmospheric pressure (hPa), for the psychrometric constant.
            Defaults to standard sea-level pressure.

        Returns
        -------
        float
            ET0 (mm/day).

        Raises
        ------
        ValueError
            If wind_speed_2m_m_s is negative or pressure_hpa is non-positive.

        Reference
        ---------
        Allen, Pereira, Raes & Smith (1998), FAO Irrigation and
        Drainage Paper 56, Ch. 4. Coefficients (0.408, 900, 0.34)
        verified via WebSearch; the WebSearch snippet's transcription
        of the equation omitted the Delta factor that must multiply
        the radiation term (0.408*(Rn-G)) — caught by a numeric sanity
        check against a known worked example (Rn=13.28, G=0.14,
        T=16.9C, u2=2.078 m/s, es=1.997kPa, ea=1.409kPa -> ET0~3.9
        mm/day) which came out ~6x too high before the fix and ~3.74
        after, confirming the corrected form:
        ET0 = [Delta*0.408*(Rn-G) + gamma*(900/(T+273))*u2*(es-ea)]
              / [Delta + gamma*(1+0.34*u2)]
        """
        if wind_speed_2m_m_s < 0:
            raise ValueError("wind_speed_2m_m_s must be non-negative.")
        if pressure_hpa <= 0:
            raise ValueError("pressure_hpa must be positive.")

        es = SaturationVaporPressureFAO56.calculate(temperature_c)
        delta = SaturationVaporPressureFAO56.slope(temperature_c)
        # Reuse the existing psychrometric-constant formula (hPa/K),
        # converted to FAO-56's kPa/degC convention.
        gamma = BowenRatio.psychrometric_constant(pressure_hpa) / 10.0

        numerator = delta * 0.408 * (net_radiation_mj_m2_day - soil_heat_flux_mj_m2_day) + gamma * (
            900.0 / (temperature_c + 273.0)
        ) * wind_speed_2m_m_s * (es - actual_vapor_pressure_kpa)
        denominator = delta + gamma * (1.0 + 0.34 * wind_speed_2m_m_s)

        return numerator / denominator
