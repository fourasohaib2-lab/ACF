"""
Tests for acf.science.surface_fire.
"""

import pytest

from acf.science.surface_fire import PenmanMonteithFAO56, SaturationVaporPressureFAO56


def test_saturation_vapor_pressure_known_value_25c():
    # Standard textbook value: es(25 degC) ~ 3.17 kPa.
    es = SaturationVaporPressureFAO56.calculate(25.0)
    assert es == pytest.approx(3.17, abs=0.01)


def test_slope_matches_analytic_derivative():
    # Numerically differentiate es(T) and compare to slope().
    t = 20.0
    h = 1e-4
    es_plus = SaturationVaporPressureFAO56.calculate(t + h)
    es_minus = SaturationVaporPressureFAO56.calculate(t - h)
    numerical_slope = (es_plus - es_minus) / (2 * h)
    assert SaturationVaporPressureFAO56.slope(t) == pytest.approx(numerical_slope, rel=1e-4)


def test_et0_matches_known_worked_example():
    # Kimberly, Idaho FAO-56 style example (widely cited).
    et0 = PenmanMonteithFAO56.calculate(
        net_radiation_mj_m2_day=13.28,
        soil_heat_flux_mj_m2_day=0.14,
        temperature_c=16.9,
        wind_speed_2m_m_s=2.078,
        actual_vapor_pressure_kpa=1.409,
        pressure_hpa=1010.0,
    )
    assert et0 == pytest.approx(3.9, abs=0.3)


def test_et0_positive_for_typical_summer_conditions():
    es = SaturationVaporPressureFAO56.calculate(25.0)
    et0 = PenmanMonteithFAO56.calculate(
        net_radiation_mj_m2_day=15.0,
        soil_heat_flux_mj_m2_day=0.0,
        temperature_c=25.0,
        wind_speed_2m_m_s=2.0,
        actual_vapor_pressure_kpa=0.5 * es,
    )
    # Physically plausible daily ET0 range for a reference crop.
    assert 2.0 < et0 < 12.0


def test_et0_higher_wind_increases_et0_when_air_is_dry():
    es = SaturationVaporPressureFAO56.calculate(25.0)
    ea = 0.3 * es  # fairly dry air
    et0_calm = PenmanMonteithFAO56.calculate(
        net_radiation_mj_m2_day=15.0, soil_heat_flux_mj_m2_day=0.0, temperature_c=25.0,
        wind_speed_2m_m_s=1.0, actual_vapor_pressure_kpa=ea,
    )
    et0_windy = PenmanMonteithFAO56.calculate(
        net_radiation_mj_m2_day=15.0, soil_heat_flux_mj_m2_day=0.0, temperature_c=25.0,
        wind_speed_2m_m_s=5.0, actual_vapor_pressure_kpa=ea,
    )
    assert et0_windy > et0_calm


def test_et0_invalid_negative_wind():
    with pytest.raises(ValueError):
        PenmanMonteithFAO56.calculate(
            net_radiation_mj_m2_day=15.0,
            soil_heat_flux_mj_m2_day=0.0,
            temperature_c=25.0,
            wind_speed_2m_m_s=-1.0,
            actual_vapor_pressure_kpa=1.0,
        )


def test_et0_invalid_pressure():
    with pytest.raises(ValueError):
        PenmanMonteithFAO56.calculate(
            net_radiation_mj_m2_day=15.0,
            soil_heat_flux_mj_m2_day=0.0,
            temperature_c=25.0,
            wind_speed_2m_m_s=2.0,
            actual_vapor_pressure_kpa=1.0,
            pressure_hpa=0.0,
        )
