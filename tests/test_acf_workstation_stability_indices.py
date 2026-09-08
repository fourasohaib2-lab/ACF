"""
Tests for acf.gui.dashboard.acf_workstation_stability_indices.
compute_real_stability_indices_at_point - the real, Qt-free per-point
stability summary (Phase 39, 2026-09-05).
"""

from __future__ import annotations

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
