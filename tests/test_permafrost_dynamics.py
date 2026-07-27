from acf.model4d.physics.permafrost_dynamics import (
    PermafrostDynamicsPhysics
)


def test_active_layer_depth():
    assert PermafrostDynamicsPhysics.active_layer_depth(
        5, 2
    ) == 10


def test_permafrost_temperature():
    assert PermafrostDynamicsPhysics.permafrost_temperature(
        5, 3
    ) == 2


def test_thaw_rate():
    assert PermafrostDynamicsPhysics.thaw_rate(
        4, 5
    ) == 20


def test_ground_ice_loss():
    assert PermafrostDynamicsPhysics.ground_ice_loss(
        100, 40
    ) == 60


def test_thermal_flux():
    assert PermafrostDynamicsPhysics.thermal_flux(
        10, 5
    ) == 50


def test_carbon_release():
    assert PermafrostDynamicsPhysics.carbon_release(
        20, 3
    ) == 60


def test_permafrost_stability():
    assert PermafrostDynamicsPhysics.permafrost_stability(
        -2
    ) == "stable"


def test_freeze_depth():
    assert PermafrostDynamicsPhysics.freeze_depth(
        -10, 2
    ) == 20


def test_soil_settlement():
    assert PermafrostDynamicsPhysics.soil_settlement(
        10, 0.5
    ) == 5


def test_methane_emission():
    assert PermafrostDynamicsPhysics.methane_emission(
        50, 2
    ) == 100
