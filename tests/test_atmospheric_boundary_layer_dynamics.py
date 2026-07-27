from acf.model4d.physics.atmospheric_boundary_layer_dynamics import (
    AtmosphericBoundaryLayerDynamics,
    BoundaryLayerState,
)


def test_boundary_layer_height():

    model = AtmosphericBoundaryLayerDynamics()

    state = BoundaryLayerState(
        surface_temperature_difference=2,
        wind_speed=5,
        surface_roughness=0.5,
        moisture_flux=4,
        mixing_coefficient=2,
    )

    assert model.boundary_layer_height(state) == 100



def test_turbulence_intensity():

    model = AtmosphericBoundaryLayerDynamics()

    state = BoundaryLayerState(
        surface_temperature_difference=2,
        wind_speed=10,
        surface_roughness=0.2,
        moisture_flux=4,
        mixing_coefficient=2,
    )

    assert model.turbulence_intensity(state) == 2



def test_heat_flux_exchange():

    model = AtmosphericBoundaryLayerDynamics()

    state = BoundaryLayerState(
        surface_temperature_difference=2,
        wind_speed=5,
        surface_roughness=0.5,
        moisture_flux=3,
        mixing_coefficient=2,
    )

    assert model.heat_flux_exchange(state) == 6



def test_turbulent_state():

    model = AtmosphericBoundaryLayerDynamics()

    state = BoundaryLayerState(
        surface_temperature_difference=3,
        wind_speed=10,
        surface_roughness=0.5,
        moisture_flux=5,
        mixing_coefficient=1,
    )

    assert (
        model.boundary_layer_state(state)
        == "turbulent_boundary_layer"
    )
