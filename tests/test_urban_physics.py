import pytest

from acf.model4d.physics.urban_physics import UrbanPhysics


def test_heat_island():

    value = UrbanPhysics.urban_heat_island(35, 30)

    assert value == 5


def test_surface_storage():

    value = UrbanPhysics.surface_storage(100, 2)

    assert value == 200


def test_roughness():

    value = UrbanPhysics.urban_roughness(20, 100)

    assert round(value, 3) == 0.02


def test_anthropogenic_flux():

    value = UrbanPhysics.anthropogenic_flux(1000, 2)

    assert value == 2000


def test_classification_weak():

    assert UrbanPhysics.classify_environment(0.5) == "weak"


def test_classification_moderate():

    assert UrbanPhysics.classify_environment(2) == "moderate"


def test_classification_strong():

    assert UrbanPhysics.classify_environment(5) == "strong"


def test_temperature_response():

    value = UrbanPhysics.urban_temperature_response(100, 0.2)

    assert value == 80


def test_invalid_albedo():

    with pytest.raises(ValueError):
        UrbanPhysics.urban_temperature_response(100, 2)


def test_invalid_height():

    with pytest.raises(ValueError):
        UrbanPhysics.urban_roughness(0, 50)
