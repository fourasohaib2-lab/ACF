from acf.model4d.physics.boundary_layer_physics import BoundaryLayerPhysics


def test_boundary_layer_height():
    value = BoundaryLayerPhysics.boundary_layer_height(
        5,
        200
    )
    assert value == 1000


def test_friction_velocity():
    value = BoundaryLayerPhysics.friction_velocity(
        10,
        0.25
    )
    assert value == 2.5


def test_turbulent_kinetic_energy():
    value = BoundaryLayerPhysics.turbulent_kinetic_energy(
        4,
        6
    )
    assert value == 26


def test_mixing_height():
    value = BoundaryLayerPhysics.mixing_height(
        300,
        3
    )
    assert value == 100


def test_surface_flux():
    value = BoundaryLayerPhysics.surface_flux(
        500,
        10
    )
    assert value == 50


def test_stability_parameter():
    value = BoundaryLayerPhysics.stability_parameter(
        20,
        5
    )
    assert value == 4


def test_richardson_number():
    value = BoundaryLayerPhysics.richardson_number(
        100,
        25
    )
    assert value == 4


def test_eddy_diffusivity():
    value = BoundaryLayerPhysics.eddy_diffusivity(
        20,
        5
    )
    assert value == 100


def test_turbulence_intensity():
    value = BoundaryLayerPhysics.turbulence_intensity(
        50,
        100
    )
    assert value == 0.5


def test_pbl_regime():
    value = BoundaryLayerPhysics.pbl_regime(
        300
    )
    assert value == "medium"
