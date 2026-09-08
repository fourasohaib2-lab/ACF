from acf.model4d.physics.surface_flux import SurfaceFlux


def test_sensible_heat_flux():
    value = SurfaceFlux.sensible_heat_flux(300, 290)

    assert value > 0


def test_sensible_heat_flux_zero():
    value = SurfaceFlux.sensible_heat_flux(290, 290)

    assert value == 0


def test_latent_heat_flux():
    value = SurfaceFlux.latent_heat_flux(0.001)

    assert round(value, 1) == 2500.0


def test_momentum_flux():
    value = SurfaceFlux.momentum_flux(10)

    assert value > 0


def test_bulk_exchange():
    value = SurfaceFlux.bulk_exchange(10, 0.5)

    assert value == 5


def test_constants():
    assert SurfaceFlux.AIR_DENSITY > 0
    assert SurfaceFlux.CP_AIR > 0


def test_negative_temperature_difference():
    value = SurfaceFlux.sensible_heat_flux(280, 290)

    assert value < 0


def test_high_wind():
    value = SurfaceFlux.momentum_flux(50)

    assert value > 0


def test_zero_evaporation():
    value = SurfaceFlux.latent_heat_flux(0)

    assert value == 0


def test_bulk_zero():
    value = SurfaceFlux.bulk_exchange(0, 10)

    assert value == 0
