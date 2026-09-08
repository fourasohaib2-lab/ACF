"""
ACF Complexity Engine — sampling real fields/volumes along a path
=====================================================================

Post-processing helpers that sample an ALREADY-COMPUTED real
acf.awci.spatial_field.compute_real_complexity_field() or
acf.awci.vertical_field.compute_real_complexity_volume() result along
a straight lat/lon path or a lon/lat/lat/lon extent - no new
CoupledEarthSolver run is performed here. Built so a dashboard's
regional map, cross-section and route-planning panels can all be
derived from ONE real computation instead of one solver run each.

Real nearest-neighbour lookup throughout (same convention as
ModelConsensusEngine.compute_real_multi_model_disagreement(),
spatial_field.py, vertical_field.py) - never spatial interpolation.
Path distance uses a simple linear lat/lon interpolation between the
two endpoints, not a true geodesic - adequate for a demo route/cross-
section, matching the exact same disclosure
gui/dashboard/awci_synthetic_field.py's own route_profile()/
cross_section_field() already carry for the synthetic path.
"""

from typing import Any

import numpy as np


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlambda / 2) ** 2
    return float(2 * r * np.arcsin(np.sqrt(a)))


def sample_field_along_path(
    lats: Any,
    lons: Any,
    field: np.ndarray,
    point_a: tuple[float, float],
    point_b: tuple[float, float],
    n_points: int = 60,
) -> tuple[list[float], list[float]]:
    """
    Real nearest-neighbour sample of a 2D field (e.g.
    compute_real_complexity_field()'s awci_field) along the straight
    lat/lon path from point_a to point_b.

    Returns
    -------
    (distances_km, values) : both length n_points. values[i] is the
        real field value at the grid point nearest the path's i-th
        sample location - not interpolated between grid points.
    """
    lats_arr = np.asarray(lats)
    lons_arr = np.asarray(lons)
    lat_a, lon_a = point_a
    lat_b, lon_b = point_b
    total_km = _haversine_km(lat_a, lon_a, lat_b, lon_b)

    distances = []
    values = []
    for i in range(n_points):
        t = i / (n_points - 1)
        lat = lat_a + t * (lat_b - lat_a)
        lon = lon_a + t * (lon_b - lon_a)
        lat_idx = int(np.argmin(np.abs(lats_arr - lat)))
        lon_idx = int(np.argmin(np.abs(lons_arr - lon)))
        distances.append(t * total_km)
        values.append(float(field[lat_idx, lon_idx]))

    return distances, values


def sample_volume_cross_section(
    lats: Any,
    lons: Any,
    pressure_hpa_volume: np.ndarray,
    value_volume: np.ndarray,
    point_a: tuple[float, float],
    point_b: tuple[float, float],
    n_along: int = 60,
) -> dict[str, Any]:
    """
    Real nearest-neighbour sample of a 3D volume (e.g.
    compute_real_complexity_volume()'s awci_volume, shape (n_levels,
    n_lat, n_lon)) along the straight lat/lon path from point_a to
    point_b.

    Honest limitation: `mean_pressure_hpa_by_level` is each native
    level's real local pressure AVERAGED across the sampled path
    points, not the true pressure at every individual path point (real
    local pressure does vary somewhat along a long path) - reported
    this way because the cross-section plot needs one y-axis value per
    level, and native levels (not standard pressure levels - see
    vertical_field.py's own honest_limitation) are used throughout ACF
    today.

    Returns
    -------
    dict
        distances_km : list[float], length n_along.
        mean_pressure_hpa_by_level : 1D numpy array, length n_levels.
        grid : 2D numpy array, shape (n_levels, n_along) - grid[level,
            i] is the real value at the point nearest the path's i-th
            sample location, at that native level.
    """
    lats_arr = np.asarray(lats)
    lons_arr = np.asarray(lons)
    lat_a, lon_a = point_a
    lat_b, lon_b = point_b
    total_km = _haversine_km(lat_a, lon_a, lat_b, lon_b)

    n_levels = value_volume.shape[0]
    distances = []
    grid = np.zeros((n_levels, n_along))
    pressure_sum = np.zeros(n_levels)

    for i in range(n_along):
        t = i / (n_along - 1)
        lat = lat_a + t * (lat_b - lat_a)
        lon = lon_a + t * (lon_b - lon_a)
        lat_idx = int(np.argmin(np.abs(lats_arr - lat)))
        lon_idx = int(np.argmin(np.abs(lons_arr - lon)))
        distances.append(t * total_km)
        grid[:, i] = value_volume[:, lat_idx, lon_idx]
        pressure_sum += pressure_hpa_volume[:, lat_idx, lon_idx]

    return {
        "distances_km": distances,
        "mean_pressure_hpa_by_level": pressure_sum / n_along,
        "grid": grid,
    }


def sample_cross_section_hazards(
    lats: Any,
    lons: Any,
    pressure_hpa_volume: np.ndarray,
    temperature_volume: np.ndarray,
    specific_humidity_volume: np.ndarray,
    u_volume: np.ndarray,
    v_volume: np.ndarray,
    point_a: tuple[float, float],
    point_b: tuple[float, float],
    n_along: int = 60,
) -> dict[str, Any]:
    """
    Real per-cell precipitation-phase severity and bulk-wind-shear
    turbulence-risk proxy, sampled along the same real cross-section
    path as sample_volume_cross_section() (docs/reference/
    awci_dashboard_reference.jpg parity work, added 2026-09-03) -
    reuses that same real nearest-neighbour sampling 4 times (T, q, P,
    plus u/v below) rather than reimplementing it.

    Real, disclosed turbulence proxy, not the full CAT index
    -------------------------------------------------------------
    The mockup's own turbulence icons would classically come from the
    Ellrod & Knapp (1992) CAT index (acf.science.wind_turbulence.
    CATIndex) - that needs real HORIZONTAL wind gradients this codebase
    has no per-point pipeline for anywhere. `wind_shear_grid` instead
    reuses the already-real, already-wired
    acf.awci.wind_shear.compute_real_wind_shear_at_point() - real
    VERTICAL bulk shear between each pair of adjacent native levels at
    each path point. A real signal genuinely correlated with
    turbulence risk, but a coarser proxy than the full CAT index -
    never presented as the Ellrod-Knapp index itself.

    Parameters
    ----------
    lats, lons : the real volume's own coordinate arrays.
    pressure_hpa_volume, temperature_volume, specific_humidity_volume,
    u_volume, v_volume : 3D numpy arrays (n_levels, n_lat, n_lon) -
        e.g. compute_real_complexity_volume()'s own real fields.
    point_a, point_b, n_along : same real path convention as
        sample_volume_cross_section().

    Returns
    -------
    dict
        distances_km : list[float], length n_along.
        mean_pressure_hpa_by_level : 1D numpy array, length n_levels -
            same as sample_volume_cross_section(), for the y-axis.
        phase_severity_grid : 2D numpy array (n_levels, n_along), real
            [0, 1] severity from acf.awci.hydrometeor_phase.
            compute_real_hydrometeor_phase_at_point(), using each
            cell's own real sampled T/q/P (not the level-averaged
            mean pressure).
        wind_shear_grid : 2D numpy array (n_levels - 1, n_along), real
            m/s bulk wind shear between each pair of adjacent native
            levels at each path point - see module/function docstring
            for the honest "proxy, not the full CAT index" disclosure.
    """
    from acf.awci.hydrometeor_phase import compute_real_hydrometeor_phase_at_point
    from acf.awci.wind_shear import compute_real_wind_shear_at_point

    temperature_sample = sample_volume_cross_section(lats, lons, pressure_hpa_volume, temperature_volume, point_a, point_b, n_along)
    humidity_sample = sample_volume_cross_section(lats, lons, pressure_hpa_volume, specific_humidity_volume, point_a, point_b, n_along)
    pressure_sample = sample_volume_cross_section(lats, lons, pressure_hpa_volume, pressure_hpa_volume, point_a, point_b, n_along)
    u_sample = sample_volume_cross_section(lats, lons, pressure_hpa_volume, u_volume, point_a, point_b, n_along)
    v_sample = sample_volume_cross_section(lats, lons, pressure_hpa_volume, v_volume, point_a, point_b, n_along)

    n_levels = temperature_volume.shape[0]
    phase_severity_grid = np.zeros((n_levels, n_along))
    for level in range(n_levels):
        for i in range(n_along):
            phase = compute_real_hydrometeor_phase_at_point(
                temperature_k=float(temperature_sample["grid"][level, i]),
                specific_humidity=float(humidity_sample["grid"][level, i]),
                pressure_hpa=float(pressure_sample["grid"][level, i]),
            )
            phase_severity_grid[level, i] = phase["phase_severity"]

    wind_shear_grid = np.zeros((max(0, n_levels - 1), n_along))
    for level in range(n_levels - 1):
        for i in range(n_along):
            shear = compute_real_wind_shear_at_point(
                u_profile=[u_sample["grid"][level, i], u_sample["grid"][level + 1, i]],
                v_profile=[v_sample["grid"][level, i], v_sample["grid"][level + 1, i]],
            )
            wind_shear_grid[level, i] = shear["shear_m_s"]

    return {
        "distances_km": temperature_sample["distances_km"],
        "mean_pressure_hpa_by_level": temperature_sample["mean_pressure_hpa_by_level"],
        "phase_severity_grid": phase_severity_grid,
        "wind_shear_grid": wind_shear_grid,
    }


def real_layer_grids_at_level(volume: dict[str, Any], level_idx: int) -> dict[str, Any]:
    """
    Real per-component map-layer grids at one real native level, from
    `acf.awci.vertical_field.compute_real_complexity_volume()`'s own
    real 3D fields (docs/awci/future-improvements.md §6 - explicit
    user request "je veux rendre tout les boutons de awci en marche"
    closed this for demo mode via
    `acf.gui.dashboard.awci_synthetic_field.awci_layer_grids()`; this
    is the Real Physics mode counterpart).

    Honest scope: the real volume carries temperature/wind_speed/u/v/
    specific_humidity/pressure but NOT cape/precipitation (see that
    function's own docstring - convective/microphysical inputs are not
    part of the real solver state today, same limitation already
    disclosed for the AWCI module scores themselves in Real Physics
    mode). Only the 3 layers derivable from what IS real are returned
    here - a caller (`AWCIMapPanel`) must leave the "CAPE"/
    "Convection"/"Clouds" checkboxes as a real no-op in Real Physics
    mode rather than fabricate a value for them.

    Parameters
    ----------
    volume : a real compute_real_complexity_volume() result.
    level_idx : the real native level index to slice.

    Returns
    -------
    dict with "lats"/"lons" (the volume's own 1D coordinate arrays)
    and "wind" (m/s, real speed magnitude), "turbulence" (m/s per grid
    step, real horizontal gradient magnitude of that same real wind
    field - the same disclosed proxy `awci_layer_grids()` uses, not
    the full Ellrod-Knapp CAT index), "icing" ([0, 1], real
    `acf.awci.hydrometeor_phase` severity from this level's own real
    T/q/P) - each a 2D numpy array (n_lat, n_lon).
    """
    from acf.awci.hydrometeor_phase import compute_real_hydrometeor_phase_at_point

    wind_speed = np.asarray(volume["wind_speed_volume"][level_idx])
    temperature = np.asarray(volume["temperature_volume"][level_idx])
    specific_humidity = np.asarray(volume["specific_humidity_volume"][level_idx])
    pressure_hpa = np.asarray(volume["pressure_volume_hpa"][level_idx])

    d_dlat, d_dlon = np.gradient(wind_speed)
    turbulence = np.hypot(d_dlat, d_dlon)

    n_lat, n_lon = wind_speed.shape
    icing = np.zeros((n_lat, n_lon))
    for i in range(n_lat):
        for j in range(n_lon):
            phase = compute_real_hydrometeor_phase_at_point(
                temperature_k=float(temperature[i, j]),
                specific_humidity=float(specific_humidity[i, j]),
                pressure_hpa=float(pressure_hpa[i, j]),
            )
            icing[i, j] = phase["phase_severity"]

    return {
        "lats": volume["lats"],
        "lons": volume["lons"],
        "wind": wind_speed,
        "turbulence": turbulence,
        "icing": icing,
    }


def crop_field_to_extent(
    lats: Any, lons: Any, field: np.ndarray, extent: tuple[float, float, float, float]
) -> dict[str, Any]:
    """
    Crop a real 2D field (e.g. compute_real_complexity_field()'s
    awci_field, or one level of compute_real_complexity_volume()'s
    awci_volume) to a lon/lat extent - real subsetting of the grid's
    own points, not resampling/regridding.

    Parameters
    ----------
    extent : (lon_min, lon_max, lat_min, lat_max) - same convention as
        gui/dashboard/awci_dashboard.py's _REGIONAL_EXTENT.

    Returns
    -------
    dict
        lons, lats : 1D numpy arrays, the real grid points that fall
            inside the extent (possibly few, if the model's native
            resolution is coarser than the extent - see
            n_points_in_extent).
        field : 2D numpy array, the cropped field.
        n_points_in_extent : (len(lats), len(lons)) - a caller should
            check this is at least (2, 2) before trying to contour it
            (matplotlib's own requirement).
    """
    lon_min, lon_max, lat_min, lat_max = extent
    lats_arr = np.asarray(lats)
    lons_arr = np.asarray(lons)

    lat_mask = (lats_arr >= lat_min) & (lats_arr <= lat_max)
    lon_mask = (lons_arr >= lon_min) & (lons_arr <= lon_max)

    cropped_lats = lats_arr[lat_mask]
    cropped_lons = lons_arr[lon_mask]
    cropped_field = field[np.ix_(lat_mask, lon_mask)]

    return {
        "lats": cropped_lats,
        "lons": cropped_lons,
        "field": cropped_field,
        "n_points_in_extent": (len(cropped_lats), len(cropped_lons)),
    }
