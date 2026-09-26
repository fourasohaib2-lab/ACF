import numpy as np
import pytest

from acf.awci.ops.cloud_profile import load_cloud_profile
from acf.awci.ops.clouds import (
    ETAGE_HIGH, ETAGE_LOW, ETAGE_MID, amount_code, etage_codes, level_interfaces, max_random_cover, oktas,
    sundqvist_fraction, vertical_gradient_per_km,
)

P = load_cloud_profile()


def test_sundqvist_bounds_and_monotonic() -> None:
    rh = np.array([50.0, 80.0, 90.0, 99.0, 100.0, 104.0, np.nan])
    c = sundqvist_fraction(rh, 0.8)
    assert c[0] == 0.0 and c[1] == 0.0 and c[4] == 1.0 and c[5] == 1.0 and np.isnan(c[6])
    assert np.isclose(c[2], 1 - np.sqrt(0.1 / 0.2))
    assert np.all(np.diff(c[:5]) >= 0)


def test_etages_follow_ecmwf_sigma_bounds() -> None:
    levels = np.array([1000.0, 850.0, 700.0, 500.0, 400.0])
    codes = etage_codes(levels, np.array([[1000.0]]), P)[:, 0, 0]
    assert codes.tolist() == [ETAGE_LOW, ETAGE_LOW, ETAGE_MID, ETAGE_MID, ETAGE_HIGH]  # 0.85 low, 0.8 mid, 0.45 high
    over_plateau = etage_codes(levels, np.array([[850.0]]), P)[:, 0, 0]  # sigma follows the terrain
    assert over_plateau[2] == ETAGE_LOW  # 700/850 = 0.82


@pytest.mark.parametrize("column,expected", [
    ([0.0, 0.5, 0.0], 0.5),                 # single layer
    ([0.3, 0.6, 0.0], 0.6),                 # adjacent: maximum overlap
    ([0.5, 0.0, 0.5], 0.75),                # separated: random overlap 1 - 0.5 * 0.5
    ([1.0, 0.0, 0.2], 1.0),
    ([np.nan, 0.4, 0.0], 0.4),              # below-ground NaN counts as clear
])
def test_max_random_overlap(column: list[float], expected: float) -> None:
    f = np.array(column)[:, None, None]
    assert np.isclose(max_random_cover(f)[0, 0], expected)


def test_overlap_restricted_to_an_etage_mask() -> None:
    f = np.array([0.5, 0.0, 0.5])[:, None, None]
    mask = np.array([True, True, False])[:, None, None]
    assert np.isclose(max_random_cover(f, mask)[0, 0], 0.5)


def test_oktas_follow_wmo_code_2700() -> None:
    out = oktas(np.array([0.0, 0.05, 0.3, 0.9, 0.999, 1.0, np.nan]))
    assert out[:6].tolist() == [0, 1, 2, 7, 7, 8] and np.isnan(out[6])
    assert [amount_code(n) for n in (1, 2, 3, 4, 5, 7, 8)] == ["FEW", "FEW", "SCT", "SCT", "BKN", "BKN", "OVC"]


def test_interfaces_midpoints_and_terrain_floor() -> None:
    gh = np.array([100.0, 800.0, 1500.0])[:, None, None]
    lower, upper = level_interfaces(gh, np.array([[300.0]]))
    assert lower[:, 0, 0].tolist() == [300.0, 450.0, 1150.0]
    assert upper[:, 0, 0].tolist() == [450.0, 1150.0, 1850.0]


def test_vertical_gradient_forward_then_backward_at_top() -> None:
    f = np.array([300.0, 305.0, 306.0])[:, None, None]
    gh = np.array([0.0, 1000.0, 2000.0])[:, None, None]
    assert vertical_gradient_per_km(f, gh)[:, 0, 0].tolist() == [5.0, 1.0, 1.0]
