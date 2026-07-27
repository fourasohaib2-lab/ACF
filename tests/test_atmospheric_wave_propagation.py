from acf.model4d.physics.atmospheric_wave_propagation import (
    AtmosphericWavePropagation,
    AtmosphericWaveState
)


def test_creation():

    model = AtmosphericWavePropagation()

    assert model.version == "8.92"


def test_phase_speed():

    model = AtmosphericWavePropagation()

    state = AtmosphericWaveState(
        wavelength=1000,
        frequency=0.01,
        wind_speed=10,
        stability=2
    )

    assert model.phase_speed(state) == 10


def test_intrinsic_frequency():

    model = AtmosphericWavePropagation()

    state = AtmosphericWaveState(
        wavelength=1000,
        frequency=1,
        wind_speed=100,
        stability=2
    )

    value = model.intrinsic_frequency(state)

    assert value >= 0


def test_vertical_factor():

    model = AtmosphericWavePropagation()

    state = AtmosphericWaveState(
        wavelength=500,
        frequency=0.2,
        wind_speed=20,
        stability=3,
        altitude=10000
    )

    assert model.vertical_propagation_factor(state) == 6


def test_wave_classification():

    model = AtmosphericWavePropagation()

    state = AtmosphericWaveState(
        wavelength=500,
        frequency=0.2,
        wind_speed=20,
        stability=10
    )

    assert (
        model.classify_wave(state)
        == "Strong gravity wave"
    )


def test_rossby():

    model = AtmosphericWavePropagation()

    state = AtmosphericWaveState(
        wavelength=10000,
        frequency=0.001,
        wind_speed=5,
        stability=1,
        wave_type="rossby"
    )

    assert (
        model.classify_wave(state)
        == "Rossby wave"
    )


def test_simulation():

    model = AtmosphericWavePropagation()

    state = AtmosphericWaveState(
        wavelength=2000,
        frequency=0.05,
        wind_speed=30,
        stability=4
    )

    result = model.simulate(state)

    assert "phase_speed" in result


def test_altitude():

    state = AtmosphericWaveState(
        wavelength=1000,
        frequency=0.1,
        wind_speed=20,
        stability=2,
        altitude=5000
    )

    model = AtmosphericWavePropagation()

    assert (
        model.vertical_propagation_factor(state)
        == 3
    )


def test_zero_frequency():

    model = AtmosphericWavePropagation()

    state = AtmosphericWaveState(
        wavelength=1000,
        frequency=0,
        wind_speed=20,
        stability=1
    )

    assert model.phase_speed(state) == 0


def test_name():

    model = AtmosphericWavePropagation()

    assert (
        model.name
        ==
        "Atmospheric Wave Propagation"
    )
