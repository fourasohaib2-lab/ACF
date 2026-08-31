"""
Tests ACF
Atmospheric Gravity Waves
Sprint 8.85
"""

from acf.model4d.physics.atmospheric_gravity_waves import (
    AtmosphericGravityWave,
    GravityWaveState,
)


def create_wave():

    return AtmosphericGravityWave(
        GravityWaveState(
            stability_frequency=0.02,
            amplitude=100,
            wavelength=40000,
            wind_speed=20,
            density=1.1,
            dissipation_rate=0.1,
        )
    )


def test_phase_speed():

    wave = create_wave()

    assert wave.phase_speed() > 0


def test_energy():

    wave = create_wave()

    assert wave.energy() > 0


def test_propagation():

    wave = create_wave()

    assert wave.propagation_speed() > 0


def test_vertical_displacement():

    wave = create_wave()

    assert wave.vertical_displacement() == 100


def test_dissipation():

    wave = create_wave()

    assert wave.dissipation() > 0


def test_simulation():

    wave = create_wave()

    result = wave.simulate()

    assert "energy" in result


def test_state():

    wave = create_wave()

    assert isinstance(wave.state, GravityWaveState)


def test_wavelength():

    state = GravityWaveState(0.01, 50, 10000, 10, 1, 0.01)

    assert state.wavelength == 10000


def test_example():

    from acf.model4d.physics.atmospheric_gravity_waves import create_example_wave

    assert create_example_wave() is not None


def test_positive_energy():

    wave = create_wave()

    assert wave.energy() >= 0
