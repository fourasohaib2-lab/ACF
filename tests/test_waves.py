import pytest

from acf.model4d.physics.waves import Waves


def test_wavelength():
    value = Waves.wavelength(10, 5)
    assert value == 50


def test_frequency():
    value = Waves.frequency(20)
    assert value == 0.05


def test_phase_speed():
    value = Waves.phase_speed(100, 10)
    assert value == 10


def test_gravity_wave_speed():
    value = Waves.gravity_wave_speed(100)
    assert round(value, 2) == 31.32


def test_negative_period_wavelength():
    with pytest.raises(ValueError):
        Waves.wavelength(10, -1)


def test_zero_period_frequency():
    with pytest.raises(ValueError):
        Waves.frequency(0)


def test_zero_period_phase_speed():
    with pytest.raises(ValueError):
        Waves.phase_speed(100, 0)


def test_negative_height():
    with pytest.raises(ValueError):
        Waves.gravity_wave_speed(-10)


def test_frequency_relation():
    assert Waves.frequency(10) == 0.1


def test_wave_consistency():
    c = Waves.phase_speed(200, 20)
    assert c == 10
