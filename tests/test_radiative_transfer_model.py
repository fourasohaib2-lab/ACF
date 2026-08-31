import pytest

from acf.model4d.physics.radiative_transfer_model import RadiativeTransferModelPhysics


def test_absorbed_radiation():
    assert RadiativeTransferModelPhysics.absorbed_radiation(1000, 0.3) == 300


def test_transmitted_radiation():
    assert RadiativeTransferModelPhysics.transmitted_radiation(1000, 0.3) == 700


def test_emitted_radiation():
    value = RadiativeTransferModelPhysics.emitted_radiation(300)

    assert value > 0


def test_optical_depth():
    assert RadiativeTransferModelPhysics.optical_depth(0.5, 10) == 5


def test_transmission():
    value = RadiativeTransferModelPhysics.transmission_from_optical_depth(1)

    assert 0 < value < 1


def test_radiative_balance():
    assert RadiativeTransferModelPhysics.radiative_balance(500, 300) == 200


def test_greenhouse_effect():
    value = RadiativeTransferModelPhysics.greenhouse_effect(288, 0.8)

    assert value > 0


def test_invalid_absorption():
    with pytest.raises(ValueError):
        RadiativeTransferModelPhysics.absorbed_radiation(1000, 2)


def test_invalid_temperature():
    with pytest.raises(ValueError):
        RadiativeTransferModelPhysics.emitted_radiation(-10)


def test_module_exists():
    assert RadiativeTransferModelPhysics is not None
