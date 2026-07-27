from acf.model4d.physics.atmospheric_convection import (
    AtmosphericConvectionPhysics
)


def test_cape():

    value = AtmosphericConvectionPhysics.cape(
        303,
        300,
        1000
    )

    assert round(value, 2) == 98.10



def test_cin():

    value = AtmosphericConvectionPhysics.cin(
        298,
        300,
        1000
    )

    assert round(value, 2) == 65.40



def test_buoyancy():

    value = AtmosphericConvectionPhysics.buoyancy(
        303,
        300
    )

    assert round(value, 3) == 0.098



def test_convection_velocity():

    value = AtmosphericConvectionPhysics.convection_velocity(
        100
    )

    assert round(value, 2) == 14.14



def test_parcel_acceleration():

    value = AtmosphericConvectionPhysics.parcel_acceleration(
        0.5
    )

    assert value == 0.5



def test_convective_timescale():

    value = AtmosphericConvectionPhysics.convective_timescale(
        1000,
        10
    )

    assert value == 100



def test_lcl_height():

    value = AtmosphericConvectionPhysics.lifting_condensation_level_height(
        300,
        290
    )

    assert value == 1250



def test_convective_flux():

    value = AtmosphericConvectionPhysics.convective_flux(
        1.2,
        5,
        2
    )

    assert round(value, 2) == 12048



def test_updraft_velocity():

    value = AtmosphericConvectionPhysics.updraft_velocity(
        50
    )

    assert round(value, 2) == 10



def test_negative_cape():

    value = AtmosphericConvectionPhysics.convection_velocity(
        -10
    )

    assert value == 0
