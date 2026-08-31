import pytest

from acf.model4d.physics.spectral_physics import SpectralPhysics


def test_wavelength_to_wavenumber():

    value = SpectralPhysics.wavelength_to_wavenumber(10)

    assert round(value, 3) == 0.628


def test_wavenumber_to_wavelength():

    value = SpectralPhysics.wavenumber_to_wavelength(0.628318)

    assert round(value, 1) == 10.0


def test_spectral_energy():

    value = SpectralPhysics.spectral_energy(2)

    assert value == 2.0


def test_fourier_component():

    value = SpectralPhysics.fourier_component(1, 0)

    assert value == 1


def test_filter():

    result = SpectralPhysics.spectral_filter([1, 5, 10], 5)

    assert result == [1, 5, 0.0]


def test_dominant_mode():

    value = SpectralPhysics.dominant_wavenumber([1, 8, 3])

    assert value == 1


def test_negative_wavelength():

    with pytest.raises(ValueError):
        SpectralPhysics.wavelength_to_wavenumber(-1)


def test_negative_wavenumber():

    with pytest.raises(ValueError):
        SpectralPhysics.wavenumber_to_wavelength(-1)


def test_negative_energy():

    with pytest.raises(ValueError):
        SpectralPhysics.spectral_energy(-2)


def test_empty_spectrum():

    with pytest.raises(ValueError):
        SpectralPhysics.dominant_wavenumber([])
