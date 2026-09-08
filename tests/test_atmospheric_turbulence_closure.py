from acf.model4d.physics.atmospheric_turbulence_closure import (
    AtmosphericTurbulenceClosure,
    TurbulenceState,
)


def test_tke():

    model = AtmosphericTurbulenceClosure()

    state = TurbulenceState(
        wind_shear=10, temperature_gradient=5, humidity_gradient=2, mixing_length=20, turbulent_energy=5
    )

    assert model.turbulent_kinetic_energy(state) == 10.0


def test_vertical_diffusion():

    model = AtmosphericTurbulenceClosure()

    state = TurbulenceState(
        wind_shear=10, temperature_gradient=5, humidity_gradient=2, mixing_length=20, turbulent_energy=5
    )

    assert model.vertical_diffusion(state) == 10.0


def test_mixing_coefficient():

    model = AtmosphericTurbulenceClosure()

    state = TurbulenceState(
        wind_shear=10, temperature_gradient=5, humidity_gradient=2, mixing_length=20, turbulent_energy=5
    )

    assert model.mixing_coefficient(state) == 10.0


def test_turbulence_intensity():

    model = AtmosphericTurbulenceClosure()

    state = TurbulenceState(
        wind_shear=10, temperature_gradient=5, humidity_gradient=2, mixing_length=20, turbulent_energy=5
    )

    assert model.turbulence_intensity(state) == 0.45


def test_closure_parameter():

    model = AtmosphericTurbulenceClosure()

    state = TurbulenceState(
        wind_shear=10, temperature_gradient=5, humidity_gradient=2, mixing_length=20, turbulent_energy=5
    )

    assert model.closure_parameter(state) == 0.8
