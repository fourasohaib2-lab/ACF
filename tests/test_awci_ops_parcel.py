"""Surface parcel ascent: Bolton LCL, theta-e conserving pseudo-adiabat, virtual-temperature EL."""

import numpy as np

from acf.awci.ops.parcel import saturated_parcel_temperature_k, surface_parcel
from acf.awci.ops.thermo import (
    lcl_temperature_bolton_k,
    saturation_specific_humidity,
    saturation_vapor_pressure_hpa,
    theta_e_bolton_k,
    virtual_temperature_k,
)
LEVELS = np.array([1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100], dtype=float)


def test_saturation_specific_humidity_matches_definition() -> None:
    es = saturation_vapor_pressure_hpa(np.array(293.15))
    assert np.isclose(saturation_specific_humidity(np.array(293.15), np.array(1000.0)),
                      0.622 * es / (1000.0 - 0.378 * es))


def test_virtual_temperature() -> None:
    assert np.isclose(virtual_temperature_k(np.array(300.0), np.array(0.01)), 300.0 * (1 + (1 / 0.622 - 1) * 0.01))


def test_lcl_temperature_bolton_eq15_saturated_and_dry() -> None:
    assert np.isclose(lcl_temperature_bolton_k(np.array(290.0), np.array(290.0)), 290.0)
    t_l = lcl_temperature_bolton_k(np.array(303.15), np.array(283.15))
    assert np.isclose(t_l, 1.0 / (1.0 / (283.15 - 56.0) + np.log(303.15 / 283.15) / 800.0) + 56.0)
    assert 270.0 < t_l < 283.15


def test_saturated_parcel_conserves_theta_e() -> None:
    p = np.array([850.0, 500.0, 200.0])
    theta_e = np.full(3, 340.0)
    t = saturated_parcel_temperature_k(theta_e, p)
    back = theta_e_bolton_k(t, saturation_specific_humidity(t, p), p)
    np.testing.assert_allclose(back, 340.0, atol=0.05)
    assert np.all(np.diff(t) < 0)  # colder aloft


def _column(t_env_c: np.ndarray, q_env: np.ndarray) -> tuple:
    shape = (len(LEVELS), 1, 1)
    gh = (44330.8 * (1 - (LEVELS / 1013.25) ** 0.190263)).reshape(shape)  # ISA heights, monotonic
    return (t_env_c + 273.15).reshape(shape), q_env.reshape(shape), gh


def test_unstable_column_has_el_high_and_stable_column_has_none() -> None:
    t_env_c = np.array([30, 24, 18, 6, -2, -11, -22, -37, -46, -55, -60, -65], dtype=float)
    q = np.full(len(LEVELS), 1e-4)
    t_env, q_env, gh = _column(t_env_c, q)
    under = np.zeros_like(t_env, dtype=bool)
    moist = surface_parcel(np.array([[305.0]]), np.array([[297.0]]), np.array([[1005.0]]), LEVELS,
                           t_env, q_env, gh, under)
    assert moist.el_index[0, 0] >= 7 and moist.el_temp_k[0, 0] < 253.15  # deep convection, top colder than -20 C
    assert moist.p_lcl_hpa[0, 0] < 1005.0
    warm_aloft = t_env + 25.0  # strong inversion everywhere: no buoyancy
    dry = surface_parcel(np.array([[290.0]]), np.array([[270.0]]), np.array([[1005.0]]), LEVELS,
                         warm_aloft, q_env, gh, under)
    assert dry.el_index[0, 0] == -1 and np.isnan(dry.el_gh_m[0, 0]) and np.isnan(dry.el_temp_k[0, 0])


def test_underground_levels_never_buoyant() -> None:
    t_env_c = np.array([30, 24, 18, 6, -2, -11, -22, -37, -46, -55, -60, -65], dtype=float)
    t_env, q_env, gh = _column(t_env_c, np.full(len(LEVELS), 1e-4))
    under = np.ones_like(t_env, dtype=bool)
    res = surface_parcel(np.array([[305.0]]), np.array([[297.0]]), np.array([[1005.0]]), LEVELS, t_env, q_env,
                         gh, under)
    assert res.el_index[0, 0] == -1


def test_parcel_below_lcl_is_not_buoyant_when_colder_than_dry_adiabat_env() -> None:
    # very dry surface air: LCL above 700 hPa, so 925/850 hPa are on the dry adiabat and never count for the EL
    t_env_c = np.array([30, 24, 18, 6, -2, -11, -22, -37, -46, -55, -60, -65], dtype=float)
    t_env, q_env, gh = _column(t_env_c, np.full(len(LEVELS), 1e-4))
    res = surface_parcel(np.array([[305.0]]), np.array([[260.0]]), np.array([[1005.0]]), LEVELS, t_env, q_env, gh,
                         np.zeros_like(t_env, dtype=bool))
    assert res.p_lcl_hpa[0, 0] < 700.0
    assert res.el_index[0, 0] == -1 or LEVELS[res.el_index[0, 0]] < res.p_lcl_hpa[0, 0]
