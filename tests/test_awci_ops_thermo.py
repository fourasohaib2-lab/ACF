import numpy as np

from acf.awci.ops.thermo import (
    cloud_base_lcl_m,
    dewpoint_k_from_vapor_pressure,
    relative_humidity_pct,
    saturation_vapor_pressure_hpa,
    theta_e_bolton_k,
    vapor_pressure_hpa,
)
from acf.science.equivalent_potential_temperature import EquivalentPotentialTemperature
from acf.science.saturation_vapor_pressure import SaturationVaporPressure
from acf.science.vapor_pressure import VaporPressure

RNG = np.random.default_rng(42)
T = RNG.uniform(210.0, 310.0, 500)
P = RNG.uniform(100.0, 1030.0, 500)
RH = RNG.uniform(0.05, 1.0, 500)
Q = np.array([0.622 * r * SaturationVaporPressure.calculate(t) / p for t, p, r in zip(T, P, RH)])


def test_vapor_pressure_matches_scalar() -> None:
    expected = np.array([VaporPressure.calculate(q, p) for q, p in zip(Q, P)])
    np.testing.assert_allclose(vapor_pressure_hpa(Q, P), expected, rtol=1e-12)


def test_saturation_vapor_pressure_matches_scalar() -> None:
    expected = np.array([SaturationVaporPressure.calculate(t) for t in T])
    np.testing.assert_allclose(saturation_vapor_pressure_hpa(T), expected, rtol=1e-12)


def test_dewpoint_inverts_bolton_es_exactly() -> None:
    e = vapor_pressure_hpa(Q, P)
    np.testing.assert_allclose(saturation_vapor_pressure_hpa(dewpoint_k_from_vapor_pressure(e)), e, rtol=1e-10)


def test_theta_e_matches_scalar_bolton_given_same_dewpoint() -> None:
    td = np.minimum(dewpoint_k_from_vapor_pressure(vapor_pressure_hpa(Q, P)), T)
    expected = np.array([EquivalentPotentialTemperature.calculate_bolton_1980(t, d, p) for t, d, p in zip(T, td, P)])
    np.testing.assert_allclose(theta_e_bolton_k(T, Q, P), expected, rtol=1e-10)


def test_zero_humidity_gives_nan_theta_e() -> None:
    out = theta_e_bolton_k(np.array([290.0]), np.array([0.0]), np.array([1000.0]))
    assert np.isnan(out[0])


def test_relative_humidity_capped_at_100() -> None:
    q_super = 1.2 * 0.622 * SaturationVaporPressure.calculate(280.0) / 900.0
    assert relative_humidity_pct(np.array([280.0]), np.array([q_super]), np.array([900.0]))[0] == 100.0


def test_cloud_base_lcl_espy_125m_per_kelvin() -> None:
    out = cloud_base_lcl_m(np.array([300.0, 290.0, 285.0]), np.array([290.0, 290.0, 286.0]))
    np.testing.assert_allclose(out, [1250.0, 0.0, 0.0])
