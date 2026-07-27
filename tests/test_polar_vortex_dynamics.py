from acf.model4d.physics.polar_vortex_dynamics import (
    PolarVortexDynamicsPhysics
)


def test_vortex_speed():
    assert PolarVortexDynamicsPhysics.vortex_speed(
        10,
        5
    ) == 50


def test_vortex_intensity():
    assert PolarVortexDynamicsPhysics.vortex_intensity(
        20
    ) == 400


def test_thermal_gradient():
    assert PolarVortexDynamicsPhysics.thermal_gradient(
        -50,
        -20
    ) == 30


def test_stratospheric_stability():
    assert PolarVortexDynamicsPhysics.stratospheric_stability(
        30
    ) == 3


def test_vortex_displacement():
    assert PolarVortexDynamicsPhysics.vortex_displacement(
        100,
        40
    ) == 60


def test_kinetic_energy():
    assert PolarVortexDynamicsPhysics.kinetic_energy(
        10,
        20
    ) == 2000


def test_angular_momentum():
    assert PolarVortexDynamicsPhysics.angular_momentum(
        10,
        5,
        4
    ) == 200


def test_polar_warming_effect():
    assert PolarVortexDynamicsPhysics.polar_warming_effect(
        15
    ) == 30


def test_vortex_decay():
    assert PolarVortexDynamicsPhysics.vortex_decay(
        100,
        0.2
    ) == 80


def test_vortex_energy():
    assert PolarVortexDynamicsPhysics.vortex_energy(
        20,
        10
    ) == 1000
