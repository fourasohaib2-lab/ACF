"""
Tests for acf.science.cyclones.
"""

import pytest

from acf.science.cyclones import Bombogenesis, BruntVaisalaFrequency, GradientWind, RossbyRadius, SaffirSimpson


def test_gradient_wind_cyclonic_positive():
    v = GradientWind.calculate(radius_m=200000, coriolis_f=1e-4, density=1.2, radial_pressure_gradient_pa_m=0.01)
    assert v > 0


def test_gradient_wind_cyclonic_less_than_geostrophic():
    # Gradient wind (cyclonic) is sub-geostrophic: it must be less
    # than the equivalent geostrophic wind Vg = (1/(rho*f)) * dp/dr.
    v_gradient = GradientWind.calculate(
        radius_m=200000, coriolis_f=1e-4, density=1.2, radial_pressure_gradient_pa_m=0.01
    )
    v_geostrophic = (1.0 / (1.2 * 1e-4)) * 0.01
    assert v_gradient < v_geostrophic


def test_gradient_wind_invalid_radius():
    with pytest.raises(ValueError):
        GradientWind.calculate(radius_m=0, coriolis_f=1e-4, density=1.2, radial_pressure_gradient_pa_m=0.01)


def test_gradient_wind_invalid_discriminant():
    with pytest.raises(ValueError):
        GradientWind.calculate(
            radius_m=200000, coriolis_f=1e-4, density=1.2, radial_pressure_gradient_pa_m=-100.0, cyclonic=False
        )


def test_brunt_vaisala_stable_atmosphere_positive():
    n = BruntVaisalaFrequency.calculate(potential_temperature_k=300.0, dtheta_dz=0.01)
    assert n > 0


def test_brunt_vaisala_neutral_or_unstable_returns_zero():
    assert BruntVaisalaFrequency.calculate(potential_temperature_k=300.0, dtheta_dz=0.0) == 0.0
    assert BruntVaisalaFrequency.calculate(potential_temperature_k=300.0, dtheta_dz=-0.01) == 0.0


def test_rossby_radius_baroclinic_positive():
    n = BruntVaisalaFrequency.calculate(potential_temperature_k=300.0, dtheta_dz=0.01)
    lr = RossbyRadius.baroclinic(brunt_vaisala_n=n, scale_height_m=10000.0, coriolis_f=1e-4)
    assert lr > 0
    # Typical midlatitude baroclinic Rossby radius is on the order of
    # several hundred km to ~1000 km.
    assert 1e5 < lr < 2e6


def test_bombogenesis_threshold_at_reference_latitude_is_24():
    assert Bombogenesis.threshold_hpa_24h(60.0) == pytest.approx(24.0)


def test_bombogenesis_threshold_at_pole_matches_published_example():
    # Sanders & Gyakum (1980): ~28 hPa/24h at the poles.
    assert Bombogenesis.threshold_hpa_24h(90.0) == pytest.approx(27.7, abs=0.2)


def test_bombogenesis_threshold_at_25deg_matches_published_example():
    # Sanders & Gyakum (1980): ~12 hPa/24h at 25 deg latitude.
    assert Bombogenesis.threshold_hpa_24h(25.0) == pytest.approx(11.7, abs=0.2)


def test_bombogenesis_threshold_undefined_at_equator():
    with pytest.raises(ValueError):
        Bombogenesis.threshold_hpa_24h(0.0)


def test_bombogenesis_is_bomb_true_case():
    # 30 hPa drop at 60N exceeds the 24 hPa threshold -> qualifies as a bomb.
    assert Bombogenesis.is_bomb(pressure_drop_24h_hpa=30.0, latitude_deg=60.0) is True


def test_bombogenesis_is_bomb_false_case():
    assert Bombogenesis.is_bomb(pressure_drop_24h_hpa=10.0, latitude_deg=60.0) is False


def test_bergeron_units_exactly_one_at_threshold():
    assert Bombogenesis.bergeron_units(pressure_drop_24h_hpa=24.0, latitude_deg=60.0) == pytest.approx(1.0)


@pytest.mark.parametrize(
    "wind_kt,expected",
    [
        (20.0, "Tropical Depression"),
        (50.0, "Tropical Storm"),
        (70.0, "Category 1"),
        (90.0, "Category 2"),
        (100.0, "Category 3"),
        (120.0, "Category 4"),
        (150.0, "Category 5"),
    ],
)
def test_saffir_simpson_categories(wind_kt, expected):
    assert SaffirSimpson.category(wind_kt) == expected


def test_saffir_simpson_major_hurricane_threshold():
    assert SaffirSimpson.is_major_hurricane(95.0) is False
    assert SaffirSimpson.is_major_hurricane(96.0) is True


def test_saffir_simpson_invalid_negative_wind():
    with pytest.raises(ValueError):
        SaffirSimpson.category(-10.0)
