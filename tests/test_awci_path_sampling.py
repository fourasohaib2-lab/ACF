"""
Tests for acf.awci.path_sampling - sampling real fields/volumes along a
path or extent (explicit user request "vas-y, branche la carte
régionale/coupe/route sur les vrais champs").

Uses small n_lat/n_lon/n_levels overrides on real
compute_real_complexity_field()/compute_real_complexity_volume() calls
throughout - real solver output, not synthetic/mocked arrays.
"""

import numpy as np
import pytest

from acf.awci.hydrometeor_phase import compute_real_hydrometeor_phase_at_point
from acf.awci.path_sampling import (
    crop_field_to_extent,
    real_layer_grids_at_level,
    sample_cross_section_hazards,
    sample_field_along_path,
    sample_volume_cross_section,
)
from acf.awci.spatial_field import compute_real_complexity_field
from acf.awci.vertical_field import compute_real_complexity_volume
from acf.awci.wind_shear import compute_real_wind_shear_at_point
from acf.science.hypsometric_equation import HypsometricEquation
from acf.science.virtual_temperature import VirtualTemperature
from acf.science.wind_turbulence import CATIndex


def test_sample_field_along_path_returns_real_values_from_the_field():
    result = compute_real_complexity_field(
        model="ALADIN", n_lat=10, n_lon=20, n_levels=4, steps=4, perturbation_scale=3.0, seed=2
    )
    distances, values = sample_field_along_path(
        result["lats"], result["lons"], result["awci_field"], point_a=(10.0, -10.0), point_b=(30.0, 20.0), n_points=15
    )

    assert len(distances) == 15
    assert len(values) == 15
    assert distances[0] == 0.0
    assert distances[-1] > 0.0
    assert distances == sorted(distances)  # monotonically increasing along the path
    for v in values:
        assert 0.0 <= v <= 100.0


def test_sample_field_along_path_matches_real_field_at_the_endpoints():
    """The path's first/last samples must be the field's real nearest-neighbour value at those exact endpoints."""
    result = compute_real_complexity_field(model="ALADIN", n_lat=10, n_lon=20, n_levels=4, steps=2)
    point_a, point_b = (5.0, 5.0), (25.0, 25.0)
    distances, values = sample_field_along_path(
        result["lats"], result["lons"], result["awci_field"], point_a, point_b, n_points=10
    )

    lats_arr = np.asarray(result["lats"])
    lons_arr = np.asarray(result["lons"])
    lat_idx = int(np.argmin(np.abs(lats_arr - point_a[0])))
    lon_idx = int(np.argmin(np.abs(lons_arr - point_a[1])))
    assert values[0] == pytest.approx(float(result["awci_field"][lat_idx, lon_idx]))


def test_sample_volume_cross_section_shape_and_real_values():
    volume = compute_real_complexity_volume(
        model="ALADIN", n_lat=10, n_lon=20, n_levels=6, steps=4, perturbation_scale=3.0, seed=3
    )
    cross = sample_volume_cross_section(
        volume["lats"],
        volume["lons"],
        volume["pressure_volume_hpa"],
        volume["awci_volume"],
        point_a=(10.0, -10.0),
        point_b=(30.0, 20.0),
        n_along=12,
    )

    assert len(cross["distances_km"]) == 12
    assert cross["grid"].shape == (6, 12)
    assert cross["mean_pressure_hpa_by_level"].shape == (6,)
    # Real physics: pressure must decrease with altitude (native level
    # index increasing), same invariant verified in test_awci_vertical_field.py.
    pressures = cross["mean_pressure_hpa_by_level"]
    assert all(pressures[level] > pressures[level + 1] for level in range(len(pressures) - 1))


def test_sample_volume_cross_section_not_a_flat_placeholder():
    volume = compute_real_complexity_volume(
        model="ALADIN", n_lat=10, n_lon=20, n_levels=6, steps=6, perturbation_scale=4.0, seed=4
    )
    cross = sample_volume_cross_section(
        volume["lats"], volume["lons"], volume["pressure_volume_hpa"], volume["awci_volume"],
        point_a=(10.0, -10.0), point_b=(30.0, 20.0), n_along=12,
    )
    assert np.std(cross["grid"]) > 0.0


# --------------------------------- sample_cross_section_hazards (§ dashboard parity)


def _real_volume_for_hazards(**overrides):
    kwargs = dict(model="ALADIN", n_lat=8, n_lon=12, n_levels=6, steps=2, perturbation_scale=3.0, seed=5)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def test_sample_cross_section_hazards_shapes():
    volume = _real_volume_for_hazards()
    result = sample_cross_section_hazards(
        volume["lats"], volume["lons"], volume["pressure_volume_hpa"], volume["temperature_volume"],
        volume["specific_humidity_volume"], volume["u_volume"], volume["v_volume"],
        point_a=(10.0, -10.0), point_b=(30.0, 20.0), n_along=10,
    )
    assert len(result["distances_km"]) == 10
    assert result["phase_severity_grid"].shape == (6, 10)
    assert result["wind_shear_grid"].shape == (5, 10)
    assert result["mean_pressure_hpa_by_level"].shape == (6,)


def test_sample_cross_section_hazards_phase_severity_matches_a_direct_call():
    volume = _real_volume_for_hazards()
    result = sample_cross_section_hazards(
        volume["lats"], volume["lons"], volume["pressure_volume_hpa"], volume["temperature_volume"],
        volume["specific_humidity_volume"], volume["u_volume"], volume["v_volume"],
        point_a=(10.0, -10.0), point_b=(30.0, 20.0), n_along=8,
    )

    t_sample = sample_volume_cross_section(
        volume["lats"], volume["lons"], volume["pressure_volume_hpa"], volume["temperature_volume"],
        (10.0, -10.0), (30.0, 20.0), n_along=8,
    )
    q_sample = sample_volume_cross_section(
        volume["lats"], volume["lons"], volume["pressure_volume_hpa"], volume["specific_humidity_volume"],
        (10.0, -10.0), (30.0, 20.0), n_along=8,
    )
    p_sample = sample_volume_cross_section(
        volume["lats"], volume["lons"], volume["pressure_volume_hpa"], volume["pressure_volume_hpa"],
        (10.0, -10.0), (30.0, 20.0), n_along=8,
    )

    level, i = 2, 3
    expected = compute_real_hydrometeor_phase_at_point(
        float(t_sample["grid"][level, i]), float(q_sample["grid"][level, i]), float(p_sample["grid"][level, i])
    )
    assert result["phase_severity_grid"][level, i] == pytest.approx(expected["phase_severity"])


def test_sample_cross_section_hazards_wind_shear_matches_a_direct_call():
    volume = _real_volume_for_hazards()
    result = sample_cross_section_hazards(
        volume["lats"], volume["lons"], volume["pressure_volume_hpa"], volume["temperature_volume"],
        volume["specific_humidity_volume"], volume["u_volume"], volume["v_volume"],
        point_a=(10.0, -10.0), point_b=(30.0, 20.0), n_along=8,
    )

    u_sample = sample_volume_cross_section(
        volume["lats"], volume["lons"], volume["pressure_volume_hpa"], volume["u_volume"],
        (10.0, -10.0), (30.0, 20.0), n_along=8,
    )
    v_sample = sample_volume_cross_section(
        volume["lats"], volume["lons"], volume["pressure_volume_hpa"], volume["v_volume"],
        (10.0, -10.0), (30.0, 20.0), n_along=8,
    )

    level, i = 1, 5
    expected = compute_real_wind_shear_at_point(
        u_profile=[u_sample["grid"][level, i], u_sample["grid"][level + 1, i]],
        v_profile=[v_sample["grid"][level, i], v_sample["grid"][level + 1, i]],
    )
    assert result["wind_shear_grid"][level, i] == pytest.approx(expected["shear_m_s"])


def test_sample_cross_section_hazards_wind_shear_is_never_negative():
    volume = _real_volume_for_hazards(seed=7, perturbation_scale=5.0)
    result = sample_cross_section_hazards(
        volume["lats"], volume["lons"], volume["pressure_volume_hpa"], volume["temperature_volume"],
        volume["specific_humidity_volume"], volume["u_volume"], volume["v_volume"],
        point_a=(10.0, -10.0), point_b=(30.0, 20.0), n_along=10,
    )
    assert np.all(result["wind_shear_grid"] >= 0.0)


def test_sample_cross_section_hazards_phase_severity_bounded_0_1():
    volume = _real_volume_for_hazards(seed=9, perturbation_scale=6.0)
    result = sample_cross_section_hazards(
        volume["lats"], volume["lons"], volume["pressure_volume_hpa"], volume["temperature_volume"],
        volume["specific_humidity_volume"], volume["u_volume"], volume["v_volume"],
        point_a=(10.0, -10.0), point_b=(30.0, 20.0), n_along=10,
    )
    assert np.all(result["phase_severity_grid"] >= 0.0)
    assert np.all(result["phase_severity_grid"] <= 1.0)


# ------------------------------------------- real_layer_grids_at_level (§12 LAYERS)


def test_real_layer_grids_at_level_shapes():
    volume = _real_volume_for_hazards()
    result = real_layer_grids_at_level(volume, level_idx=2)
    n_lat, n_lon = len(volume["lats"]), len(volume["lons"])
    for key in ("wind", "turbulence", "icing"):
        assert result[key].shape == (n_lat, n_lon)


def test_real_layer_grids_at_level_wind_matches_the_real_volume_directly():
    volume = _real_volume_for_hazards()
    result = real_layer_grids_at_level(volume, level_idx=3)
    assert np.array_equal(result["wind"], volume["wind_speed_volume"][3])


def test_real_layer_grids_at_level_icing_matches_a_direct_real_call():
    volume = _real_volume_for_hazards()
    result = real_layer_grids_at_level(volume, level_idx=1)
    i, j = 2, 4
    expected = compute_real_hydrometeor_phase_at_point(
        float(volume["temperature_volume"][1, i, j]),
        float(volume["specific_humidity_volume"][1, i, j]),
        float(volume["pressure_volume_hpa"][1, i, j]),
    )
    assert result["icing"][i, j] == pytest.approx(expected["phase_severity"])


def test_real_layer_grids_at_level_icing_bounded_0_1():
    volume = _real_volume_for_hazards(seed=11, perturbation_scale=6.0)
    result = real_layer_grids_at_level(volume, level_idx=0)
    assert np.all(result["icing"] >= 0.0)
    assert np.all(result["icing"] <= 1.0)


def test_real_layer_grids_at_level_turbulence_is_nonnegative():
    volume = _real_volume_for_hazards()
    result = real_layer_grids_at_level(volume, level_idx=2)
    # TI1 = VWS * DEF, both real non-negative magnitudes (sqrt of a
    # sum of squares) - the product can never be negative.
    assert np.all(result["turbulence"] >= 0.0)


def test_real_layer_grids_at_level_turbulence_matches_a_direct_ellrod_knapp_ti1_call():
    """Regression guard for future-improvements.md §5's Real Physics
    closure: "turbulence" must be the real Ellrod-Knapp TI1 index
    computed from the real u/v horizontal gradients and a real
    hypsometric-equation vertical shear, not the old wind-speed-
    gradient proxy."""
    volume = _real_volume_for_hazards(seed=13, perturbation_scale=4.0)
    level_idx = 2
    result = real_layer_grids_at_level(volume, level_idx=level_idx)

    u = volume["u_volume"][level_idx]
    v = volume["v_volume"][level_idx]
    du_dlat, du_dlon = np.gradient(u)
    dv_dlat, dv_dlon = np.gradient(v)

    i, j = 3, 5
    neighbor_idx = level_idx + 1
    p_here = float(volume["pressure_volume_hpa"][level_idx, i, j]) * 100.0
    p_neighbor = float(volume["pressure_volume_hpa"][neighbor_idx, i, j]) * 100.0
    assert p_here > p_neighbor  # pressure must decrease with the real solver's own level ordering

    tv_here = VirtualTemperature.calculate(
        float(volume["temperature_volume"][level_idx, i, j]), float(volume["specific_humidity_volume"][level_idx, i, j])
    )
    tv_neighbor = VirtualTemperature.calculate(
        float(volume["temperature_volume"][neighbor_idx, i, j]),
        float(volume["specific_humidity_volume"][neighbor_idx, i, j]),
    )
    thickness_m = HypsometricEquation.calculate(p_here, p_neighbor, 0.5 * (tv_here + tv_neighbor))

    du_dz = (float(volume["u_volume"][neighbor_idx, i, j]) - float(volume["u_volume"][level_idx, i, j])) / thickness_m
    dv_dz = (float(volume["v_volume"][neighbor_idx, i, j]) - float(volume["v_volume"][level_idx, i, j])) / thickness_m
    expected_vws = CATIndex.vertical_wind_shear(du_dz, dv_dz)
    expected_def = CATIndex.deformation(
        du_dx=float(du_dlon[i, j]), dv_dy=float(dv_dlat[i, j]), dv_dx=float(dv_dlon[i, j]), du_dy=float(du_dlat[i, j])
    )
    expected_ti1 = CATIndex.ti1(expected_vws, expected_def)

    assert result["turbulence"][i, j] == pytest.approx(expected_ti1)


def test_real_layer_grids_at_level_has_no_clouds_key():
    """Honest scope guard: the real solver volume carries no real
    precipitation field, so this function must never fabricate a
    "clouds" layer. "cape"/"convection" ARE real here (closed
    2026-09-11, future-improvements.md §6) - see the dedicated tests
    below."""
    volume = _real_volume_for_hazards()
    result = real_layer_grids_at_level(volume, level_idx=0)
    assert "clouds" not in result


def test_real_layer_grids_at_level_cape_matches_a_direct_real_call():
    from acf.awci.convective_energy import compute_real_cape_cin_at_point

    volume = _real_volume_for_hazards()
    level_idx = 0
    result = real_layer_grids_at_level(volume, level_idx=level_idx)
    i, j = 2, 4
    expected = compute_real_cape_cin_at_point(
        temperature_profile_k=volume["temperature_volume"][:, i, j],
        specific_humidity_profile=volume["specific_humidity_volume"][:, i, j],
        pressure_profile_hpa=volume["pressure_volume_hpa"][:, i, j],
    )
    assert expected["is_real_data"]
    assert result["cape"][i, j] == pytest.approx(expected["cape_j_kg"])
    assert not np.isnan(result["cape"][i, j])


def test_real_layer_grids_at_level_cape_is_independent_of_level_idx():
    """Real CAPE describes a whole sounding, not one flight level - the
    grid must be identical regardless of which level_idx is requested,
    unlike wind/icing/turbulence."""
    volume = _real_volume_for_hazards()
    cape_at_0 = real_layer_grids_at_level(volume, level_idx=0)["cape"]
    cape_at_2 = real_layer_grids_at_level(volume, level_idx=2)["cape"]
    assert np.array_equal(cape_at_0, cape_at_2, equal_nan=True)


def test_real_layer_grids_at_level_convection_matches_a_direct_real_call():
    from acf.awci.updraft import compute_real_max_updraft_velocity

    volume = _real_volume_for_hazards()
    level_idx = 0
    result = real_layer_grids_at_level(volume, level_idx=level_idx)
    i, j = 2, 4
    assert not np.isnan(result["cape"][i, j])
    expected = compute_real_max_updraft_velocity(float(result["cape"][i, j]))
    assert result["convection"][i, j] == pytest.approx(expected["w_max_m_s"])


def test_crop_field_to_extent_keeps_only_points_inside_it():
    result = compute_real_complexity_field(model="ARPEGE", n_lat=20, n_lon=40, n_levels=4, steps=2)
    extent = (-12.0, 35.0, 15.0, 40.0)  # lon_min, lon_max, lat_min, lat_max (North Africa)

    cropped = crop_field_to_extent(result["lats"], result["lons"], result["awci_field"], extent)

    assert all(extent[2] <= lat <= extent[3] for lat in cropped["lats"])
    assert all(extent[0] <= lon <= extent[1] for lon in cropped["lons"])
    assert cropped["field"].shape == (len(cropped["lats"]), len(cropped["lons"]))
    assert cropped["n_points_in_extent"] == (len(cropped["lats"]), len(cropped["lons"]))


def test_crop_field_to_extent_values_are_real_not_recomputed():
    result = compute_real_complexity_field(model="ARPEGE", n_lat=20, n_lon=40, n_levels=4, steps=2)
    extent = (-12.0, 35.0, 15.0, 40.0)
    cropped = crop_field_to_extent(result["lats"], result["lons"], result["awci_field"], extent)

    lats_arr = np.asarray(result["lats"])
    lons_arr = np.asarray(result["lons"])
    lat_mask = (lats_arr >= extent[2]) & (lats_arr <= extent[3])
    lon_mask = (lons_arr >= extent[0]) & (lons_arr <= extent[1])
    expected = result["awci_field"][np.ix_(lat_mask, lon_mask)]
    np.testing.assert_array_equal(cropped["field"], expected)
