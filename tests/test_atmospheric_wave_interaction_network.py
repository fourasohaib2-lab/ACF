from acf.model4d.physics.atmospheric_wave_interaction_network import (
    AtmosphericWaveInteractionNetwork,
    WaveInteractionState,
)


def test_initialization():

    model = AtmosphericWaveInteractionNetwork()

    assert model.version == "8.95"


def test_energy_exchange():

    model = AtmosphericWaveInteractionNetwork()

    state = WaveInteractionState(
        wave_energy=10,
        propagation_speed=5,
        turbulence_level=0.2,
        convection_index=0.8,
        jet_intensity=0.6,
    )

    result = model.compute_energy_exchange(state)

    assert result > 0


def test_simulation():

    model = AtmosphericWaveInteractionNetwork()

    state = WaveInteractionState(
        wave_energy=20,
        propagation_speed=3,
        turbulence_level=0.1,
        convection_index=0.5,
        jet_intensity=0.4,
    )

    output = model.simulate(state)

    assert "wave_energy_exchange" in output
    assert "convection_response" in output
    assert "jet_response" in output
