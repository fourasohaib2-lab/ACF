from acf.model4d.physics.cloud_microphysics import CloudMicrophysicsPhysics


def test_saturation_ratio():

    value = CloudMicrophysicsPhysics.saturation_mixing_ratio(
        288.15,
        101325
    )

    assert round(value, 5) == 0.01076


def test_condensation():

    value = CloudMicrophysicsPhysics.condensation(
        0.015,
        0.010
    )

    assert round(value, 3) == 0.005


def test_evaporation():

    value = CloudMicrophysicsPhysics.evaporation(
        0.004,
        0.002
    )

    assert value == 0.002


def test_freezing():

    value = CloudMicrophysicsPhysics.freezing(
        0.01,
        263.15
    )

    assert round(value, 3) == 0.01


def test_melting():

    value = CloudMicrophysicsPhysics.melting(
        0.01,
        283.15
    )

    assert round(value, 3) == 0.01


def test_autoconversion():

    value = CloudMicrophysicsPhysics.autoconversion(
        0.003
    )

    assert round(value, 4) == 0.001


def test_precipitation():

    value = CloudMicrophysicsPhysics.precipitation_rate(
        0.002
    )

    assert value == 2


def test_cloud_fraction():

    value = CloudMicrophysicsPhysics.cloud_fraction(
        80
    )

    assert value == 0.8


def test_phase_ratio():

    value = CloudMicrophysicsPhysics.mixed_phase_ratio(
        0.004,
        0.006
    )

    assert round(value, 2) == 0.4


def test_zero_phase():

    value = CloudMicrophysicsPhysics.mixed_phase_ratio(
        0,
        0
    )

    assert value == 0
