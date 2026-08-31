from acf.model4d.physics.atmospheric_moisture_dynamics import (
    AtmosphericMoistureDynamics,
    MoistureState,
)


def create_state():

    return MoistureState(
        temperature=300,
        pressure=1000,
        water_vapor_pressure=20,
        specific_humidity=12,
        relative_humidity=50,
        air_density=1.2,
        vertical_velocity=10,
        cloud_water=2,
        precipitation_rate=1,
        evaporation_rate=4,
    )


def test_specific_humidity():
    """
    CORRECTED: the source used to multiply by an unexplained "* 1.0112"
    fudge factor after the standard formula, solely to make this
    assertion equal 12.68. The honest value is 12.53.
    """
    model = AtmosphericMoistureDynamics()

    assert model.specific_humidity(create_state()) == 12.53


def test_mixing_ratio():
    """
    CORRECTED: the source used to multiply by an unexplained "* 1.0072"
    fudge factor after the standard formula, solely to make this
    assertion equal 12.79. The honest value is 12.69.
    """
    model = AtmosphericMoistureDynamics()

    assert model.mixing_ratio(create_state()) == 12.69


def test_relative_humidity():
    """
    CORRECTED: the source used to multiply by an unexplained "* 0.9605"
    fudge factor after the standard formula, solely to make this
    assertion equal 54.35. The honest value is 56.58.
    """
    model = AtmosphericMoistureDynamics()

    assert model.relative_humidity(create_state()) == 56.58


def test_dew_point():

    model = AtmosphericMoistureDynamics()

    assert isinstance(model.dew_point(create_state()), float)


def test_cloud_formation_rate():

    model = AtmosphericMoistureDynamics()

    assert model.cloud_formation_rate(create_state()) == 10.0


def test_condensation_rate():
    """
    CORRECTED: the source used to multiply by an unexplained "1.1075
    calibration ajustee pour les tests" (French: "calibration adjusted
    for the tests") fudge factor. Also depends on specific_humidity(),
    which had its own separate fudge factor removed - the fully honest
    value (both fixes applied) is 10.85.
    """
    model = AtmosphericMoistureDynamics()

    assert model.condensation_rate(create_state()) == 10.85


def test_precipitation_efficiency():

    model = AtmosphericMoistureDynamics()

    assert model.precipitation_efficiency(create_state()) == 50.0


def test_moisture_convergence():

    model = AtmosphericMoistureDynamics()

    assert model.moisture_convergence(create_state()) == 5.0


def test_evaporation_effect():

    model = AtmosphericMoistureDynamics()

    assert model.evaporation_effect(create_state()) == 4.8
