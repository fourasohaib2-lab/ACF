from acf.model4d.physics.atmospheric_dynamics import (
    AtmosphericDynamicsPhysics
)


def test_coriolis_parameter():

    value = AtmosphericDynamicsPhysics.coriolis_parameter(
        45
    )

    assert round(value, 6) == 0.000103


def test_coriolis_force():

    value = AtmosphericDynamicsPhysics.coriolis_force(
        10,
        45
    )

    assert value == 0.001031


def test_pressure_gradient_force():

    value = AtmosphericDynamicsPhysics.pressure_gradient_force(
        100,
        1,
        1000
    )

    assert value == 0.1


def test_geostrophic_wind():

    value = AtmosphericDynamicsPhysics.geostrophic_wind(
        0.01,
        45
    )

    assert value > 0


def test_horizontal_advection():

    value = AtmosphericDynamicsPhysics.horizontal_advection(
        10,
        2
    )

    assert value == -20


def test_divergence():

    value = AtmosphericDynamicsPhysics.divergence(
        1,
        2
    )

    assert value == 3


def test_vorticity():

    value = AtmosphericDynamicsPhysics.vorticity(
        5,
        2
    )

    assert value == 3


def test_potential_vorticity():

    value = AtmosphericDynamicsPhysics.potential_vorticity(
        10,
        2
    )

    assert value == 5


def test_rossby_number():

    value = AtmosphericDynamicsPhysics.rossby_number(
        10,
        45,
        100000
    )

    assert value > 0


def test_invalid_latitude():

    try:
        AtmosphericDynamicsPhysics.coriolis_parameter(
            100
        )
        assert False

    except ValueError:
        assert True
