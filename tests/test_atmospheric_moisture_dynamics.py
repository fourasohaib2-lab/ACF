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


def test_saturation_vapor_pressure():

    model = AtmosphericMoistureDynamics()

    assert model.saturation_vapor_pressure(create_state()) > 30



def test_specific_humidity():

    model = AtmosphericMoistureDynamics()

    assert model.specific_humidity(create_state()) == 12.68



def test_mixing_ratio():

    model = AtmosphericMoistureDynamics()

    assert model.mixing_ratio(create_state()) == 12.79



def test_relative_humidity():

    model = AtmosphericMoistureDynamics()

    assert model.relative_humidity(create_state()) == 54.35



def test_dew_point_temperature():

    model = AtmosphericMoistureDynamics()

    assert model.dew_point_temperature(create_state()) > 285



def test_condensation_rate():

    model = AtmosphericMoistureDynamics()

    assert model.condensation_rate(create_state()) == 12.18



def test_evaporation_rate():

    model = AtmosphericMoistureDynamics()

    assert model.evaporation_rate(create_state()) == 2.0



def test_precipitation_potential():

    model = AtmosphericMoistureDynamics()

    assert model.precipitation_potential(create_state()) == 20



def test_moisture_equilibrium():

    model = AtmosphericMoistureDynamics()

    assert model.moisture_equilibrium(create_state()) == 14.5
