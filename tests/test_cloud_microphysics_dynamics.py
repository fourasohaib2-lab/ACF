"""
Atmospheric Complexity Framework (ACF)

MODEL4D - Cloud Microphysics Dynamics Test Suite

This file was previously empty - pytest collected it but ran no tests,
so the real source module (src/acf/model4d/physics/
cloud_microphysics_dynamics.py) had 0% coverage and was never actually
verified. Added real tests exercising the actual source class.
"""

import math

import pytest

from acf.model4d.physics.cloud_microphysics_dynamics import CloudMicrophysicsDynamics


def test_saturation_vapor_pressure_ice_matches_formula():
    t_k = 253.15  # -20 degC
    t_c = t_k - 273.15
    expected = round(611.2 * math.exp((21.875 * t_c) / (t_c + 265.5)), 2)
    assert CloudMicrophysicsDynamics.saturation_vapor_pressure_ice(t_k) == pytest.approx(expected)


def test_saturation_vapor_pressure_ice_rejects_non_positive_kelvin():
    with pytest.raises(ValueError):
        CloudMicrophysicsDynamics.saturation_vapor_pressure_ice(0.0)


def test_bergeron_findeisen_potential_zero_below_ice_saturation():
    assert CloudMicrophysicsDynamics.bergeron_findeisen_potential(300.0, 250.0, 200.0) == 0.0


def test_bergeron_findeisen_potential_positive_in_growth_regime():
    # Actual vapor pressure between ice and water saturation -> WBF growth favorable
    result = CloudMicrophysicsDynamics.bergeron_findeisen_potential(
        e_sat_water=300.0, e_sat_ice=250.0, actual_vapor_pressure=280.0
    )
    assert result == pytest.approx(30.0)


def test_terminal_velocity_hydrometeor_species_differ():
    diameter = 0.002  # 2mm
    rain_v = CloudMicrophysicsDynamics.terminal_velocity_hydrometeor(diameter, species="rain")
    ice_v = CloudMicrophysicsDynamics.terminal_velocity_hydrometeor(diameter, species="ice_crystal")
    graupel_v = CloudMicrophysicsDynamics.terminal_velocity_hydrometeor(diameter, species="graupel")
    cloud_v = CloudMicrophysicsDynamics.terminal_velocity_hydrometeor(diameter, species="cloud_droplet")
    # All must be non-negative and species must genuinely produce different fall speeds
    assert rain_v >= 0.0 and ice_v >= 0.0 and graupel_v >= 0.0 and cloud_v >= 0.0
    assert len({rain_v, ice_v, graupel_v, cloud_v}) == 4


def test_terminal_velocity_hydrometeor_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        CloudMicrophysicsDynamics.terminal_velocity_hydrometeor(-1.0)
    with pytest.raises(ValueError):
        CloudMicrophysicsDynamics.terminal_velocity_hydrometeor(0.002, density_air=0.0)


def test_autoconversion_kessler_zero_below_threshold():
    assert CloudMicrophysicsDynamics.autoconversion_kessler(q_cloud=0.0001, q_crit=0.0005) == 0.0


def test_autoconversion_kessler_positive_above_threshold():
    result = CloudMicrophysicsDynamics.autoconversion_kessler(q_cloud=0.002, q_crit=0.0005, rate_const=0.001)
    assert result == pytest.approx(0.001 * (0.002 - 0.0005))
