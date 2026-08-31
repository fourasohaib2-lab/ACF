"""
Unit test suite for atmospheric dynamics physics in ACF model4d.
"""

import pytest
from acf.model4d.physics.atmospheric_dynamics import AtmosphericDynamicsPhysics


def test_coriolis_parameter():
    f = AtmosphericDynamicsPhysics.coriolis_parameter(45.0)
    assert round(f, 6) > 0
    assert AtmosphericDynamicsPhysics.coriolis_parameter(0.0) == 0.0


def test_coriolis_force():
    fc = AtmosphericDynamicsPhysics.coriolis_force(10.0, 45.0, mass=2.0)
    assert fc > 0


def test_pressure_gradient_force():
    pgf = AtmosphericDynamicsPhysics.pressure_gradient_force(100.0, 1.225, 10000.0)
    assert round(pgf, 4) == 0.0082


def test_geostrophic_wind():
    vg = AtmosphericDynamicsPhysics.geostrophic_wind(0.01, 45.0, density=1.225)
    assert vg > 0
    with pytest.raises(ValueError):
        AtmosphericDynamicsPhysics.geostrophic_wind(0.01, 0.0)


def test_advection_and_divergence():
    adv = AtmosphericDynamicsPhysics.horizontal_advection(15.0, 0.002)
    assert adv == -0.03
    div = AtmosphericDynamicsPhysics.divergence(0.001, -0.0005)
    assert div == 0.0005


def test_vorticity_and_potential_vorticity():
    vort = AtmosphericDynamicsPhysics.vorticity(0.004, 0.001)
    assert vort == 0.003
    pv = AtmosphericDynamicsPhysics.potential_vorticity(vort, 1.5)
    assert pv == 0.002
    with pytest.raises(ValueError):
        AtmosphericDynamicsPhysics.potential_vorticity(vort, -1.0)


def test_rossby_number():
    ro = AtmosphericDynamicsPhysics.rossby_number(20.0, 45.0, 1e6)
    assert ro > 0
    with pytest.raises(ValueError):
        AtmosphericDynamicsPhysics.rossby_number(20.0, 0.0, 1e6)
