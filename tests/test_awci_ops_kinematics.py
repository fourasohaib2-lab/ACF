import numpy as np
import pytest

from acf.awci.ops.kinematics import (
    cat_category_codes,
    ellrod_ti2,
    grid_spacing_m,
    horizontal_gradients,
    layer_shear,
    wind_speed,
)
from acf.science.wind_turbulence import CATIndex

LATS = np.linspace(30.0, 32.0, 9)
LONS = np.linspace(0.0, 2.0, 9)


def test_wind_speed() -> None:
    np.testing.assert_allclose(wind_speed(np.array([3.0]), np.array([4.0])), [5.0])


def test_layer_shear_uses_real_gh_and_upper_neighbour() -> None:
    u = np.stack([np.full((2, 2), 10.0), np.full((2, 2), 20.0), np.full((2, 2), 20.0)])
    v = np.zeros_like(u)
    gh = np.stack([np.full((2, 2), 100.0), np.full((2, 2), 1100.0), np.full((2, 2), 3100.0)])
    shear, vws = layer_shear(u, v, gh)
    assert shear[0, 0, 0] == pytest.approx(10.0)
    assert vws[0, 0, 0] == pytest.approx(10.0 / 1000.0)
    # top level uses the lower neighbour: |20-20| / 2000
    assert vws[2, 0, 0] == pytest.approx(0.0)
    assert shear[1, 0, 0] == pytest.approx(0.0)


def test_layer_shear_degenerate_dz_is_nan() -> None:
    u = np.stack([np.ones((1, 1)), 2 * np.ones((1, 1))])
    gh = np.stack([np.full((1, 1), 500.0), np.full((1, 1), 500.2)])
    _, vws = layer_shear(u, np.zeros_like(u), gh)
    assert np.isnan(vws[0, 0, 0])


def test_horizontal_gradient_of_linear_field() -> None:
    dy, dx = grid_spacing_m(LATS, LONS)
    lat_m = (LATS - LATS[0])[:, None] * (dy / (LATS[1] - LATS[0])) * np.ones((1, LONS.size))
    df_dx, df_dy = horizontal_gradients(2.0e-5 * lat_m, LATS, LONS)
    np.testing.assert_allclose(df_dy, 2.0e-5, rtol=1e-9)
    np.testing.assert_allclose(df_dx, 0.0, atol=1e-15)


def test_ti2_matches_scalar_cat_index() -> None:
    rng = np.random.default_rng(1)
    u = rng.normal(20.0, 8.0, (3, 9, 9))
    v = rng.normal(0.0, 8.0, (3, 9, 9))
    gh = np.stack([np.full((9, 9), h) for h in (1500.0, 3000.0, 5600.0)])
    div = rng.normal(0.0, 1e-5, (3, 9, 9))
    ti2 = ellrod_ti2(u, v, gh, div, LATS, LONS)
    du_dx, du_dy = horizontal_gradients(u, LATS, LONS)
    dv_dx, dv_dy = horizontal_gradients(v, LATS, LONS)
    _, vws = layer_shear(u, v, gh)
    k, i, j = 1, 4, 4
    expected = CATIndex.ti2(
        vws[k, i, j],
        CATIndex.deformation(du_dx[k, i, j], dv_dy[k, i, j], dv_dx[k, i, j], du_dy[k, i, j]),
        -div[k, i, j],
    )
    assert ti2[k, i, j] == pytest.approx(expected, rel=1e-12)


def test_cat_categories_match_scalar_thresholds() -> None:
    values = np.array([1e-7, 5e-7, 9e-7, 13e-7, np.nan])
    np.testing.assert_array_equal(cat_category_codes(values), [0, 1, 2, 3, -1])
    names = ["Smooth to Light", "Light-Moderate", "Moderate", "Moderate-Severe"]
    for code, value in zip(cat_category_codes(values[:4]), values[:4]):
        assert names[code] == CATIndex.category(float(value))
