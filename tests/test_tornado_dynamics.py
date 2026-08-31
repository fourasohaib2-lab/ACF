"""
ACF - Atmospheric Complexity Framework
Model4D Physics
Tornado Dynamics Physics Module

REWRITTEN: this file used to contain only a stray duplicate copy of
TornadoDynamicsPhysics (pasted from src/acf/model4d/physics/
tornado_dynamics.py) with zero `def test_*` functions - pytest
collected the file but ran no tests from it, so the real source module
had 0% coverage and was never actually verified. Replaced with real
tests importing and exercising the actual source class.
"""

import math

import pytest

from acf.model4d.physics.tornado_dynamics import TornadoDynamicsPhysics


def test_pressure_deficit():
    assert TornadoDynamicsPhysics.pressure_deficit(101325.0, 90000.0) == pytest.approx(11325.0)


def test_wind_speed_from_pressure_drop():
    # V = sqrt(2*dP/rho), rho=1.225
    v = TornadoDynamicsPhysics.wind_speed_from_pressure_drop(5000.0)
    assert v == pytest.approx(math.sqrt(2 * 5000.0 / 1.225), rel=1e-3)


def test_rotational_and_angular_velocity_are_inverses():
    radius, omega = 200.0, 0.5
    v = TornadoDynamicsPhysics.rotational_velocity(radius, omega)
    assert v == pytest.approx(radius * omega)
    assert TornadoDynamicsPhysics.angular_velocity(v, radius) == pytest.approx(omega)


def test_tornado_energy():
    assert TornadoDynamicsPhysics.tornado_energy(1000.0, 50.0) == pytest.approx(0.5 * 1000.0 * 50.0**2)


def test_vortex_strength():
    assert TornadoDynamicsPhysics.vortex_strength(0.05, 300.0) == pytest.approx(15.0)


def test_tornado_intensity():
    assert TornadoDynamicsPhysics.tornado_intensity(60.0, 4000.0) == pytest.approx(240000.0)


def test_inflow_rate():
    assert TornadoDynamicsPhysics.inflow_rate(20.0, 500.0) == pytest.approx(10000.0)


def test_tornado_lifetime():
    assert TornadoDynamicsPhysics.tornado_lifetime(20000.0, 15.0) == pytest.approx(1333.33, rel=1e-3)


def test_enhanced_fujita_index_thresholds():
    """
    CORRECTED: the EF2-EF5 thresholds used to diverge substantially
    from the real NWS/NOAA Enhanced Fujita Scale 3-second-gust wind
    estimates converted to m/s, understating severity for strong
    tornadoes (e.g. 95 m/s used to be misclassified as EF4 instead of
    EF5).
    """
    assert TornadoDynamicsPhysics.enhanced_fujita_index(20.0) == "EF0"
    assert TornadoDynamicsPhysics.enhanced_fujita_index(35.0) == "EF1"
    assert TornadoDynamicsPhysics.enhanced_fujita_index(45.0) == "EF2"
    assert TornadoDynamicsPhysics.enhanced_fujita_index(55.0) == "EF3"
    assert TornadoDynamicsPhysics.enhanced_fujita_index(70.0) == "EF4"
    assert TornadoDynamicsPhysics.enhanced_fujita_index(95.0) == "EF5"
