from acf.model4d.physics.land_surface_atmosphere_exchange import (
    LandSurfaceAtmosphereExchange,
    SurfaceExchangeState,
)


def test_surface_energy_balance():

    model = LandSurfaceAtmosphereExchange()

    state = SurfaceExchangeState(
        net_radiation=100,
        soil_temperature=20,
        air_temperature=15,
        soil_moisture=0.5,
        vegetation_fraction=0.8,
        albedo=0.25,
    )

    assert model.surface_energy_balance(state) == 60.0


def test_soil_heat_flux():

    model = LandSurfaceAtmosphereExchange()

    state = SurfaceExchangeState(
        net_radiation=100,
        soil_temperature=20,
        air_temperature=15,
        soil_moisture=0.5,
        vegetation_fraction=0.8,
        albedo=0.25,
    )

    assert model.soil_heat_flux(state) == 2.5


def test_evapotranspiration():

    model = LandSurfaceAtmosphereExchange()

    state = SurfaceExchangeState(
        net_radiation=100,
        soil_temperature=20,
        air_temperature=15,
        soil_moisture=0.5,
        vegetation_fraction=0.8,
        albedo=0.25,
    )

    assert model.evapotranspiration(state) == 4.0


def test_surface_albedo_effect():

    model = LandSurfaceAtmosphereExchange()

    state = SurfaceExchangeState(
        net_radiation=100,
        soil_temperature=20,
        air_temperature=15,
        soil_moisture=0.5,
        vegetation_fraction=0.8,
        albedo=0.25,
    )

    assert model.surface_albedo_effect(state) == 25.0


def test_soil_moisture_feedback():

    model = LandSurfaceAtmosphereExchange()

    state = SurfaceExchangeState(
        net_radiation=100,
        soil_temperature=20,
        air_temperature=15,
        soil_moisture=0.5,
        vegetation_fraction=0.8,
        albedo=0.25,
    )

    assert model.soil_moisture_feedback(state) == 0.38


def test_radiative_exchange():

    model = LandSurfaceAtmosphereExchange()

    state = SurfaceExchangeState(
        net_radiation=100,
        soil_temperature=20,
        air_temperature=15,
        soil_moisture=0.5,
        vegetation_fraction=0.8,
        albedo=0.25,
    )

    assert model.radiative_exchange(state) == 75.0
