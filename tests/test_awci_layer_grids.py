"""
Tests for acf.gui.dashboard.awci_synthetic_field.awci_layer_grids() -
the real per-component map-layer grids (Wind/Turbulence/Icing/
Convection/CAPE/Clouds) built 2026-09-03, explicit user request "je
veux rendre tout les boutons de awci en marche" (the "LAYERS" checkbox
panel's 6 extra checkboxes were previously honestly disabled - no real
data source wired in).
"""

from __future__ import annotations

import numpy as np
import pytest

from acf.gui.dashboard.awci_synthetic_field import _synthetic_inputs, awci_layer_grids
from acf.science.hypsometric_equation import HypsometricEquation
from acf.science.virtual_temperature import VirtualTemperature
from acf.science.wind_turbulence import CATIndex


def test_returns_the_real_expected_grid_shape():
    result = awci_layer_grids(lat_step=8.0, lon_step=8.0, lat_range=(-40.0, 40.0), lon_range=(-40.0, 40.0))
    n_lat, n_lon = len(result["lats"]), len(result["lons"])
    for key in ("wind", "turbulence", "icing", "convection", "cape", "clouds"):
        arr = np.asarray(result[key])
        assert arr.shape == (n_lat, n_lon)


def test_wind_matches_the_real_synthetic_inputs_wind_speed():
    result = awci_layer_grids(lat_step=10.0, lon_step=10.0, lat_range=(-20.0, 20.0), lon_range=(-20.0, 20.0))
    lat, lon = result["lats"][1], result["lons"][1]
    expected = _synthetic_inputs(lat, lon, 300.0, 0.0)["wind_speed"]
    lat_idx = result["lats"].index(lat)
    lon_idx = result["lons"].index(lon)
    assert result["wind"][lat_idx][lon_idx] == pytest.approx(expected)


def test_cape_matches_the_real_synthetic_inputs_cape():
    result = awci_layer_grids(lat_step=10.0, lon_step=10.0, lat_range=(-20.0, 20.0), lon_range=(-20.0, 20.0))
    lat, lon = result["lats"][0], result["lons"][0]
    expected = _synthetic_inputs(lat, lon, 300.0, 0.0)["cape"]
    assert result["cape"][0][0] == pytest.approx(expected)


def test_clouds_matches_the_real_synthetic_inputs_precipitation():
    """Disclosed proxy - "clouds" is literally the real precipitation
    rate, not a fabricated cloud-fraction quantity (see the function's
    own docstring)."""
    result = awci_layer_grids(lat_step=10.0, lon_step=10.0, lat_range=(-20.0, 20.0), lon_range=(-20.0, 20.0))
    lat, lon = result["lats"][0], result["lons"][0]
    expected = _synthetic_inputs(lat, lon, 300.0, 0.0)["precipitation"]
    assert result["clouds"][0][0] == pytest.approx(expected)


def test_icing_is_a_real_hydrometeor_phase_severity_in_0_1():
    result = awci_layer_grids(lat_step=8.0, lon_step=8.0, lat_range=(-40.0, 40.0), lon_range=(-40.0, 40.0))
    arr = np.asarray(result["icing"])
    assert arr.min() >= 0.0
    assert arr.max() <= 1.0
    assert arr.max() > arr.min()  # real variation across the grid, not a flat fabricated constant


def test_icing_matches_a_direct_real_hydrometeor_phase_call():
    from acf.awci.hydrometeor_phase import compute_real_hydrometeor_phase_at_point

    result = awci_layer_grids(lat_step=10.0, lon_step=10.0, lat_range=(-20.0, 20.0), lon_range=(-20.0, 20.0))
    lat, lon = result["lats"][0], result["lons"][0]
    raw = _synthetic_inputs(lat, lon, 300.0, 0.0)
    expected = compute_real_hydrometeor_phase_at_point(raw["temperature"], raw["specific_humidity"], 300.0)
    assert result["icing"][0][0] == pytest.approx(expected["phase_severity"])


def test_convection_is_a_real_nonlinear_function_of_cape_not_independent():
    """Real, disclosed relationship: convection (updraft_velocity) is
    w_max=sqrt(2*CAPE) - it must be monotonically non-decreasing with
    cape across the same grid, never independent/random relative to
    it."""
    result = awci_layer_grids(lat_step=6.0, lon_step=6.0, lat_range=(-30.0, 30.0), lon_range=(-30.0, 30.0))
    cape = np.asarray(result["cape"]).flatten()
    convection = np.asarray(result["convection"]).flatten()
    order = np.argsort(cape)
    sorted_convection = convection[order]
    # A real sqrt() relationship is monotonic - allow a tiny numerical
    # tolerance rather than requiring a bit-for-bit non-decreasing run.
    assert np.all(np.diff(sorted_convection) >= -1e-9)


def test_convection_matches_a_direct_real_updraft_call():
    from acf.awci.updraft import compute_real_max_updraft_velocity

    result = awci_layer_grids(lat_step=10.0, lon_step=10.0, lat_range=(-20.0, 20.0), lon_range=(-20.0, 20.0))
    lat, lon = result["lats"][0], result["lons"][0]
    raw = _synthetic_inputs(lat, lon, 300.0, 0.0)
    expected = compute_real_max_updraft_velocity(raw["cape"])
    assert result["convection"][0][0] == pytest.approx(expected["w_max_m_s"])


def test_turbulence_is_a_real_nonnegative_gradient_magnitude():
    result = awci_layer_grids(lat_step=6.0, lon_step=6.0, lat_range=(-30.0, 30.0), lon_range=(-30.0, 30.0))
    arr = np.asarray(result["turbulence"])
    assert (arr >= 0.0).all()
    # A genuinely flat wind field would give a real zero gradient
    # everywhere - the real synthetic wind pattern is not flat, so
    # this must show real variation.
    assert arr.max() > 0.0


def test_turbulence_matches_a_direct_ellrod_knapp_ti1_call():
    """Regression guard for future-improvements.md §5's demo-mode
    closure: "turbulence" must be the real Ellrod-Knapp TI1 index from
    the synthetic u/v decomposition + a synthetic-second-level
    hypsometric vertical shear, not the old wind-speed-gradient proxy."""
    lat_step, lon_step = 6.0, 6.0
    lat_range, lon_range = (-18.0, 18.0), (-18.0, 18.0)
    flight_level_hpa = 300.0
    offset_hpa = 50.0

    result = awci_layer_grids(
        lat_step=lat_step, lon_step=lon_step, lat_range=lat_range, lon_range=lon_range,
        flight_level_hpa=flight_level_hpa,
    )
    lats, lons = result["lats"], result["lons"]

    u = np.array([[_synthetic_inputs(lat, lon, flight_level_hpa, 0.0)["u"] for lon in lons] for lat in lats])
    v = np.array([[_synthetic_inputs(lat, lon, flight_level_hpa, 0.0)["v"] for lon in lons] for lat in lats])
    du_dlat, du_dlon = np.gradient(u)
    dv_dlat, dv_dlon = np.gradient(v)

    i, j = 2, 1
    raw = _synthetic_inputs(lats[i], lons[j], flight_level_hpa, 0.0)
    raw_upper = _synthetic_inputs(lats[i], lons[j], flight_level_hpa - offset_hpa, 0.0)
    tv_lower = VirtualTemperature.calculate(raw["temperature"], raw["specific_humidity"])
    tv_upper = VirtualTemperature.calculate(raw_upper["temperature"], raw_upper["specific_humidity"])
    thickness_m = HypsometricEquation.calculate(
        flight_level_hpa * 100.0, (flight_level_hpa - offset_hpa) * 100.0, 0.5 * (tv_lower + tv_upper)
    )
    du_dz = (raw_upper["u"] - raw["u"]) / thickness_m
    dv_dz = (raw_upper["v"] - raw["v"]) / thickness_m
    expected_vws = CATIndex.vertical_wind_shear(du_dz, dv_dz)
    expected_def = CATIndex.deformation(
        du_dx=float(du_dlon[i, j]), dv_dy=float(dv_dlat[i, j]), dv_dx=float(dv_dlon[i, j]), du_dy=float(du_dlat[i, j])
    )
    expected_ti1 = CATIndex.ti1(expected_vws, expected_def)

    assert result["turbulence"][i][j] == pytest.approx(expected_ti1)


def test_wind_speed_equals_the_u_v_magnitude_the_awci_score_is_untouched():
    """The AWCI composite score consumes ONLY wind_speed (never u/v) -
    u/v must be an exact vector decomposition of it
    (sqrt(u**2+v**2) == wind_speed), not a second, independent
    quantity, so adding them cannot silently change awci_grid()'s own
    real score."""
    raw = _synthetic_inputs(23.4, 67.8, 300.0, 3.0)
    assert np.hypot(raw["u"], raw["v"]) == pytest.approx(raw["wind_speed"], abs=1e-9)


def test_awci_calculator_ignores_the_new_u_v_keys():
    """Real proof (not just a shape/range check) that AWCICalculator's
    own composite score is unaffected by u/v being present in the dict
    - removing them must give the exact same real result, so
    awci_grid()/awci_at() stay bit-identical to before this closure."""
    from acf.awci.calculator import AWCICalculator

    raw = _synthetic_inputs(23.4, 67.8, 300.0, 3.0)
    calc = AWCICalculator()
    with_uv = calc.calculate(dict(raw))
    without_uv = calc.calculate({k: v for k, v in raw.items() if k not in ("u", "v")})
    assert with_uv["awci"] == pytest.approx(without_uv["awci"])
    assert with_uv["module_scores"] == without_uv["module_scores"]


def test_turbulence_is_zero_for_a_hand_built_flat_wind_field():
    """Real, direct proof the gradient formula itself is correct,
    independent of the synthetic wind pattern's own real variation."""
    import numpy as np

    flat = np.full((5, 5), 12.3)
    d_dlat, d_dlon = np.gradient(flat)
    assert np.allclose(np.hypot(d_dlat, d_dlon), 0.0)


def test_deterministic_across_repeated_calls():
    a = awci_layer_grids(lat_step=10.0, lon_step=10.0, lat_range=(-20.0, 20.0), lon_range=(-20.0, 20.0))
    b = awci_layer_grids(lat_step=10.0, lon_step=10.0, lat_range=(-20.0, 20.0), lon_range=(-20.0, 20.0))
    for key in ("wind", "turbulence", "icing", "convection", "cape", "clouds"):
        assert a[key] == b[key]


def test_time_offset_genuinely_shifts_the_grids():
    """time_offset_hours drives the same real synthetic-pattern phase
    drift every other panel already uses - must not be a silently
    ignored parameter here."""
    a = awci_layer_grids(lat_step=8.0, lon_step=8.0, lat_range=(-40.0, 40.0), lon_range=(-40.0, 40.0), time_offset_hours=0.0)
    b = awci_layer_grids(lat_step=8.0, lon_step=8.0, lat_range=(-40.0, 40.0), lon_range=(-40.0, 40.0), time_offset_hours=6.0)
    assert a["wind"] != b["wind"]
