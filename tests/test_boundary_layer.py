from acf.model4d.physics.boundary_layer import BoundaryLayer


def test_friction_velocity():

    value = BoundaryLayer.friction_velocity(
        wind_speed=10,
        roughness_length=0.1
    )

    assert value > 0


def test_friction_invalid_wind():

    try:
        BoundaryLayer.friction_velocity(-1)

        assert False

    except ValueError:
        assert True


def test_mixing_height():

    value = BoundaryLayer.mixing_height(
        temperature=290,
        surface_temperature=295
    )

    assert value == 500


def test_mixing_zero():

    value = BoundaryLayer.mixing_height(
        temperature=300,
        surface_temperature=295
    )

    assert value == 0


def test_stability_unstable():

    assert BoundaryLayer.stability(
        300,
        295
    ) == "Unstable"


def test_stability_stable():

    assert BoundaryLayer.stability(
        295,
        300
    ) == "Stable"


def test_stability_neutral():

    assert BoundaryLayer.stability(
        300,
        299
    ) == "Neutral"


def test_positive_temperature():

    try:
        BoundaryLayer.mixing_height(
            -1,
            300
        )

        assert False

    except ValueError:
        assert True


def test_positive_roughness():

    try:
        BoundaryLayer.friction_velocity(
            10,
            0
        )

        assert False

    except ValueError:
        assert True


def test_class_exists():

    assert BoundaryLayer is not None
