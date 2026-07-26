from acf.model4d.physics.precipitation import Precipitation


def test_default_state():
    p = Precipitation()

    assert p.rain_rate == 0.0
    assert p.cloud_water == 0.0


def test_condensation():
    p = Precipitation(cloud_water=2.0)

    value = p.condensation_rate()

    assert value == 0.2


def test_efficiency():
    p = Precipitation(
        rain_rate=5.0,
        cloud_water=10.0
    )

    value = p.precipitation_efficiency()

    assert 0 <= value <= 1


def test_evaporation():
    p = Precipitation(
        rain_rate=10,
        temperature=300
    )

    assert p.evaporation_loss() == 0.5


def test_cold_evaporation():
    p = Precipitation(
        rain_rate=10,
        temperature=260
    )

    assert p.evaporation_loss() == 0


def test_update():
    p = Precipitation(
        cloud_water=5
    )

    result = p.update()

    assert result >= 0


def test_positive_rain():
    p = Precipitation(
        rain_rate=1
    )

    assert p.rain_rate > 0


def test_no_negative_rain():
    p = Precipitation(
        rain_rate=0
    )

    p.update()

    assert p.rain_rate >= 0


def test_temperature_effect():
    warm = Precipitation(
        rain_rate=10,
        temperature=300
    )

    cold = Precipitation(
        rain_rate=10,
        temperature=250
    )

    assert warm.evaporation_loss() > cold.evaporation_loss()


def test_module_creation():
    p = Precipitation()

    assert isinstance(p, Precipitation)
