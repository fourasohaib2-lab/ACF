"""
Real shape-consistency checking between a field array and its coordinate arrays.

Honest scope (see package docstring): covers the specific 2D (lat, lon)
/ 3D (level, lat, lon) convention ACF's own real fields already use
throughout (acf.awci.spatial_field/vertical_field/temporal_field,
acf.storage.writer) - not a fully generic tensor dimensional-analysis
engine for arbitrary array conventions.
"""

from typing import Any

from acf.core.exceptions import DimensionError


def check_field_shape(
    field: Any, lats: Any, lons: Any, levels: Any | None = None
) -> None:
    """
    Verify `field`'s shape is consistent with its coordinate arrays,
    using ACF's own real (lat, lon) / (level, lat, lon) convention.

    Parameters
    ----------
    field : array-like
        2D (n_lat, n_lon) or 3D (n_levels, n_lat, n_lon).
    lats, lons : 1D array-like.
    levels : 1D array-like, optional - required (and checked) only if
        `field` is 3D.

    Raises
    ------
    DimensionError
        If field.ndim is not 2 or 3, or any coordinate array's length
        doesn't match field's corresponding axis, or field is 3D but
        `levels` was not supplied.
    """
    ndim = getattr(field, "ndim", None)
    if ndim is None:
        raise DimensionError(f"field has no .ndim - expected a real array, got {type(field)!r}")

    if ndim == 2:
        n_lat, n_lon = field.shape
        if len(lats) != n_lat:
            raise DimensionError(f"field has {n_lat} latitude rows but lats has {len(lats)} entries")
        if len(lons) != n_lon:
            raise DimensionError(f"field has {n_lon} longitude columns but lons has {len(lons)} entries")
        return

    if ndim == 3:
        if levels is None:
            raise DimensionError("field is 3D (level, lat, lon) but no levels array was supplied")
        n_levels, n_lat, n_lon = field.shape
        if len(levels) != n_levels:
            raise DimensionError(f"field has {n_levels} levels but levels array has {len(levels)} entries")
        if len(lats) != n_lat:
            raise DimensionError(f"field has {n_lat} latitude rows but lats has {len(lats)} entries")
        if len(lons) != n_lon:
            raise DimensionError(f"field has {n_lon} longitude columns but lons has {len(lons)} entries")
        return

    raise DimensionError(f"field has {ndim} dimensions - expected 2 (lat, lon) or 3 (level, lat, lon)")
