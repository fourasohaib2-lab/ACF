from acf.model4d.physics.atmospheric_stability import AtmosphericStabilityPhysics


def test_brunt_vaisala_frequency():

    value = AtmosphericStabilityPhysics.brunt_vaisala_frequency(
        0.01,
        300
    )

    assert round(value, 3) == 0.018


def test_richardson_number():

    value = AtmosphericStabilityPhysics.richardson_number(
        0.25,
        0.5
    )

    assert value == 1.0


def test_stability_parameter():

    value = AtmosphericStabilityPhysics.stability_parameter(
        6,
        9.8
    )

    assert value == 3.8


def test_stable_classification():

    value = AtmosphericStabilityPhysics.classify_stability(
        3
    )

    assert value == "stable"


def test_unstable_classification():

    value = AtmosphericStabilityPhysics.classify_stability(
        -2
    )

    assert value == "unstable"


def test_neutral_classification():

    value = AtmosphericStabilityPhysics.classify_stability(
        0
    )

    assert value == "neutral"


def test_cape():

    value = AtmosphericStabilityPhysics.convective_available_energy(
        10,
        1000
    )

    assert value == 327.0


def test_cin():

    value = AtmosphericStabilityPhysics.convective_inhibition(
        -5,
        1000
    )

    assert value == 50


def test_positive_cin():

    value = AtmosphericStabilityPhysics.convective_inhibition(
        5,
        1000
    )

    assert value == 0


def test_stability_index():

    value = AtmosphericStabilityPhysics.stability_index(
        -4
    )

    assert value == -4
