"""
Tests for acf.science.thermodynamics.Thermodynamics (the science/ facade).

NOTE: this is distinct from acf.model4d.physics.thermodynamics.Thermodynamics,
which is a separate, unrelated class covered by tests/test_thermodynamics.py.
The duplicate class name is a known pre-existing condition, tracked in
/tmp/acf_scan_report.txt — not resolved here.
"""

import pytest

from acf.science.thermodynamics import Thermodynamics


def test_potential_temperature():
    theta = Thermodynamics.calculate_potential_temperature(300.0, 850.0)
    assert theta > 300.0


def test_equivalent_potential_temperature_simple():
    thetae = Thermodynamics.calculate_equivalent_potential_temperature(300.0, 0.01)
    assert thetae > 300.0


def test_equivalent_potential_temperature_bolton():
    thetae = Thermodynamics.calculate_equivalent_potential_temperature_bolton(300.0, 290.0, 1000.0)
    assert thetae > 300.0


def test_equivalent_potential_temperature_bolton_invalid():
    with pytest.raises(ValueError):
        Thermodynamics.calculate_equivalent_potential_temperature_bolton(290.0, 295.0, 1000.0)


def test_wet_bulb_temperature():
    tw = Thermodynamics.calculate_wet_bulb_temperature(25.0, 0.5)
    assert tw < 25.0


def test_dry_static_energy():
    s = Thermodynamics.calculate_dry_static_energy(300.0, 1000.0)
    assert s > 300000.0


def test_moist_static_energy():
    h = Thermodynamics.calculate_moist_static_energy(300.0, 1000.0, 0.01)
    assert h > Thermodynamics.calculate_dry_static_energy(300.0, 1000.0)


def test_hypsometric_thickness_positive_for_warmer_layer():
    thickness_warm = Thermodynamics.calculate_hypsometric_thickness(100000.0, 85000.0, 290.0)
    thickness_cold = Thermodynamics.calculate_hypsometric_thickness(100000.0, 85000.0, 270.0)
    assert thickness_warm > thickness_cold > 0.0
