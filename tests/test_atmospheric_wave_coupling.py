from acf.model4d.physics.atmospheric_wave_coupling import (
    AtmosphericWaveCoupling,
    AtmosphericWaveState,
)


def test_creation():

    state = AtmosphericWaveState(
        amplitude=2,
        wavelength=100,
        frequency=0.1
    )

    assert state.amplitude == 2



def test_phase_speed():

    model = AtmosphericWaveCoupling()

    state = AtmosphericWaveState(
        amplitude=2,
        wavelength=100,
        frequency=0.1
    )

    assert model.phase_speed(state) == 10



def test_energy():

    model = AtmosphericWaveCoupling()

    state = AtmosphericWaveState(
        amplitude=4,
        wavelength=100,
        frequency=0.1
    )

    assert model.wave_energy(state) == 8



def test_gravity():

    model = AtmosphericWaveCoupling()

    state = AtmosphericWaveState(
        amplitude=1,
        wavelength=50,
        frequency=0.2
    )

    assert model.gravity_wave_effect(state) > 9



def test_wind():

    model = AtmosphericWaveCoupling()

    state = AtmosphericWaveState(
        amplitude=1,
        wavelength=50,
        frequency=0.2,
        wind_speed=20
    )

    assert model.wind_coupling(state) == 4



def test_coupling():

    model = AtmosphericWaveCoupling()

    state = AtmosphericWaveState(
        amplitude=3,
        wavelength=100,
        frequency=0.1,
        wind_speed=10
    )

    result = model.coupling_index(state)

    assert result > 0



def test_simulation():

    model = AtmosphericWaveCoupling()

    state = AtmosphericWaveState(
        amplitude=5,
        wavelength=200,
        frequency=0.05,
        wind_speed=30
    )

    output = model.simulate(state)

    assert "phase_speed" in output
    assert "energy" in output



def test_altitude():

    state = AtmosphericWaveState(
        amplitude=2,
        wavelength=100,
        frequency=0.1,
        altitude=12000
    )

    assert state.altitude == 12000



def test_frequency():

    state = AtmosphericWaveState(
        amplitude=1,
        wavelength=100,
        frequency=0.5
    )

    assert state.frequency == 0.5



def test_model():

    model = AtmosphericWaveCoupling()

    assert model.gravity > 9
