import pytest

from acf.model4d.physics.radiative_transfer import (
    RadiativeTransferPhysics
)


def test_stefan_boltzmann():
    value = (
        RadiativeTransferPhysics
        .stefan_boltzmann_flux(300)
    )

    assert round(value, 2) == 459.3


def test_absorbed_flux():
    value = (
        RadiativeTransferPhysics
        .absorbed_solar_flux(
            1000,
            0.3
        )
    )

    assert value == 700


def test_transmission():
    value = (
        RadiativeTransferPhysics
        .atmospheric_transmission(1)
    )

    assert round(value, 2) == 0.37


def test_emission():
    value = (
        RadiativeTransferPhysics
        .emitted_radiation(
            1,
            300
        )
    )

    assert round(value, 2) == 459.3


def test_equilibrium():
    value = (
        RadiativeTransferPhysics
        .radiative_equilibrium(
            459.3
        )
    )

    assert round(value) == 300


def test_warming():
    assert (
        RadiativeTransferPhysics
        .classify_radiative_state(10)
        ==
        "warming"
    )


def test_cooling():
    assert (
        RadiativeTransferPhysics
        .classify_radiative_state(-10)
        ==
        "cooling"
    )


def test_equilibrium_state():
    assert (
        RadiativeTransferPhysics
        .classify_radiative_state(0)
        ==
        "equilibrium"
    )


def test_invalid_temperature():

    with pytest.raises(ValueError):

        RadiativeTransferPhysics\
        .stefan_boltzmann_flux(0)


def test_invalid_albedo():

    with pytest.raises(ValueError):

        RadiativeTransferPhysics\
        .absorbed_solar_flux(
            1000,
            2
        )
