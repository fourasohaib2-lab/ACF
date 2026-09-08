"""
Tests for acf.awci.workstation_fields.compute_real_convection_indices_field()
- the real severe-convection composite pipeline (CAPE/CIN, LCL, Bunkers
storm motion, storm-relative helicity, EHI/SCP/STP) backing the AWCI-free
ACF Scientific Workstation's Convection Lab (added 2026-09-04, Phase 18).
"""

from __future__ import annotations

import numpy as np

from acf.awci.convective_energy import compute_real_cape_cin_at_point
from acf.awci.theta_e import compute_real_theta_e_at_point
from acf.awci.wind_shear import compute_real_wind_shear_at_point
from acf.awci.workstation_fields import compute_real_convection_indices_field
from acf.science.lcl import LCL
from acf.science.severe_weather import SevereWeather
from acf.science.storm_motion import StormMotion
from acf.science.storm_relative_helicity import StormRelativeHelicity


def _synthetic_profile(n_levels: int = 6) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Real, hand-shaped vertical profile - realistic enough for a
    genuine MetPy parcel ascent to succeed, matching the same
    convention already used in test_acf_workstation_thermodynamics.py's
    own _synthetic_profile() helper."""
    pressure_hpa = np.linspace(1000.0, 500.0, n_levels)
    temperature_k = np.linspace(298.0, 260.0, n_levels)
    specific_humidity = np.linspace(0.012, 0.001, n_levels)
    return temperature_k, specific_humidity, pressure_hpa


def _synthetic_wind(n_levels: int = 6) -> tuple[np.ndarray, np.ndarray]:
    """Real, hand-shaped wind profile with genuine (non-zero) shear -
    veering with height, a real hodograph shape, not a degenerate
    uniform wind."""
    u_profile = np.linspace(2.0, 18.0, n_levels)
    v_profile = np.linspace(-3.0, 9.0, n_levels)
    return u_profile, v_profile


def _build_volume(n_lat: int, n_lon: int, n_levels: int = 6):
    t_profile, q_profile, p_profile = _synthetic_profile(n_levels)
    u_profile, v_profile = _synthetic_wind(n_levels)

    lon_warm = np.linspace(0.0, 3.0, n_lon)
    temperature_volume = np.broadcast_to(t_profile[:, None, None], (n_levels, n_lat, n_lon)).copy()
    temperature_volume += lon_warm[None, None, :]
    specific_humidity_volume = np.broadcast_to(q_profile[:, None, None], (n_levels, n_lat, n_lon)).copy()
    pressure_volume_hpa = np.broadcast_to(p_profile[:, None, None], (n_levels, n_lat, n_lon)).copy()
    u_volume = np.broadcast_to(u_profile[:, None, None], (n_levels, n_lat, n_lon)).copy()
    v_volume = np.broadcast_to(v_profile[:, None, None], (n_levels, n_lat, n_lon)).copy()
    lats = np.linspace(30.0, 40.0, n_lat)
    lons = np.linspace(0.0, 10.0, n_lon)
    return temperature_volume, specific_humidity_volume, pressure_volume_hpa, u_volume, v_volume, lats, lons


def test_convection_indices_match_the_real_underlying_formulas_directly():
    """Cross-check discipline: every real strided grid cell must equal
    an independent, direct call to each real underlying formula on
    that exact real column - never a separately re-derived value."""
    n_lat, n_lon, stride = 6, 8, 2
    temperature_volume, specific_humidity_volume, pressure_volume_hpa, u_volume, v_volume, lats, lons = (
        _build_volume(n_lat, n_lon)
    )

    result = compute_real_convection_indices_field(
        temperature_volume, specific_humidity_volume, pressure_volume_hpa, u_volume, v_volume, lats, lons,
        stride=stride,
    )

    assert np.array_equal(result["lats"], lats[::stride])
    assert np.array_equal(result["lons"], lons[::stride])
    for key in ("cape_j_kg", "cin_j_kg", "lcl_m", "bulk_shear_m_s", "srh_m2_s2", "ehi", "scp", "stp"):
        assert result[key].shape == (len(lats[::stride]), len(lons[::stride]))

    row_indices = list(range(0, n_lat, stride))
    col_indices = list(range(0, n_lon, stride))
    for si, i in enumerate(row_indices):
        for sj, j in enumerate(col_indices):
            t_profile = temperature_volume[:, i, j]
            q_profile = specific_humidity_volume[:, i, j]
            p_profile = pressure_volume_hpa[:, i, j]
            u_profile = u_volume[:, i, j]
            v_profile = v_volume[:, i, j]

            cape_cin = compute_real_cape_cin_at_point(t_profile, q_profile, p_profile)
            assert cape_cin["is_real_data"] is True
            cape = cape_cin["cape_j_kg"]
            cin_magnitude = cape_cin["cin_j_kg"]
            assert result["cape_j_kg"][si, sj] == cape
            assert result["cin_j_kg"][si, sj] == cin_magnitude

            theta_e_result = compute_real_theta_e_at_point(
                float(t_profile[0]), float(q_profile[0]), float(p_profile[0])
            )
            assert theta_e_result["is_real_data"] is True
            expected_lcl = LCL.calculate_bolton(float(t_profile[0]), theta_e_result["dewpoint_k"])
            assert result["lcl_m"][si, sj] == expected_lcl

            shear_result = compute_real_wind_shear_at_point(u_profile, v_profile)
            expected_bulk_shear = shear_result["shear_m_s"]
            assert result["bulk_shear_m_s"][si, sj] == expected_bulk_shear

            shear_u = float(u_profile[-1] - u_profile[0])
            shear_v = float(v_profile[-1] - v_profile[0])
            mean_u, mean_v = float(u_profile.mean()), float(v_profile.mean())
            storm_motion = StormMotion.calculate_bunkers(mean_u, mean_v, shear_u, shear_v)
            expected_srh = StormRelativeHelicity.calculate_profile(
                list(u_profile), list(v_profile), *storm_motion["right_mover"]
            )
            assert result["srh_m2_s2"][si, sj] == expected_srh

            expected_ehi = SevereWeather.energy_helicity_index(cape, expected_srh)
            assert result["ehi"][si, sj] == expected_ehi

            expected_scp = SevereWeather.supercell_composite_parameter(
                mucape=cape, effective_srh=expected_srh, effective_bulk_shear=expected_bulk_shear,
                mucin=-cin_magnitude,
            )
            assert result["scp"][si, sj] == expected_scp

            expected_stp = SevereWeather.significant_tornado_parameter_fixed(
                sbcape=cape, sblcl_m=expected_lcl, srh_1km=expected_srh, shear_6km=expected_bulk_shear,
            )
            assert result["stp"][si, sj] == expected_stp


def test_convection_indices_return_a_real_coarser_grid_not_the_native_resolution():
    """Honest performance trade-off (see module docstring): the
    returned grid is genuinely smaller than the native one, not a
    same-size grid with gaps."""
    n_lat, n_lon, stride = 9, 11, 3
    temperature_volume, specific_humidity_volume, pressure_volume_hpa, u_volume, v_volume, lats, lons = (
        _build_volume(n_lat, n_lon)
    )

    result = compute_real_convection_indices_field(
        temperature_volume, specific_humidity_volume, pressure_volume_hpa, u_volume, v_volume, lats, lons,
        stride=stride,
    )

    assert result["cape_j_kg"].shape[0] < n_lat
    assert result["cape_j_kg"].shape[1] < n_lon
    assert not np.isnan(result["cape_j_kg"]).any()  # every real coarser-grid cell was actually computed


def test_convection_indices_are_honestly_nan_for_a_genuinely_zero_shear_column():
    """A genuinely zero shear vector leaves Bunkers storm motion's
    deviation direction undefined (see StormMotion.calculate_bunkers()'s
    own docstring) - SRH/EHI/SCP/STP must be honestly NaN there, never
    a fabricated value. CAPE/CIN/LCL/bulk-shear-magnitude are unaffected
    (they don't depend on the shear vector's direction) and must still
    be real, non-NaN numbers."""
    n_levels = 6
    t_profile, q_profile, p_profile = _synthetic_profile(n_levels)
    uniform_u = np.full(n_levels, 5.0)  # zero shear: same wind at every level
    uniform_v = np.full(n_levels, -2.0)

    temperature_volume = t_profile[:, None, None]
    specific_humidity_volume = q_profile[:, None, None]
    pressure_volume_hpa = p_profile[:, None, None]
    u_volume = uniform_u[:, None, None]
    v_volume = uniform_v[:, None, None]
    lats = np.array([30.0])
    lons = np.array([0.0])

    result = compute_real_convection_indices_field(
        temperature_volume, specific_humidity_volume, pressure_volume_hpa, u_volume, v_volume, lats, lons,
        stride=1,
    )

    assert not np.isnan(result["cape_j_kg"][0, 0])
    assert not np.isnan(result["cin_j_kg"][0, 0])
    assert not np.isnan(result["lcl_m"][0, 0])
    assert not np.isnan(result["bulk_shear_m_s"][0, 0])
    assert result["bulk_shear_m_s"][0, 0] == 0.0
    assert np.isnan(result["srh_m2_s2"][0, 0])
    assert np.isnan(result["ehi"][0, 0])
    assert np.isnan(result["scp"][0, 0])
    assert np.isnan(result["stp"][0, 0])


def test_convection_indices_are_honestly_nan_for_a_genuinely_dry_lcl_input():
    """A genuinely zero-humidity surface point has no real dewpoint
    (see compute_real_theta_e_at_point()'s own docstring) - LCL and,
    downstream, STP (which needs a real LCL) must be honestly NaN,
    never a fabricated value. CAPE/CIN can still be real numbers since
    they are computed from the full profile, not just the surface
    point."""
    n_levels = 6
    t_profile, _, p_profile = _synthetic_profile(n_levels)
    q_profile = np.linspace(0.0, 0.001, n_levels)  # zero surface humidity
    u_profile, v_profile = _synthetic_wind(n_levels)

    temperature_volume = t_profile[:, None, None]
    specific_humidity_volume = q_profile[:, None, None]
    pressure_volume_hpa = p_profile[:, None, None]
    u_volume = u_profile[:, None, None]
    v_volume = v_profile[:, None, None]
    lats = np.array([30.0])
    lons = np.array([0.0])

    result = compute_real_convection_indices_field(
        temperature_volume, specific_humidity_volume, pressure_volume_hpa, u_volume, v_volume, lats, lons,
        stride=1,
    )

    assert np.isnan(result["lcl_m"][0, 0])
    assert np.isnan(result["stp"][0, 0])  # STP needs a real LCL input
