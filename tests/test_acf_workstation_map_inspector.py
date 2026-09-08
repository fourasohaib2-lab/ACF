"""
Tests for acf.gui.dashboard.acf_workstation_map_inspector - the real,
Qt-free per-point diagnostic snapshot/formatting behind the ACF
Scientific Workstation's own Map Inspector (Phase 36, 2026-09-05).
"""

from __future__ import annotations

import math

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation_map_inspector import (
    compute_real_map_inspector_snapshot,
    format_map_inspector_lines,
)


def _real_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=10, n_lon=18, n_levels=5, steps=3, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def test_snapshot_lands_on_a_real_grid_coordinate():
    volume = _real_volume()
    snapshot = compute_real_map_inspector_snapshot(volume, lat=10.3, lon=20.7, level_index=0)

    assert snapshot["lat"] in list(volume["lats"])
    assert snapshot["lon"] in list(volume["lons"])


def test_snapshot_temperature_matches_the_volume_at_the_same_point():
    volume = _real_volume()
    lat, lon = float(volume["lats"][2]), float(volume["lons"][4])

    snapshot = compute_real_map_inspector_snapshot(volume, lat, lon, level_index=0)

    lat_idx = list(volume["lats"]).index(lat)
    lon_idx = list(volume["lons"]).index(lon)
    expected_c = float(volume["temperature_volume"][0, lat_idx, lon_idx]) - 273.15
    assert snapshot["temperature_c"] == expected_c


def test_snapshot_wind_speed_matches_a_real_independent_hypot_computation():
    volume = _real_volume()
    lat, lon = float(volume["lats"][1]), float(volume["lons"][3])

    snapshot = compute_real_map_inspector_snapshot(volume, lat, lon, level_index=0)

    lat_idx = list(volume["lats"]).index(lat)
    lon_idx = list(volume["lons"]).index(lon)
    u = float(volume["u_volume"][0, lat_idx, lon_idx])
    v = float(volume["v_volume"][0, lat_idx, lon_idx])
    assert snapshot["wind_speed_ms"] == math.hypot(u, v)


def test_snapshot_includes_every_real_documented_field():
    volume = _real_volume()
    snapshot = compute_real_map_inspector_snapshot(volume, lat=10.0, lon=20.0, level_index=0)

    for key in (
        "elevation_m", "slope", "aspect_deg", "temperature_c", "wind_speed_ms", "wind_direction_deg",
        "specific_humidity_g_kg", "pressure_hpa", "relative_humidity_pct", "theta_e_k",
        "precipitation_phase", "precipitation_phase_severity", "wet_bulb_c",
        "vorticity_s1", "divergence_s1", "bulk_wind_shear_ms",
    ):
        assert key in snapshot


def test_format_lines_never_raises_on_a_real_snapshot():
    volume = _real_volume()
    snapshot = compute_real_map_inspector_snapshot(volume, lat=10.0, lon=20.0, level_index=0)

    lines = format_map_inspector_lines(snapshot)

    assert any("Lat, Lon" in line for line in lines)
    assert any("CAPE/CIN" in line for line in lines)  # honest deferral disclosed, never silently omitted


def test_format_lines_handles_a_real_none_theta_e_honestly():
    """A genuinely dry point (compute_real_theta_e_at_point's own
    honest None case) must format as "n/a", never crash or fabricate
    a number."""
    volume = _real_volume()
    snapshot = compute_real_map_inspector_snapshot(volume, lat=10.0, lon=20.0, level_index=0)
    snapshot["theta_e_k"] = None
    snapshot["relative_humidity_pct"] = None

    lines = format_map_inspector_lines(snapshot)

    assert any("θ-e: n/a" in line for line in lines)
