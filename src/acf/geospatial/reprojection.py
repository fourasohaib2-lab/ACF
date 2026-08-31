"""
Atmospheric Complexity Framework (ACF)

Geospatial - Reprojection
==========================

Performs actual coordinate transformations, always via pyproj/PROJ
(never a hand-rolled projection formula) and always on a copy - the
mission is explicit that reprojection must never silently mutate the
original data or discard its original CRS (rules #9-11).

Every function here is a pure transform: it takes coordinates/arrays
in, returns new coordinates/arrays out, and never touches an existing
Dataset/array in place.
"""

from __future__ import annotations

from typing import Any

import numpy as np

try:
    from pyproj import Transformer

    HAS_PYPROJ = True
except Exception:  # pragma: no cover
    HAS_PYPROJ = False


def reproject_points(
    x: Any,
    y: Any,
    source_crs: Any,
    target_crs: Any,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Reproject scalar or array coordinates from source_crs to target_crs.

    Parameters
    ----------
    x, y : scalar, list, or numpy array
        Coordinates in source_crs order (longitude/x, latitude/y for
        `always_xy=True`, which this function always uses so that
        callers never have to guess axis order).
    source_crs, target_crs : Any
        Anything pyproj.CRS.from_user_input() accepts.

    Returns
    -------
    (numpy.ndarray, numpy.ndarray)
        New arrays - the inputs are never modified in place.

    Raises
    ------
    RuntimeError
        If pyproj is not installed.
    """
    if not HAS_PYPROJ:
        raise RuntimeError("pyproj is not installed - cannot reproject.")

    transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    new_x, new_y = transformer.transform(x_arr, y_arr)
    return np.asarray(new_x), np.asarray(new_y)


def reproject_dataset_copy(dataset: Any, target_crs: Any, source_crs: Any | None = None) -> Any:
    """
    Return a REPROJECTED COPY of an ACF Dataset - the original dataset
    object passed in is never mutated (mission rule #10: "Toute
    reprojection doit être effectuée sur une copie ou dans une étape
    dédiée du pipeline").

    Expects the dataset to expose "latitude"/"lat" and "longitude"/
    "lon" variables (the acf.data.dataset.Dataset convention already
    used elsewhere in ACF). If those cannot be found, raises rather
    than guessing which variables hold coordinates.

    The returned copy carries a "crs" metadata entry (mission rule
    #11) built by geospatial.metadata.build_crs_metadata(), recording
    BOTH the original and the new CRS - the original CRS is never
    discarded, only the copy's coordinates change.
    """
    import copy as _copy

    from acf.geospatial.metadata import build_crs_metadata

    lon_var = _first_present(dataset, ("longitude", "lon"))
    lat_var = _first_present(dataset, ("latitude", "lat"))
    if lon_var is None or lat_var is None:
        raise ValueError(
            "Dataset has no recognizable longitude/latitude variable ('longitude'/'lon', "
            "'latitude'/'lat') - cannot reproject. Provide explicit coordinate arrays via "
            "reproject_points() instead."
        )

    resolved_source_crs = source_crs
    if resolved_source_crs is None:
        resolved_source_crs = dataset.get_metadata("crs") if dataset.has_metadata("crs") else "EPSG:4326"
        if isinstance(resolved_source_crs, dict):
            resolved_source_crs = resolved_source_crs.get("source_crs", "EPSG:4326")

    new_ds = _copy.deepcopy(dataset)

    lon_vals = dataset.get_variable(lon_var)
    lat_vals = dataset.get_variable(lat_var)
    new_x, new_y = reproject_points(lon_vals, lat_vals, resolved_source_crs, target_crs)

    new_ds.add_variable(lon_var, new_x)
    new_ds.add_variable(lat_var, new_y)

    crs_meta = build_crs_metadata(resolved_source_crs, target_crs)
    new_ds.set_metadata("crs", crs_meta.to_dict())
    new_ds.set_metadata("original_crs", str(resolved_source_crs))

    return new_ds


def round_trip_error(
    x: Any,
    y: Any,
    source_crs: Any,
    target_crs: Any,
) -> dict[str, Any]:
    """
    Reproject source_crs -> target_crs -> source_crs and report the
    residual error, for reversibility testing (mission section 20,
    test 4). Uses geodesic distance (pyproj.Geod) for the residual so
    the error is reported in real meters, not degrees.
    """
    if not HAS_PYPROJ:
        return {"status": "NOT_AVAILABLE_PYPROJ_NOT_INSTALLED"}

    from pyproj import Geod

    fwd_x, fwd_y = reproject_points(x, y, source_crs, target_crs)
    back_x, back_y = reproject_points(fwd_x, fwd_y, target_crs, source_crs)

    geod = Geod(ellps="WGS84")
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    _, _, distance_m = geod.inv(x_arr, y_arr, back_x, back_y)

    return {
        "status": "OK",
        "max_error_m": float(np.max(np.abs(distance_m))),
        "mean_error_m": float(np.mean(np.abs(distance_m))),
    }


def _first_present(dataset: Any, names: tuple[str, ...]) -> str | None:
    for name in names:
        if dataset.has_variable(name):
            return name
    return None
