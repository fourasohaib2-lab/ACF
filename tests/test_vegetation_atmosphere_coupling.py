from acf.model4d.physics.vegetation_atmosphere_coupling import (
    VegetationAtmosphereCouplingPhysics
)


def test_transpiration_rate():
    value = VegetationAtmosphereCouplingPhysics.transpiration_rate(
        100,
        20
    )
    assert value == 5


def test_canopy_temperature_effect():
    value = VegetationAtmosphereCouplingPhysics.canopy_temperature_effect(
        300,
        20
    )
    assert value == 280


def test_leaf_area_index():
    value = VegetationAtmosphereCouplingPhysics.leaf_area_index(
        500,
        100
    )
    assert value == 5


def test_evapotranspiration_coupling():
    value = VegetationAtmosphereCouplingPhysics.evapotranspiration_coupling(
        50,
        30
    )
    assert value == 80


def test_vegetation_moisture_feedback():
    value = VegetationAtmosphereCouplingPhysics.vegetation_moisture_feedback(
        40,
        2
    )
    assert value == 80


def test_albedo_vegetation_effect():
    value = VegetationAtmosphereCouplingPhysics.albedo_vegetation_effect(
        0.2,
        100
    )
    assert value == 80


def test_carbon_flux():
    value = VegetationAtmosphereCouplingPhysics.carbon_flux(
        300,
        100
    )
    assert value == 200


def test_vegetation_heat_flux():
    value = VegetationAtmosphereCouplingPhysics.vegetation_heat_flux(
        200,
        0.5
    )
    assert value == 100


def test_humidity_feedback():
    value = VegetationAtmosphereCouplingPhysics.humidity_feedback(
        50,
        2
    )
    assert value == 100


def test_surface_exchange_rate():
    value = VegetationAtmosphereCouplingPhysics.surface_exchange_rate(
        70,
        30
    )
    assert value == 100

