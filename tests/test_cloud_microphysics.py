from acf.model4d.physics.cloud_microphysics import CloudMicrophysics


def test_relative_humidity():
    value = CloudMicrophysics.relative_humidity(
        0.010,
        0.020
    )

    assert value == 50.0


def test_saturation_deficit():
    value = CloudMicrophysics.saturation_deficit(
        0.020,
        0.010
    )

    assert value == 0.010


def test_condensation_positive():
    value = CloudMicrophysics.condensation_rate(
        0.020,
        0.010
    )

    assert value == 0.010


def test_no_condensation():
    value = CloudMicrophysics.condensation_rate(
        0.005,
        0.010
    )

    assert value == 0.0


def test_cloud_water_update():
    value = CloudMicrophysics.cloud_water_update(
        0.001,
        0.002,
        0.0005
    )

    assert value == 0.0025


def test_autoconversion():
    value = CloudMicrophysics.autoconversion(
        0.003,
        threshold=0.001,
        rate=1
    )

    assert value == 0.002


def test_autoconversion_below_threshold():
    value = CloudMicrophysics.autoconversion(
        0.0005
    )

    assert value == 0.0


def test_zero_humidity():
    value = CloudMicrophysics.relative_humidity(
        0,
        0.02
    )

    assert value == 0


def test_saturation_equal():
    value = CloudMicrophysics.condensation_rate(
        0.01,
        0.01
    )

    assert value == 0


def test_module_exists():
    assert CloudMicrophysics is not None
