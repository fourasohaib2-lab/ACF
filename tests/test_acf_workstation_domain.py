"""
Tests for acf.gui.dashboard.acf_workstation_domain.
crop_real_volume_to_domain() - the real, Qt-free geographic crop
backing the ACF Scientific Workstation's own "Domain" selector (Phase
40, 2026-09-05).
"""

from __future__ import annotations

import numpy as np
import pytest

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation_domain import DOMAIN_BOUNDS, DOMAIN_NAMES, crop_real_volume_to_domain


def _real_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=20, n_lon=36, n_levels=5, steps=3, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def test_domain_names_start_with_global():
    assert DOMAIN_NAMES[0] == "Global"
    assert set(DOMAIN_NAMES[1:]) == set(DOMAIN_BOUNDS.keys())


def test_crop_shrinks_every_real_lat_lon_shaped_array():
    volume = _real_volume()
    lat_min, lat_max, lon_min, lon_max = DOMAIN_BOUNDS["Western Mediterranean"]

    cropped = crop_real_volume_to_domain(volume, lat_min, lat_max, lon_min, lon_max)

    assert len(cropped["lats"]) < len(volume["lats"])
    assert len(cropped["lons"]) < len(volume["lons"])
    assert cropped["temperature_volume"].shape == (volume["n_levels"], len(cropped["lats"]), len(cropped["lons"]))
    assert cropped["wind_speed_volume"].shape == cropped["temperature_volume"].shape
    assert cropped["u_volume"].shape == cropped["temperature_volume"].shape
    assert cropped["pressure_volume_hpa"].shape == cropped["temperature_volume"].shape


def test_cropped_coordinates_are_genuinely_within_the_real_requested_box():
    volume = _real_volume()
    lat_min, lat_max, lon_min, lon_max = DOMAIN_BOUNDS["North Africa"]

    cropped = crop_real_volume_to_domain(volume, lat_min, lat_max, lon_min, lon_max)

    assert np.all(cropped["lats"] >= lat_min)
    assert np.all(cropped["lats"] <= lat_max)
    assert np.all(cropped["lons"] >= lon_min)
    assert np.all(cropped["lons"] <= lon_max)


def test_cropped_values_match_the_real_full_volume_at_the_same_point():
    """Cross-check discipline: a real cropped cell must equal the exact
    same real value from the uncropped volume - never re-derived or
    interpolated."""
    volume = _real_volume()
    lat_min, lat_max, lon_min, lon_max = DOMAIN_BOUNDS["Western Europe"]

    cropped = crop_real_volume_to_domain(volume, lat_min, lat_max, lon_min, lon_max)

    for real_lat in cropped["lats"][:3]:
        for real_lon in cropped["lons"][:3]:
            full_lat_idx = list(volume["lats"]).index(real_lat)
            full_lon_idx = list(volume["lons"]).index(real_lon)
            crop_lat_idx = list(cropped["lats"]).index(real_lat)
            crop_lon_idx = list(cropped["lons"]).index(real_lon)
            assert (
                cropped["temperature_volume"][0, crop_lat_idx, crop_lon_idx]
                == volume["temperature_volume"][0, full_lat_idx, full_lon_idx]
            )


def test_non_array_fields_pass_through_unchanged():
    volume = _real_volume()
    lat_min, lat_max, lon_min, lon_max = DOMAIN_BOUNDS["North Atlantic"]

    cropped = crop_real_volume_to_domain(volume, lat_min, lat_max, lon_min, lon_max)

    assert cropped["model"] == volume["model"]
    assert cropped["n_levels"] == volume["n_levels"]
    assert cropped["status"] == volume["status"]
    assert cropped["is_real_data"] == volume["is_real_data"]
    assert cropped["honest_limitation"] == volume["honest_limitation"]


def test_crop_raises_a_real_honest_error_when_the_box_is_empty():
    volume = _real_volume()
    with pytest.raises(ValueError, match="real lat point"):
        crop_real_volume_to_domain(volume, lat_min=85.0, lat_max=89.0, lon_min=-179.0, lon_max=-178.0)


def test_crop_raises_a_real_honest_error_when_the_box_is_too_thin_to_render():
    """A real, non-empty but degenerate 1-row/1-column crop must be
    rejected too - matplotlib's own contourf() genuinely cannot render
    fewer than 2x2 points."""
    volume = _real_volume()  # n_lat=20 -> real lat points every ~9.47 degrees
    with pytest.raises(ValueError, match="too few to render"):
        crop_real_volume_to_domain(volume, lat_min=-91.0, lat_max=-85.0, lon_min=-180.0, lon_max=180.0)
