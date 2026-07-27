from acf.model4d.physics.atmospheric_fluid_dynamics import (
    AtmosphericFluidDynamics,
    FluidDynamicsState,
)


def create_state():

    return FluidDynamicsState(
        temperature=300,
        pressure=1000,
        density=1.2,
        wind_u=10,
        wind_v=5,
        vertical_velocity=2,
        vorticity=0.4,
        divergence=0.1,
        altitude=1000,
        coriolis_parameter=0.0001,
    )


def test_wind_speed():

    model = AtmosphericFluidDynamics()

    assert model.wind_speed(create_state()) == 11.18


def test_kinetic_energy():

    model = AtmosphericFluidDynamics()

    assert model.kinetic_energy(create_state()) == 75.0


def test_relative_vorticity():

    model = AtmosphericFluidDynamics()

    assert model.relative_vorticity(create_state()) == 0.4


def test_divergence():

    model = AtmosphericFluidDynamics()

    assert model.divergence(create_state()) == 0.1


def test_vertical_motion():

    model = AtmosphericFluidDynamics()

    assert model.vertical_motion(create_state()) == 2


def test_coriolis_effect():

    model = AtmosphericFluidDynamics()

    assert model.coriolis_effect(create_state()) == 0.0


def test_pressure_gradient_force():

    model = AtmosphericFluidDynamics()

    assert model.pressure_gradient_force(create_state()) == 833.33


def test_flow_balance():

    model = AtmosphericFluidDynamics()

    assert model.flow_balance(create_state()) == 0.3


def test_atmospheric_transport():

    model = AtmosphericFluidDynamics()

    assert model.atmospheric_transport(create_state()) == 22.36


def test_potential_vorticity():

    model = AtmosphericFluidDynamics()

    assert model.potential_vorticity(create_state()) == 0.42
