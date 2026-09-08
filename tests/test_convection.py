from acf.model4d.physics.convection import ConvectionPhysics


def test_cape():
    """
    CORRECTED: cape() used to divide the (already dimensionally
    correct, in J/kg) formula result by an unexplained 100, reporting
    3.38 J/kg for a case that is actually a real, moderate-instability
    338.28 J/kg. The formula's own units (m/s^2 * dimensionless * m)
    already work out to J/kg with no conversion needed.
    """

    value = ConvectionPhysics.cape(300, 290, 1000)

    assert round(value, 2) == 338.28


def test_cin():
    """CORRECTED: same unexplained "/ 100" bug as cape() - see its NOTE."""

    value = ConvectionPhysics.cin(290, 300, 1000)

    assert round(value, 2) == -327.0


def test_convective_velocity():

    value = ConvectionPhysics.convective_velocity(500)

    assert round(value, 2) == 31.62


def test_zero_cape():

    value = ConvectionPhysics.convective_velocity(0)

    assert value == 0


def test_convection_index():

    value = ConvectionPhysics.convection_index(1000, -100)

    assert value == 1100


def test_thunderstorm_probability():

    value = ConvectionPhysics.thunderstorm_probability(1250)

    assert value == 0.5


def test_probability_limit():

    value = ConvectionPhysics.thunderstorm_probability(5000)

    assert value == 1.0


def test_negative_cape():

    value = ConvectionPhysics.cape(280, 290, 1000)

    assert value == 0


def test_negative_height():

    value = ConvectionPhysics.cape(300, 290, -10)

    assert value == 0


def test_cin_positive_case():

    value = ConvectionPhysics.cin(300, 290, 1000)

    assert value == 0


def test_cape_chains_consistently_into_sibling_functions():
    """
    The bug this class had (cape()'s output 100x too small) was only
    visible by chaining cape() into its own sibling functions, which
    both assume a real-unit CAPE input - convective_velocity(cape) =
    sqrt(2*CAPE) and thunderstorm_probability(cape) = CAPE/2500. A
    genuinely severe-instability CAPE (~2500 J/kg, the standard
    "extreme instability" threshold) must now yield a near-certain
    thunderstorm probability and a physically real updraft speed
    (tens of m/s), not the near-zero probability the old /100 bug
    would have produced.
    """
    severe_cape = ConvectionPhysics.cape(320, 290, 2500)  # a genuinely strongly unstable case
    assert severe_cape > 2000.0

    updraft = ConvectionPhysics.convective_velocity(severe_cape)
    assert 30.0 < updraft < 100.0  # realistic severe-storm updraft speed range

    probability = ConvectionPhysics.thunderstorm_probability(severe_cape)
    assert probability > 0.8
