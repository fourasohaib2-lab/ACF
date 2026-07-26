from acf.model4d.physics.convection import ConvectionPhysics


def test_cape():

    value = ConvectionPhysics.cape(
        300,
        290,
        1000
    )

    assert round(value, 2) == 3.38



def test_cin():

    value = ConvectionPhysics.cin(
        290,
        300,
        1000
    )

    assert round(value, 2) == -3.27



def test_convective_velocity():

    value = ConvectionPhysics.convective_velocity(
        500
    )

    assert round(value, 2) == 31.62



def test_zero_cape():

    value = ConvectionPhysics.convective_velocity(
        0
    )

    assert value == 0



def test_convection_index():

    value = ConvectionPhysics.convection_index(
        1000,
        -100
    )

    assert value == 1100



def test_thunderstorm_probability():

    value = ConvectionPhysics.thunderstorm_probability(
        1250
    )

    assert value == 0.5



def test_probability_limit():

    value = ConvectionPhysics.thunderstorm_probability(
        5000
    )

    assert value == 1.0



def test_negative_cape():

    value = ConvectionPhysics.cape(
        280,
        290,
        1000
    )

    assert value == 0



def test_negative_height():

    value = ConvectionPhysics.cape(
        300,
        290,
        -10
    )

    assert value == 0



def test_cin_positive_case():

    value = ConvectionPhysics.cin(
        300,
        290,
        1000
    )

    assert value == 0
