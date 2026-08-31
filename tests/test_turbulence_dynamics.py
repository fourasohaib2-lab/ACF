import pytest

from acf.model4d.physics.turbulence_dynamics import (
    TurbulenceDynamics,
    TurbulenceState,
)


def test_tke():
    model = TurbulenceDynamics()

    value = model.turbulent_kinetic_energy(4)

    assert value == 6


def test_intensity():
    model = TurbulenceDynamics()

    value = model.turbulence_intensity(4, 10)

    assert value == 0.2


def test_diffusivity():
    model = TurbulenceDynamics()

    value = model.eddy_diffusivity(50, 2)

    assert value == 100


def test_timescale():
    model = TurbulenceDynamics()

    value = model.dissipation_timescale(10, 2)

    assert value == 5


def test_analysis():
    model = TurbulenceDynamics()

    state = TurbulenceState(wind_speed=10, velocity_variance=4, dissipation_rate=2, mixing_length=50)

    result = model.analyze(state)

    assert result["tke"] == 6
    assert result["eddy_diffusivity"] == 100


def test_name():
    model = TurbulenceDynamics()

    assert model.name == "Turbulence Dynamics"


def test_version():
    model = TurbulenceDynamics()

    assert model.version == "1.0"


def test_negative_variance():
    model = TurbulenceDynamics()

    with pytest.raises(ValueError):
        model.turbulent_kinetic_energy(-1)


def test_zero_wind():
    model = TurbulenceDynamics()

    with pytest.raises(ValueError):
        model.turbulence_intensity(1, 0)


def test_negative_mixing():
    model = TurbulenceDynamics()

    with pytest.raises(ValueError):
        model.eddy_diffusivity(-1, 2)
