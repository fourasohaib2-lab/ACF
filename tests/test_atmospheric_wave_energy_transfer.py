from acf.model4d.physics.atmospheric_wave_energy_transfer import (
    AtmosphericWaveEnergyTransfer,
    WaveEnergyState
)


def test_creation():
    model = AtmosphericWaveEnergyTransfer()
    assert model.version == "8.93"


def test_energy_density():
    state = WaveEnergyState(
        amplitude=10,
        frequency=1,
        density=2,
        propagation_distance=10
    )

    model = AtmosphericWaveEnergyTransfer()

    assert model.energy_density(state) == 100


def test_attenuation_zero():

    model = AtmosphericWaveEnergyTransfer()

    state = WaveEnergyState(
        amplitude=5,
        frequency=1,
        density=1,
        propagation_distance=10,
        damping=0
    )

    assert model.attenuation(state) == 1


def test_attenuation():

    model = AtmosphericWaveEnergyTransfer()

    state = WaveEnergyState(
        amplitude=5,
        frequency=1,
        density=1,
        propagation_distance=10,
        damping=0.05
    )

    assert model.attenuation(state) == 0.5


def test_transfer():

    model = AtmosphericWaveEnergyTransfer()

    state = WaveEnergyState(
        amplitude=20,
        frequency=2,
        density=1,
        propagation_distance=5
    )

    assert model.transferred_energy(state) == 200


def test_classification():

    model = AtmosphericWaveEnergyTransfer()

    state = WaveEnergyState(
        amplitude=20,
        frequency=1,
        density=1,
        propagation_distance=1
    )

    assert model.classify_transfer(state) == "Strong transfer"


def test_simulation():

    model = AtmosphericWaveEnergyTransfer()

    state = WaveEnergyState(
        amplitude=10,
        frequency=1,
        density=2,
        propagation_distance=2
    )

    result = model.simulate(state)

    assert "transferred_energy" in result


def test_weak_transfer():

    model = AtmosphericWaveEnergyTransfer()

    state = WaveEnergyState(
        amplitude=1,
        frequency=1,
        density=1,
        propagation_distance=1
    )

    assert (
        model.classify_transfer(state)
        == "Weak transfer"
    )


def test_high_damping():

    model = AtmosphericWaveEnergyTransfer()

    state = WaveEnergyState(
        amplitude=10,
        frequency=1,
        density=1,
        propagation_distance=100,
        damping=1
    )

    assert model.attenuation(state) == 0


def test_name():

    model = AtmosphericWaveEnergyTransfer()

    assert (
        model.name
        ==
        "Atmospheric Wave Energy Transfer"
    )
