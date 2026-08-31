import pytest

from acf.model4d.physics.turbulence import TurbulencePhysics


def test_tke():

    value = TurbulencePhysics.turbulent_kinetic_energy(1, 1, 1)

    assert round(value, 2) == 1.50


def test_eddy_viscosity():

    value = TurbulencePhysics.eddy_viscosity(10, 0.02)

    assert round(value, 2) == 2.00


def test_mixing_length():

    value = TurbulencePhysics.mixing_length(100, 0)

    assert round(value, 1) == 40.0


def test_turbulence_intensity():

    value = TurbulencePhysics.turbulence_intensity(1.5, 10)

    assert round(value, 3) == 0.316


def test_stable():

    result = TurbulencePhysics.stability_correction(0.5)

    assert result == "stable"


def test_unstable():

    result = TurbulencePhysics.stability_correction(-0.2)

    assert result == "unstable"


def test_neutral():

    result = TurbulencePhysics.stability_correction(0.1)

    assert result == "neutral"


def test_invalid_height():

    with pytest.raises(ValueError):
        TurbulencePhysics.mixing_length(0, 1)


def test_invalid_tke():

    with pytest.raises(ValueError):
        TurbulencePhysics.turbulence_intensity(-1, 10)


def test_invalid_velocity():

    with pytest.raises(ValueError):
        TurbulencePhysics.turbulence_intensity(1, 0)
