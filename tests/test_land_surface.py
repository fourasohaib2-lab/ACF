from acf.model4d.physics.land_surface import LandSurface


def test_soil_temperature():
    value = LandSurface.soil_temperature(
        100,
        10
    )

    assert value == 10


def test_invalid_heat_capacity():
    try:
        LandSurface.soil_temperature(100, 0)
        assert False
    except ValueError:
        assert True


def test_soil_moisture_balance():
    value = LandSurface.soil_moisture_balance(
        50,
        20,
        10
    )

    assert value == 60


def test_soil_moisture_not_negative():
    value = LandSurface.soil_moisture_balance(
        5,
        0,
        20
    )

    assert value == 0


def test_evaporation():
    value = LandSurface.evaporation_rate(
        300,
        0.5
    )

    assert value > 0


def test_evaporation_freezing():
    value = LandSurface.evaporation_rate(
        -5,
        0.5
    )

    assert value == 0


def test_sensible_heat_flux():
    value = LandSurface.sensible_heat_flux(
        300,
        290
    )

    assert value == 100


def test_energy_balance():
    value = LandSurface.energy_balance(
        500,
        100,
        200,
        50
    )

    assert value == 150


def test_class_exists():
    assert LandSurface is not None


def test_constant():
    assert LandSurface.STEFAN_BOLTZMANN > 0
