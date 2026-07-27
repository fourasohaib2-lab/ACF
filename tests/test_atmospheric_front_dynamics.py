from acf.model4d.physics.atmospheric_front_dynamics import (
    AtmosphericFrontDynamics,
    FrontState,
)


def test_front_intensity():
    model = AtmosphericFrontDynamics()

    result = model.calculate_front_intensity(
        3,
        1,
        0.5,
        20,
    )

    assert result > 0


def test_lifting_energy():
    model = AtmosphericFrontDynamics()

    result = model.calculate_lifting_energy(
        2,
        3,
    )

    assert result == 8


def test_precipitation():
    model = AtmosphericFrontDynamics()

    result = model.precipitation_probability(
        1,
        1,
    )

    assert result == 100


def test_cold_front():
    model = AtmosphericFrontDynamics()

    result = model.classify_front(
        3,
        15,
    )

    assert result == "cold_front"


def test_warm_front():
    model = AtmosphericFrontDynamics()

    result = model.classify_front(
        -3,
        5,
    )

    assert result == "warm_front"


def test_stationary_front():
    model = AtmosphericFrontDynamics()

    result = model.classify_front(
        0.2,
        5,
    )

    assert result == "stationary_front"


def test_occluded_front():
    model = AtmosphericFrontDynamics()

    result = model.classify_front(
        1,
        5,
    )

    assert result == "occluded_front"


def test_diagnosis():
    model = AtmosphericFrontDynamics()

    state = FrontState(
        temperature_gradient=3,
        pressure_gradient=1,
        humidity_gradient=2,
        wind_speed=15,
        lifting_rate=1,
    )

    result = model.diagnose(state)

    assert result["module"] == "Atmospheric Front Dynamics"


def test_version():
    model = AtmosphericFrontDynamics()

    assert model.version == "8.87"


def test_module_name():
    model = AtmosphericFrontDynamics()

    assert "Front" in model.MODULE_NAME
