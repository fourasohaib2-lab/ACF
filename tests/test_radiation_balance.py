from acf.model4d.physics.radiation_balance import (
    RadiationBalancePhysics
)


def test_outgoing_longwave_radiation():

    value = RadiationBalancePhysics.outgoing_longwave_radiation(
        288.15
    )

    assert round(value, 2) == 39.05



def test_net_radiation():

    value = RadiationBalancePhysics.net_radiation(
        300,
        250
    )

    assert value == 50



def test_radiative_equilibrium():

    value = RadiationBalancePhysics.radiative_equilibrium(
        200,
        200
    )

    assert value == 1



def test_greenhouse_effect():

    value = RadiationBalancePhysics.greenhouse_effect(
        400,
        300
    )

    assert round(value, 2) == 0.25



def test_zero_emission():

    try:
        RadiationBalancePhysics.radiative_equilibrium(
            100,
            0
        )
        assert False
    except ValueError:
        assert True



def test_negative_temperature():

    try:
        RadiationBalancePhysics.outgoing_longwave_radiation(
            -10
        )
        assert False
    except ValueError:
        assert True



def test_positive_flux():

    value = RadiationBalancePhysics.greenhouse_effect(
        500,
        400
    )

    assert value == 0.2



def test_negative_balance():

    value = RadiationBalancePhysics.net_radiation(
        100,
        200
    )

    assert value == -100



def test_equilibrium_ratio():

    value = RadiationBalancePhysics.radiative_equilibrium(
        500,
        250
    )

    assert value == 2



def test_module_exists():

    assert RadiationBalancePhysics is not None
