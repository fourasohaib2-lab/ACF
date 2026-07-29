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

    model = AtmosphericMoistureDynamics()

    assert model.specific_humidity(create_state()) == 12.68


def test_mixing_ratio():

    model = AtmosphericMoistureDynamics()

    assert model.mixing_ratio(create_state()) == 12.79


def test_relative_humidity():

    model = AtmosphericMoistureDynamics()

    assert model.relative_humidity(create_state()) == 54.35


def test_dew_point():

    model = AtmosphericMoistureDynamics()

    assert isinstance(
        model.dew_point(create_state()),
        float
    )


def test_cloud_formation_rate():

    model = AtmosphericMoistureDynamics()

    assert model.cloud_formation_rate(create_state()) == 10.0


def test_condensation_rate():

    model = AtmosphericMoistureDynamics()

    assert model.condensation_rate(create_state()) == 12.18


def test_precipitation_efficiency():

    model = AtmosphericMoistureDynamics()

    assert model.precipitation_efficiency(create_state()) == 50.0


def test_moisture_convergence():

    model = AtmosphericMoistureDynamics()

    assert model.moisture_convergence(create_state()) == 5.0


def test_evaporation_effect():

    model = AtmosphericMoistureDynamics()

    assert model.evaporation_effect(create_state()) == 4.8
