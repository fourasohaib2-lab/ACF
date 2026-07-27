from acf.model4d.physics.atmospheric_convection_dynamics import (
    AtmosphericConvectionDynamics,
    ConvectionState,
)


def test_buoyancy():
    model = AtmosphericConvectionDynamics()

    value = model.calculate_buoyancy(
        305,
        300
    )

    assert value > 0


def test_cape():
    model = AtmosphericConvectionDynamics()

    value = model.calculate_cape(
        0.01,
        1000
    )

    assert value > 0


def test_cin():
    model = AtmosphericConvectionDynamics()

    value = model.calculate_cin(
        -0.01,
        1000
    )

    assert value > 0


def test_velocity():
    model = AtmosphericConvectionDynamics()

    value = model.convective_velocity(
        100
    )

    assert value > 0


def test_heat_transport():
    model = AtmosphericConvectionDynamics()

    value = model.heat_transport(
        20,
        10
    )

    assert value == 200


def test_analysis():

    model = AtmosphericConvectionDynamics()

    state = ConvectionState(
        temperature_surface=305,
        temperature_parcel=305,
        environmental_temperature=300,
        vertical_velocity=5,
        heat_flux=100
    )

    result = model.analyze(
        state,
        1000
    )

    assert "cape" in result
    assert "cin" in result


def test_name():

    model = AtmosphericConvectionDynamics()

    assert model.name == "Atmospheric Convection Dynamics"


def test_version():

    model = AtmosphericConvectionDynamics()

    assert model.version == "1.0"


def test_negative_height():

    model = AtmosphericConvectionDynamics()

    try:
        model.calculate_cape(
            0.1,
            -10
        )
        assert False
    except ValueError:
        assert True


def test_negative_cape():

    model = AtmosphericConvectionDynamics()

    try:
        model.convective_velocity(
            -1
        )
        assert False
    except ValueError:
        assert True
