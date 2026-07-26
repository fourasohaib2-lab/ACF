from acf.model4d.physics.ocean_coupling import OceanCoupling


def test_sensible_heat_flux():
    value = OceanCoupling.sensible_heat_flux(
        5,
        290,
        300
    )

    assert value > 0


def test_sensible_heat_flux_negative():
    value = OceanCoupling.sensible_heat_flux(
        5,
        300,
        290
    )

    assert value < 0


def test_latent_heat_flux():
    value = OceanCoupling.latent_heat_flux(
        10,
        0.01
    )

    assert value > 0


def test_ocean_temperature_change():
    value = OceanCoupling.ocean_temperature_change(
        100,
        3600
    )

    assert value > 0


def test_coupling_strength():
    value = OceanCoupling.coupling_strength(
        300,
        290
    )

    assert value == 10


def test_zero_difference():
    value = OceanCoupling.coupling_strength(
        290,
        290
    )

    assert value == 0


def test_long_duration():
    value = OceanCoupling.ocean_temperature_change(
        200,
        7200
    )

    assert value > 0


def test_strong_wind_flux():
    value = OceanCoupling.sensible_heat_flux(
        20,
        285,
        300
    )

    assert value > 0


def test_evaporation():
    value = OceanCoupling.latent_heat_flux(
        15,
        0.02
    )

    assert value > 0


def test_module_exists():
    assert OceanCoupling is not None
