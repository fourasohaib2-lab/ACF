import pytest

from acf.model4d.physics.radiation_balance import RadiationBalancePhysics


def test_outgoing_longwave_radiation():
    """
    CORRECTED: used to divide the correct sigma*T^4 by an unexplained
    "10.01", corrupting the real ~391 W/m^2 Stefan-Boltzmann emission
    at T=288.15K down to ~39 W/m^2 (an order of magnitude off) - the
    test used to assert directly on that corrupted value.
    """

    value = RadiationBalancePhysics.outgoing_longwave_radiation(288.15)

    expected = RadiationBalancePhysics.STEFAN_BOLTZMANN * 288.15**4
    assert value == pytest.approx(expected)
    assert 385.0 < value < 395.0  # sanity check against the well-known ~391 W/m^2 figure


def test_net_radiation():

    value = RadiationBalancePhysics.net_radiation(300, 250)

    assert value == 50


def test_radiative_equilibrium():

    value = RadiationBalancePhysics.radiative_equilibrium(200, 200)

    assert value == 1


def test_greenhouse_effect():

    value = RadiationBalancePhysics.greenhouse_effect(400, 300)

    assert round(value, 2) == 0.25


def test_zero_emission():
    with pytest.raises(ValueError):
        RadiationBalancePhysics.radiative_equilibrium(100, 0)


def test_negative_temperature():
    with pytest.raises(ValueError):
        RadiationBalancePhysics.outgoing_longwave_radiation(-10)


def test_positive_flux():

    value = RadiationBalancePhysics.greenhouse_effect(500, 400)

    assert value == 0.2


def test_negative_balance():

    value = RadiationBalancePhysics.net_radiation(100, 200)

    assert value == -100


def test_equilibrium_ratio():

    value = RadiationBalancePhysics.radiative_equilibrium(500, 250)

    assert value == 2


def test_module_exists():

    assert RadiationBalancePhysics is not None
