"""Area-weighted domain indicators for the KPI row."""

import numpy as np

from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.summary import area_pct, area_weights, badge, summarize, weighted_percentile

PROFILE = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)


def test_area_weights_follow_cos_latitude() -> None:
    w = area_weights(np.array([0.0, 60.0]), 3)
    assert w.shape == (2, 3) and np.allclose(w[1] / w[0], 0.5)


def test_area_pct_is_weighted_and_ignores_nan() -> None:
    w = area_weights(np.array([0.0, 60.0]), 1)
    cond = np.array([[False], [True]])
    assert np.isclose(area_pct(cond, np.ones((2, 1), bool), w), 100 * 0.5 / 1.5)
    assert area_pct(cond, np.zeros((2, 1), bool), w) is None


def test_weighted_percentile_inverted_cdf() -> None:
    v = np.array([1.0, 2.0, 3.0, 4.0, np.nan])
    w = np.ones(5)
    assert weighted_percentile(v, w, 50) == 2.0 and weighted_percentile(v, w, 95) == 4.0
    assert weighted_percentile(np.array([np.nan]), np.ones(1), 95) is None


def test_badges() -> None:
    assert badge(None, (5, 15, 30)) is None
    assert [badge(x, (5, 15, 30)) for x in (1, 5, 20, 31)] == ["ok", "attention", "serious", "critical"]
    assert [badge(x, (5e-3, 8e-3)) for x in (1e-3, 6e-3, 9e-3)] == ["ok", "attention", "serious"]


def test_summarize_on_synthetic_fields() -> None:
    lats = np.array([30.0, 30.25])
    ones = np.ones((2, 2))
    layers = {
        "awci": np.array([[10.0, 70.0], [np.nan, 40.0]]), "cat_category": np.array([[0.0, 2.0], [np.nan, 3.0]]),
        "icing_potential": np.array([[0.0, 1.0], [np.nan, 0.0]]), "vertical_shear": ones * 4e-3,
        "mucape": np.array([[0.0, 1500.0], [200.0, 1000.0]]), "precip_class": np.array([[0.0, 3.0], [1.0, 0.0]]),
        "ceiling_m": np.array([[np.nan, 200.0], [500.0, np.nan]]), "convective_class": np.array([[0, 4], [0, 2.0]]),
        "cloud_cover_bias": np.array([[0.1, -0.1], [0.2, 0.0]]),
    }
    s = summarize(layers, lats, PROFILE)
    assert s["valid_cells_pct"] is not None and 74 < s["valid_cells_pct"] < 76
    assert 66 < s["turbulence_area_pct"] < 67 and s["mucape_max"] == 1500.0
    assert 49 < s["convection_area_pct"] < 51 and 24 < s["cb_area_pct"] < 26
    assert s["awci_class"] == "Very High" and s["badges"]["turbulence_area_pct"] == "critical"


def test_summarize_without_sp1c_layers() -> None:
    lats = np.array([30.0, 30.25])
    base = {k: np.zeros((2, 2)) for k in ("awci", "cat_category", "icing_potential", "vertical_shear", "mucape",
                                          "precip_class")}
    s = summarize(base | {"ceiling_m": None, "convective_class": None, "cloud_cover_bias": None}, lats, PROFILE)
    assert s["low_ceiling_area_pct"] is None and s["cb_area_pct"] is None and s["cloud_cover_bias_mean"] is None
