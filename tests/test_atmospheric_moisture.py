from acf.model4d.physics.atmospheric_moisture import AtmosphericMoisturePhysics


def test_saturation_vapor_pressure():

    value = AtmosphericMoisturePhysics.saturation_vapor_pressure(293)

    assert round(value, 1) == 23.4


def test_relative_humidity():

    value = AtmosphericMoisturePhysics.relative_humidity(10, 20)

    assert value == 50


def test_mixing_ratio():

    value = AtmosphericMoisturePhysics.mixing_ratio(10, 1000)

    assert value == 6.276


def test_specific_humidity():

    value = AtmosphericMoisturePhysics.specific_humidity(10)

    assert value == 0.009901


def test_dew_point():

    value = AtmosphericMoisturePhysics.dew_point_temperature(300, 50)

    assert round(value, 1) == 289.3


def test_precipitable_water():

    value = AtmosphericMoisturePhysics.precipitable_water(5, 1000)

    assert value == 5


def test_cloud_water():

    value = AtmosphericMoisturePhysics.cloud_water_content(2, 0.5)

    assert value == 1


def test_evaporation():

    value = AtmosphericMoisturePhysics.evaporation_rate(300, 50)

    assert value == 13.425


def test_flux():

    value = AtmosphericMoisturePhysics.moisture_flux(10, 2)

    assert value == 20


def test_condensation():

    value = AtmosphericMoisturePhysics.condensation_rate(120)

    assert value == 0.2
