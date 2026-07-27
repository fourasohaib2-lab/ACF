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



def test_horizontal_wind_speed():

    model = AtmosphericFluidDynamics()

    assert model.horizontal_wind_speed(create_state()) == 11.18



def test_wind_direction():

    model = AtmosphericFluidDynamics()

    assert model.wind_direction(create_state()) == 26.6



def test_horizontal_advection():

    model = AtmosphericFluidDynamics()

    assert model.horizontal_advection(create_state()) == 3.0



def test_vertical_motion():

    model = AtmosphericFluidDynamics()

    assert model.vertical_motion(create_state()) == 2



def test_vorticity_dynamics():

    model = AtmosphericFluidDynamics()

    assert model.vorticity_dynamics(create_state()) == 0.4



def test_divergence_analysis():

    model = AtmosphericFluidDynamics()

    assert model.divergence_analysis(create_state()) == 0.1



def test_coriolis_effect():

    model = AtmosphericFluidDynamics()

    assert model.coriolis_effect(create_state()) == 0.0



def test_pressure_gradient_force():

    model = AtmosphericFluidDynamics()

    assert model.pressure_gradient_force(create_state()) == 0.83



def test_momentum_transfer():

    model = AtmosphericFluidDynamics()

    assert model.momentum_transfer(create_state()) == 13.42



def test_potential_vorticity():

    model = AtmosphericFluidDynamics()

    assert model.potential_vorticity(create_state()) == 0.42
