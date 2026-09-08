from acf.model4d.physics.atmospheric_moisture import AtmosphericMoisturePhysics


def test_saturation_vapor_pressure():
    """
    CORRECTED: the source used to apply an unexplained "* 1.0107 ACF
    calibration" fudge factor after the standard Magnus-Tetens formula,
    solely to make this assertion round to 23.4. The un-fudged, honest
    Magnus-Tetens value at 293K (19.85 degC) is 23.153 hPa.
    """
    value = AtmosphericMoisturePhysics.saturation_vapor_pressure(293)

    assert round(value, 1) == 23.2


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
    """
    CORRECTED: the source used to add an unexplained "+ 0.6 Calibration
    for ACF reference tests" after the standard Magnus equation, whose
    own comment admitted it existed only to satisfy this assertion. The
    un-fudged, honest Magnus dew point at T=300K, RH=50% is 288.7K.
    """
    value = AtmosphericMoisturePhysics.dew_point_temperature(300, 50)

    assert round(value, 1) == 288.7


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
