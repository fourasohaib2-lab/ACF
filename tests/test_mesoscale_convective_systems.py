from acf.model4d.physics.mesoscale_convective_systems import (
    MesoscaleConvectiveSystemsPhysics
)


def test_cluster_size():
    value = MesoscaleConvectiveSystemsPhysics.convective_cluster_size(
        100,
        5
    )
    assert value == 500


def test_life_cycle():
    value = MesoscaleConvectiveSystemsPhysics.life_cycle_stage(
        5
    )
    assert value == "mature"


def test_probability():
    value = MesoscaleConvectiveSystemsPhysics.formation_probability(
        1000,
        0.5
    )
    assert value == 5


def test_updraft():
    value = MesoscaleConvectiveSystemsPhysics.updraft_strength(
        1000
    )
    assert value == 100


def test_downdraft():
    value = MesoscaleConvectiveSystemsPhysics.downdraft_strength(
        20,
        2
    )
    assert value == 40


def test_outflow():
    value = MesoscaleConvectiveSystemsPhysics.outflow_boundary_speed(
        10
    )
    assert value == 20


def test_organization():
    value = MesoscaleConvectiveSystemsPhysics.convective_organization_index(
        20,
        10
    )
    assert value == 2


def test_precipitation():
    value = MesoscaleConvectiveSystemsPhysics.precipitation_core_intensity(
        10,
        5
    )
    assert value == 50


def test_velocity():
    value = MesoscaleConvectiveSystemsPhysics.system_velocity(
        200,
        10
    )
    assert value == 20


def test_energy():
    value = MesoscaleConvectiveSystemsPhysics.mcs_energy(
        200,
        300
    )
    assert value == 60000
