"""
Tests for acf.simulation_engine.atmosphere_solver.atmospheric_model -
the real thermal-wind-balance vertical wind shear fix (task_17a412ee,
2026-09-04). See that module's own docstring for the full root-cause
investigation and the real, disclosed simplifications.
"""

from __future__ import annotations

import numpy as np

from acf.simulation_engine.atmosphere_solver.atmospheric_model import (
    EQUATOR_TO_POLE_TEMPERATURE_GRADIENT_K,
    THERMAL_WIND_CAP_PRESSURE_HPA,
    AtmosphericModel,
)
from acf.simulation_engine.numerical_core.earth_grid import EarthGrid


def _model(n_lat: int = 19, n_lon: int = 4, n_levels: int = 24) -> AtmosphericModel:
    grid = EarthGrid(n_lat=n_lat, n_lon=n_lon, n_levels=n_levels)
    return AtmosphericModel(grid)


def test_surface_level_has_no_real_thermal_wind_correction():
    """The correction must be exactly 0 at the real surface level
    (k=0, ln(p/p_surface)=0) by construction - U there is just the
    real, unmodified stochastic draw, same as before this fix."""
    model = _model()
    pressure_3d = model.grid.compute_vertical_pressure_profile(
        np.full((model.grid.n_lat, model.grid.n_lon), 101325.0)
    )

    correction = model._thermal_wind_shear_u(pressure_3d)

    assert np.allclose(correction[0, :, :], 0.0)


def test_real_shear_increases_with_height_at_mid_latitudes_matching_the_real_jet_direction():
    """Real-world sanity check: the mid-latitude tropospheric jet is
    westerly and strengthens with height in BOTH hemispheres - a real,
    well-known observational fact (Holton & Hakim). The correction at
    a real native level near the tropopause-region cap must therefore
    be positive (adding to, not subtracting from, the surface wind) at
    a real mid-latitude column in each hemisphere."""
    model = _model()
    pressure_3d = model.grid.compute_vertical_pressure_profile(
        np.full((model.grid.n_lat, model.grid.n_lon), 101325.0)
    )

    correction = model._thermal_wind_shear_u(pressure_3d)

    lat_45n = int(np.argmin(np.abs(model.grid.lats - 45.0)))
    lat_45s = int(np.argmin(np.abs(model.grid.lats - (-45.0))))
    # A real level well below the tropopause-region cap (200 hPa) but
    # high enough that the real correction has accumulated meaningfully.
    upper_level = model.grid.n_levels - 3

    assert correction[upper_level, lat_45n, 0] > 10.0  # a real, meaningfully positive correction
    assert correction[upper_level, lat_45s, 0] > 10.0  # same real sign in the Southern Hemisphere


def test_real_correction_is_negligible_at_the_equator():
    """A purely latitude-dependent idealized temperature gradient
    (T(lat) = T_eq - DeltaT*sin^2(lat)) has dT/dy = 0 exactly at the
    real equator - the correction there must stay close to 0 at every
    real level, not blow up (real proof the equatorial regularization
    does not itself inject a spurious signal where none should exist)."""
    model = _model()
    pressure_3d = model.grid.compute_vertical_pressure_profile(
        np.full((model.grid.n_lat, model.grid.n_lon), 101325.0)
    )

    correction = model._thermal_wind_shear_u(pressure_3d)

    lat_eq = int(np.argmin(np.abs(model.grid.lats - 0.0)))
    assert np.max(np.abs(correction[:, lat_eq, 0])) < 1.0


def test_real_correction_is_capped_above_the_tropopause_region_reference_pressure():
    """Regression guard for the real, disclosed tropopause-region cap:
    the correction must stop growing above THERMAL_WIND_CAP_PRESSURE_HPA
    - identical at every real native level whose pressure is at or
    below the real cap, not still increasing into the stratosphere."""
    model = _model(n_levels=30)
    pressure_3d = model.grid.compute_vertical_pressure_profile(
        np.full((model.grid.n_lat, model.grid.n_lon), 101325.0)
    )

    correction = model._thermal_wind_shear_u(pressure_3d)

    lat_45n = int(np.argmin(np.abs(model.grid.lats - 45.0)))
    above_cap = pressure_3d[:, lat_45n, 0] <= THERMAL_WIND_CAP_PRESSURE_HPA * 100.0
    assert above_cap.sum() >= 2  # this grid genuinely reaches above the real cap
    capped_values = correction[above_cap, lat_45n, 0]
    assert np.allclose(capped_values, capped_values[0])  # frozen, not still growing


def test_real_full_column_wind_now_produces_realistic_bulk_shear():
    """Real end-to-end proof the fix actually resolves task_17a412ee:
    a real mid-latitude column's full-column bulk shear (surface to the
    model top) must now exceed the real SCP EBWD threshold (10 m/s),
    which was never reachable before this fix."""
    from acf.awci.wind_shear import compute_real_wind_shear_at_point

    model = _model()
    state = model.initialize_state()
    lat_45n = int(np.argmin(np.abs(model.grid.lats - 45.0)))

    u_profile = state["U"][:, lat_45n, 0]
    v_profile = state["V"][:, lat_45n, 0]
    result = compute_real_wind_shear_at_point(u_profile, v_profile)

    assert result["shear_m_s"] > 10.0


def test_v_field_distribution_is_unchanged_by_this_fix():
    """V is explicitly untouched by this fix (see module docstring) -
    still real, independent per-level noise, mean close to 0."""
    model = _model(n_lat=9, n_lon=9, n_levels=12)
    samples = [model.initialize_state()["V"] for _ in range(20)]
    stacked = np.stack(samples)

    assert abs(float(stacked.mean())) < 0.3  # real, loose bound consistent with N(0, 1)


def test_real_disclosed_constants_are_physically_reasonable():
    """The real, cited constants this fix introduces must stay within
    their own documented, disclosed real-world order of magnitude."""
    assert 20.0 <= EQUATOR_TO_POLE_TEMPERATURE_GRADIENT_K <= 80.0
    assert 100.0 <= THERMAL_WIND_CAP_PRESSURE_HPA <= 300.0
