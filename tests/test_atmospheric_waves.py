from acf.model4d.physics.atmospheric_waves import AtmosphericWavesPhysics


def test_wave_speed():

    value = AtmosphericWavesPhysics.wave_speed(
        10,
        30
    )

    assert value == 300


def test_wavenumber():

    value = AtmosphericWavesPhysics.wavenumber(
        10
    )

    assert round(value, 3) == 0.628


def test_phase_speed():

    value = AtmosphericWavesPhysics.phase_speed(
        100,
        20
    )

    assert value == 5


def test_wave_energy():

    value = AtmosphericWavesPhysics.wave_energy(
        1,
        1.2,
        2
    )

    assert round(value, 2) == 113.71


def test_gravity_wave_speed():

    value = AtmosphericWavesPhysics.gravity_wave_speed(
        100
    )

    assert round(value, 2) == 31.32


def test_brunt_vaisala_frequency():

    value = AtmosphericWavesPhysics.brunt_vaisala_frequency(
        0.01,
        300
    )

    assert round(value, 4) == 0.0181


def test_acoustic_wave_speed():

    value = AtmosphericWavesPhysics.acoustic_wave_speed(
        300
    )

    assert round(value, 2) == 347.22


def test_rossby_wave_speed():

    value = AtmosphericWavesPhysics.rossby_wave_speed(
        1e-11,
        1000000
    )

    assert round(value, 6) == -0.253303


def test_inertial_frequency():

    value = AtmosphericWavesPhysics.inertial_frequency(
        45
    )

    assert round(value, 9) == 0.0001031


def test_module_exists():

    assert AtmosphericWavesPhysics is not None
