"""
Tests Sprint 8.75
Solar Radiation Dynamics
"""

import pytest

from acf.model4d.physics.solar_radiation_dynamics import (
    SolarRadiationDynamics
)


def test_absorbed_by_atmosphere():
    assert (
        SolarRadiationDynamics.absorbed_by_atmosphere(
            1000,
            0.2
        )
        == 200
    )


def test_surface_reflection():
    assert (
        SolarRadiationDynamics.reflected_by_surface(
            1000,
            0.3
        )
        == 300
    )


def test_surface_absorption():
    assert (
        SolarRadiationDynamics.absorbed_by_surface(
            1000,
            0.3
        )
        == 700
    )


def test_net_radiation():
    assert (
        SolarRadiationDynamics.net_radiation(
            1000,
            0.2,
            0.3
        )
        == 500
    )


def test_greenhouse_effect():
    assert (
        SolarRadiationDynamics.greenhouse_radiative_effect(
            0.5,
            200
        )
        == 100
    )


def test_invalid_fraction():
    with pytest.raises(ValueError):
        SolarRadiationDynamics.validate_fraction(
            1.5
        )


def test_default_model():

    model = SolarRadiationDynamics()

    assert model.solar_constant == 1361.0


def test_simulation():

    model = SolarRadiationDynamics()

    result = model.simulate(1000)

    assert (
        result["net_radiation"]
        == 500
    )


def test_zero_radiation():

    assert (
        SolarRadiationDynamics.net_radiation(
            0,
            0.2,
            0.3
        )
        == 0
    )


def test_fraction_boundary():

    assert (
        SolarRadiationDynamics.validate_fraction(
            1
        )
        == 1
    )
