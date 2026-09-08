import pytest

from acf.model4d.physics.atmospheric_waves import AtmosphericWavesPhysics


def test_wave_speed():

    value = AtmosphericWavesPhysics.wave_speed(10, 30)

    assert value == 300


def test_wavenumber():

    value = AtmosphericWavesPhysics.wavenumber(10)

    assert round(value, 3) == 0.628


def test_phase_speed():
    # CORRECTED: phase_speed used to compute wave_number/frequency
    # (the reciprocal of phase speed - a real formula bug). The
    # correct value for wave_number=100, frequency=20 is 2*pi*20/100.
    import math

    value = AtmosphericWavesPhysics.phase_speed(100, 20)

    assert value == pytest.approx(2 * math.pi * 20 / 100)


def test_phase_speed_self_consistent_with_wave_speed():
    # Strong correctness check: phase_speed(wavenumber(lambda), f)
    # must equal wave_speed(lambda, f) for any lambda, f, since both
    # describe the same physical quantity c = lambda*f = 2*pi*f/k.
    wavelength, frequency = 10.0, 30.0
    k = AtmosphericWavesPhysics.wavenumber(wavelength)
    assert AtmosphericWavesPhysics.phase_speed(k, frequency) == pytest.approx(
        AtmosphericWavesPhysics.wave_speed(wavelength, frequency)
    )


def test_phase_speed_invalid_zero_wave_number():
    with pytest.raises(ValueError):
        AtmosphericWavesPhysics.phase_speed(0, 20)


def test_wave_energy():
    # CORRECTED: wave_energy used to multiply by 23.6895833333 instead
    # of the standard 0.5 coefficient (E = 0.5*rho*omega^2*A^2) - no
    # known derivation matched the old value.
    value = AtmosphericWavesPhysics.wave_energy(1, 1.2, 2)

    assert value == pytest.approx(0.5 * 1.2 * 2**2 * 1**2)
    assert round(value, 2) == 2.4


def test_gravity_wave_speed():

    value = AtmosphericWavesPhysics.gravity_wave_speed(100)

    assert round(value, 2) == 31.32


def test_brunt_vaisala_frequency():

    value = AtmosphericWavesPhysics.brunt_vaisala_frequency(0.01, 300)

    assert round(value, 4) == 0.0181


def test_acoustic_wave_speed():

    value = AtmosphericWavesPhysics.acoustic_wave_speed(300)

    assert round(value, 2) == 347.22


def test_rossby_wave_speed():
    # CORRECTED: rossby_wave_speed used to always return -0.253303
    # regardless of input (a hard-coded fake stub). Correct formula:
    # c = -beta * L^2 (long-wave limit).
    value = AtmosphericWavesPhysics.rossby_wave_speed(1e-11, 1000000)

    assert value == pytest.approx(-1e-11 * 1000000**2)
    assert value == pytest.approx(-10.0)


def test_rossby_wave_speed_varies_with_input():
    # Regression guard: must NOT be the old hard-coded constant, and
    # must actually depend on its inputs.
    v1 = AtmosphericWavesPhysics.rossby_wave_speed(1e-11, 500000)
    v2 = AtmosphericWavesPhysics.rossby_wave_speed(1e-11, 1000000)
    assert v1 != v2
    assert v1 != pytest.approx(-0.253303)
    assert v2 != pytest.approx(-0.253303)


def test_rossby_wave_speed_is_westward():
    # Rossby waves always propagate westward relative to the mean
    # flow: c must be negative for any positive beta, radius.
    assert AtmosphericWavesPhysics.rossby_wave_speed(1e-11, 1000000) < 0


def test_inertial_frequency():

    value = AtmosphericWavesPhysics.inertial_frequency(45)

    assert round(value, 9) == 0.0001031


def test_module_exists():

    assert AtmosphericWavesPhysics is not None
