from acf.model4d.physics.atmospheric_boundary_layer_dynamics import (
    AtmosphericBoundaryLayerDynamics,
    BoundaryLayerState,
)


def test_name():

    model = AtmosphericBoundaryLayerDynamics()

    assert model.name == (
        "Atmospheric Boundary Layer Dynamics"
    )


def test_turbulence():

    model = AtmosphericBoundaryLayerDynamics()

    state = BoundaryLayerState(
        wind_speed=10,
        temperature_difference=5,
        humidity_difference=2,
        surface_roughness=0.5,
        stability=1
    )

    assert model.turbulence_intensity(state) == 0.5


def test_sensible_heat_flux():

    model = AtmosphericBoundaryLayerDynamics()

    state = BoundaryLayerState(
        wind_speed=20,
        temperature_difference=10,
        humidity_difference=5,
        surface_roughness=0.4
    )

    assert model.sensible_heat_flux(state) == 20.0


def test_latent_heat_flux():

    model = AtmosphericBoundaryLayerDynamics()

    state = BoundaryLayerState(
        wind_speed=10,
        temperature_difference=5,
        humidity_difference=4,
        surface_roughness=0.3
    )

    assert model.latent_heat_flux(state) == 3.2


def test_vertical_mixing():

    model = AtmosphericBoundaryLayerDynamics()

    state = BoundaryLayerState(
        wind_speed=10,
        temperature_difference=5,
        humidity_difference=2,
        surface_roughness=0.5,
        stability=2
    )

    assert model.vertical_mixing(state) == 1.0


def test_surface_exchange():

    model = AtmosphericBoundaryLayerDynamics()

    state = BoundaryLayerState(
        wind_speed=10,
        temperature_difference=5,
        humidity_difference=4,
        surface_roughness=0.3
    )

    assert model.surface_exchange(state) == 7.2
