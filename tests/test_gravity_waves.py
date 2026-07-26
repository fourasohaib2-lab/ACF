import pytest

from acf.model4d.physics.gravity_waves import (
    GravityWavesPhysics
)


def test_brunt_vaisala_frequency_squared():

    value = (
        GravityWavesPhysics
        .brunt_vaisala_frequency_squared(0.01)
    )

    assert round(value, 2) == 0.10



def test_phase_speed():

    value = (
        GravityWavesPhysics
        .wave_phase_speed(
            0.01,
            1000
        )
    )

    assert round(value, 2) == 1.59



def test_vertical_wavenumber():

    value = (
        GravityWavesPhysics
        .vertical_wavenumber(
            0.01,
            0.001
        )
    )

    assert round(value, 2) == 10



def test_slow_wave():

    assert (
        GravityWavesPhysics
        .classify_wave(5)
        ==
        "slow"
    )



def test_moderate_wave():

    assert (
        GravityWavesPhysics
        .classify_wave(20)
        ==
        "moderate"
    )



def test_fast_wave():

    assert (
        GravityWavesPhysics
        .classify_wave(80)
        ==
        "fast"
    )



def test_invalid_stability():

    with pytest.raises(ValueError):

        GravityWavesPhysics \
        .brunt_vaisala_frequency_squared(
            0
        )



def test_invalid_frequency():

    with pytest.raises(ValueError):

        GravityWavesPhysics \
        .wave_phase_speed(
            0,
            100
        )



def test_invalid_wavelength():

    with pytest.raises(ValueError):

        GravityWavesPhysics \
        .wave_phase_speed(
            1,
            0
        )



def test_invalid_wavenumber():

    with pytest.raises(ValueError):

        GravityWavesPhysics \
        .vertical_wavenumber(
            1,
            0
        )
