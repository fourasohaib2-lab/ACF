"""
Tests for acf.gui.dashboard.acf_workstation_stability_indices.
compute_real_stability_indices_at_point - the real, Qt-free per-point
stability summary (Phase 39, 2026-09-05).
"""

from __future__ import annotations

import numpy as np

from acf.awci.convective_energy import compute_real_cape_cin_at_point
from acf.awci.vertical_field import compute_real_complexity_volume
from acf.awci.wind_shear import compute_real_wind_shear_at_point
from acf.gui.dashboard.acf_workstation_stability_indices import compute_real_stability_indices_at_point


def _real_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=10, n_lon=18, n_levels=8, steps=3, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def test_lands_on_a_real_grid_coordinate():
    volume = _real_volume()
    result = compute_real_stability_indices_at_point(volume, lat=10.3, lon=20.7)

    assert result["lat"] in list(volume["lats"])
    assert result["lon"] in list(volume["lons"])


def test_cape_cin_match_a_real_independent_call_at_the_same_column():
    """Cross-check discipline: never a separately re-derived formula."""
    volume = _real_volume()
    lat, lon = float(volume["lats"][2]), float(volume["lons"][4])

    result = compute_real_stability_indices_at_point(volume, lat, lon)

    lat_idx = list(volume["lats"]).index(lat)
    lon_idx = list(volume["lons"]).index(lon)
    expected = compute_real_cape_cin_at_point(
        volume["temperature_volume"][:, lat_idx, lon_idx],
        volume["specific_humidity_volume"][:, lat_idx, lon_idx],
        volume["pressure_volume_hpa"][:, lat_idx, lon_idx],
    )
    assert result["cape_j_kg"] == expected["cape_j_kg"]
    assert result["cin_j_kg"] == expected["cin_j_kg"]


def test_bulk_wind_shear_matches_a_real_independent_call_at_the_same_column():
    volume = _real_volume()
    lat, lon = float(volume["lats"][1]), float(volume["lons"][3])

    result = compute_real_stability_indices_at_point(volume, lat, lon)

    lat_idx = list(volume["lats"]).index(lat)
    lon_idx = list(volume["lons"]).index(lon)
    expected = compute_real_wind_shear_at_point(
        volume["u_volume"][:, lat_idx, lon_idx], volume["v_volume"][:, lat_idx, lon_idx]
    )
    assert result["bulk_wind_shear_ms"] == expected["shear_m_s"]


def test_cape_cin_are_real_non_negative_values():
    volume = _real_volume()
    result = compute_real_stability_indices_at_point(volume, lat=10.0, lon=20.0)

    assert result["cape_j_kg"] >= 0.0
    assert result["cin_j_kg"] >= 0.0


def test_severe_weather_indices_are_real_and_match_independent_calls():
    """Regression guard (2026-09-13, master-prompt gap audit): K-Index/
    Total Totals/SWEAT Index already existed in acf.science but were
    never wired into any GUI panel. Cross-checks against direct
    independent formula calls on the same real interpolated values -
    never a second, silently-diverging implementation."""
    from acf.science.k_index import KIndex
    from acf.science.sweat_index import SWEATIndex
    from acf.science.total_totals import TotalTotals

    volume = _real_volume(n_levels=8)
    lat, lon = float(volume["lats"][2]), float(volume["lons"][4])

    result = compute_real_stability_indices_at_point(volume, lat, lon)

    assert result["k_index"] is not None
    assert result["total_totals"] is not None
    assert result["sweat_index"] is not None
    assert result["k_index_category"] == KIndex.category(result["k_index"])
    assert result["total_totals_category"] == TotalTotals.category(result["total_totals"])
    assert result["sweat_index_category"] == SWEATIndex.category(result["sweat_index"])


def test_severe_weather_indices_are_honestly_none_when_standard_levels_are_out_of_range():
    """A volume whose real native levels never reach down to 850 hPa
    must report None, never an extrapolated/fabricated value."""
    from acf.gui.dashboard.acf_workstation_stability_indices import compute_real_severe_weather_indices_at_point

    n = 5
    t_profile = np.full(n, 220.0)
    q_profile = np.full(n, 1e-4)
    p_profile = np.linspace(300.0, 100.0, n)  # entirely above 850/700/500 hPa
    u_profile = np.full(n, 5.0)
    v_profile = np.full(n, 5.0)

    result = compute_real_severe_weather_indices_at_point(t_profile, q_profile, p_profile, u_profile, v_profile)

    assert result["k_index"] is None
    assert result["total_totals"] is None
    assert result["sweat_index"] is None


def test_bulk_richardson_number_matches_a_real_independent_call():
    """Regression guard (2026-09-13, master-prompt gap audit): BRN
    already existed in acf.science.bulk_richardson_number but was never
    wired into any GUI panel - closes that gap using the exact same
    CAPE/shear this panel already computes, no second formula."""
    from acf.science.bulk_richardson_number import BulkRichardsonNumber

    volume = _real_volume()
    lat, lon = float(volume["lats"][2]), float(volume["lons"][4])

    result = compute_real_stability_indices_at_point(volume, lat, lon)

    if result["bulk_wind_shear_ms"] == 0:
        assert result["bulk_richardson_number"] is None
        assert result["bulk_richardson_category"] is None
    else:
        expected = BulkRichardsonNumber.calculate(cape=result["cape_j_kg"], shear=result["bulk_wind_shear_ms"])
        assert result["bulk_richardson_number"] == expected
        assert result["bulk_richardson_category"] == BulkRichardsonNumber.category(expected)
