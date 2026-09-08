import pytest

from acf.model4d.physics.chemistry_coupling import ChemistryCouplingPhysics


def test_reaction_rate():

    value = ChemistryCouplingPhysics.reaction_rate(10, 0.5)

    assert round(value, 2) == 5.0


def test_chemical_lifetime():

    value = ChemistryCouplingPhysics.chemical_lifetime(100, 10)

    assert value == 10


def test_production_rate():

    value = ChemistryCouplingPhysics.production_rate(50, 20)

    assert value == 30


def test_transport_coupling():

    value = ChemistryCouplingPhysics.chemistry_transport_coupling(2, 5)

    assert value == 10


def test_photochemical_factor():

    value = ChemistryCouplingPhysics.photochemical_factor(100)

    assert value == 1


def test_ozone_production():

    value = ChemistryCouplingPhysics.ozone_production(10, 100)

    assert value == 10


def test_negative_concentration():

    with pytest.raises(ValueError):
        ChemistryCouplingPhysics.reaction_rate(-1, 2)


def test_invalid_loss():

    with pytest.raises(ValueError):
        ChemistryCouplingPhysics.chemical_lifetime(10, 0)


def test_negative_sun():

    with pytest.raises(ValueError):
        ChemistryCouplingPhysics.photochemical_factor(-10)


def test_zero_sink():

    value = ChemistryCouplingPhysics.production_rate(0, 0)

    assert value == 0
