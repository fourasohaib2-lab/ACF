"""
Tests Sprint 8.98
Atmospheric Wave Ocean Coupling
"""

from acf.model4d.physics.atmospheric_wave_ocean_coupling import (
    AtmosphericWaveOceanCoupling,
    AtmosphericWaveState,
    OceanSurfaceState,
)


def create_states():

    wave = AtmosphericWaveState(amplitude=5, frequency=0.2, wavelength=100, phase=0)

    ocean = OceanSurfaceState(sea_surface_temperature=300, mixed_layer_depth=50, current_velocity=2, surface_stress=0.8)

    return wave, ocean


def test_wave_state():

    wave, _ = create_states()

    assert wave.amplitude == 5
    assert wave.frequency == 0.2


def test_ocean_state():

    _, ocean = create_states()

    assert ocean.mixed_layer_depth == 50
    assert ocean.surface_stress == 0.8


def test_engine_creation():

    model = AtmosphericWaveOceanCoupling()

    assert model.name == "Atmospheric Wave Ocean Coupling"


def test_momentum_exchange():

    wave, ocean = create_states()

    model = AtmosphericWaveOceanCoupling()

    value = model.calculate_momentum_exchange(wave, ocean)

    assert value > 0


def test_heat_flux():

    wave, ocean = create_states()

    model = AtmosphericWaveOceanCoupling()

    value = model.calculate_heat_flux_exchange(wave, ocean)

    assert value > 0


def test_energy_transfer():

    wave, ocean = create_states()

    model = AtmosphericWaveOceanCoupling()

    value = model.calculate_energy_transfer(wave, ocean)

    assert value > 0


def test_damping():

    _, ocean = create_states()

    model = AtmosphericWaveOceanCoupling()

    damping = model.calculate_wave_damping(ocean)

    assert 0 < damping <= 1


def test_simulation():

    wave, ocean = create_states()

    model = AtmosphericWaveOceanCoupling()

    result = model.simulate(wave, ocean)

    assert result.energy_transfer > 0
    assert result.climate_interaction_index > 0


def test_negative_current():

    wave = AtmosphericWaveState(amplitude=3, frequency=0.1, wavelength=50)

    ocean = OceanSurfaceState(
        sea_surface_temperature=290, mixed_layer_depth=20, current_velocity=-5, surface_stress=0.5
    )

    model = AtmosphericWaveOceanCoupling()

    result = model.simulate(wave, ocean)

    assert result.damping_factor < 1


def test_complete_result():

    wave, ocean = create_states()

    model = AtmosphericWaveOceanCoupling()

    result = model.simulate(wave, ocean)

    assert hasattr(result, "momentum_exchange")
    assert hasattr(result, "heat_flux_exchange")
    assert hasattr(result, "energy_transfer")
