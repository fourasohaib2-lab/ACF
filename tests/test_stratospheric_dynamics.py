from acf.model4d.physics.stratospheric_dynamics import (
    StratosphericDynamicsPhysics
)


def test_temperature_gradient():
    assert StratosphericDynamicsPhysics.temperature_gradient(
        220, 250
    ) == 30


def test_geopotential_height():
    assert StratosphericDynamicsPhysics.geopotential_height(
        100, 20
    ) == 120


def test_wind_shear():
    assert StratosphericDynamicsPhysics.wind_shear(
        80, 50
    ) == 30


def test_planetary_wave_effect():
    assert StratosphericDynamicsPhysics.planetary_wave_effect(
        10, 5
    ) == 50


def test_ozone_heating():
    assert StratosphericDynamicsPhysics.ozone_heating(
        4, 20
    ) == 80


def test_stratopause_temperature():
    assert StratosphericDynamicsPhysics.stratopause_temperature(
        260, 10
    ) == 270


def test_polar_vortex_strength():
    assert StratosphericDynamicsPhysics.polar_vortex_strength(
        50, 4
    ) == 200


def test_stratospheric_stability():
    assert StratosphericDynamicsPhysics.stratospheric_stability(
        -20
    ) == 20


def test_radiation_balance():
    assert StratosphericDynamicsPhysics.radiation_balance(
        500, 300
    ) == 200


def test_ozone_recovery_rate():
    assert StratosphericDynamicsPhysics.ozone_recovery_rate(
        300, 250
    ) == 50
