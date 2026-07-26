from acf.model4d.physics.state_equations import StateEquations


def test_pressure():
    value = StateEquations.pressure(
        1.2,
        300
    )

    assert round(value, 2) == 103338.0


def test_density():
    value = StateEquations.density(
        101325,
        288
    )

    assert round(value, 2) == 1.23


def test_virtual_temperature():
    value = StateEquations.virtual_temperature(
        300,
        0.01
    )

    assert value == 301.83


def test_speed_of_sound():
    value = StateEquations.speed_of_sound(288)

    # Tolérance numérique physique
    assert abs(value - 340.20) < 0.01


def test_stability_unstable():
    assert StateEquations.stability(-0.01) == "Unstable"


def test_stability_neutral():
    assert StateEquations.stability(0) == "Neutral"


def test_stability_stable():
    assert StateEquations.stability(0.01) == "Stable"


def test_zero_temperature_density():
    try:
        StateEquations.density(
            100000,
            0
        )
        assert False
    except ValueError:
        assert True


def test_negative_temperature_sound():
    try:
        StateEquations.speed_of_sound(-1)
        assert False
    except ValueError:
        assert True


def test_constants():
    assert StateEquations.R_DRY_AIR == 287.05
    assert StateEquations.GAMMA == 1.4
