from acf.model4d.physics.turbulence import Turbulence


def test_tke():
    value = Turbulence.tke(
        2,
        1,
        1
    )

    assert value == 3.0


def test_dissipation():
    value = Turbulence.dissipation(
        10,
        2
    )

    assert value == 5


def test_dissipation_error():
    try:
        Turbulence.dissipation(10, 0)
        assert False
    except ValueError:
        assert True


def test_mixing():
    value = Turbulence.mixing_length_coefficient(
        100,
        2
    )

    assert value == 200


def test_intensity():
    value = Turbulence.intensity(
        6,
        10
    )

    assert round(value, 3) == 0.2


def test_zero_tke():
    assert Turbulence.tke(0, 0, 0) == 0


def test_positive_values():
    assert Turbulence.tke(1, 1, 1) > 0


def test_large_scale():
    assert Turbulence.mixing_length_coefficient(
        1000,
        5
    ) == 5000


def test_negative_velocity_error():
    try:
        Turbulence.intensity(5, -1)
        assert False
    except ValueError:
        assert True


def test_type():
    assert isinstance(
        Turbulence.tke(1, 2, 3),
        float
    )
