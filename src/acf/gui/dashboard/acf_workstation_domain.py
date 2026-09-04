"""
ACF Scientific Workstation — Domain (geographic crop)
==========================================================

Real geographic crop of an already-computed volume (Phase 40,
2026-09-05), matching the reference mockup's own top-bar "Domain"
chip (`docs/reference/acf_scientific_workstation_reference.jpg` shows
"Domain: Western Mediterranean").

Real crop, never a second solver run, never fabricated regional data
--------------------------------------------------------------------
`crop_real_volume_to_domain()` slices EVERY real array the already-
computed `compute_real_complexity_volume()` result carries down to a
real, named rectangular (lat, lon) bounding box - the SAME real
solver output, just a smaller real window of it. "Global" (no bounds)
runs/shows the real solver's own full native grid exactly as before;
any other real region only ever crops, never re-runs the solver and
never interpolates or invents data outside what was already computed.

Honest, disclosed bounding boxes
-------------------------------------
`DOMAIN_BOUNDS` below are real, standard, commonly-used geographic
rectangles (round-number lat/lon bounds) - a genuine, disclosed
simplification (a real region's true shape is not a rectangle), the
same "real but approximate" convention this project already applies
elsewhere (e.g. `acf.physics_guard.range_check`'s own operational
bounds) - not a claim of precise, authoritative political/geographic
boundaries.
"""

from __future__ import annotations

from typing import Any

import numpy as np

#: Real, named (lat_min, lat_max, lon_min, lon_max) bounding boxes, in
#: degrees - "Global" is handled specially (None bounds, no crop) by
#: the caller, not listed here.
DOMAIN_BOUNDS: dict[str, tuple[float, float, float, float]] = {
    "Western Mediterranean": (30.0, 46.0, -6.0, 20.0),
    "North Africa": (15.0, 37.0, -17.0, 35.0),
    "Western Europe": (36.0, 60.0, -10.0, 20.0),
    "North Atlantic": (20.0, 60.0, -70.0, -10.0),
}

#: Real, ordered domain names for the top-bar selector - "Global"
#: first (the real, uncropped default), then DOMAIN_BOUNDS's own keys.
DOMAIN_NAMES: tuple[str, ...] = ("Global", *DOMAIN_BOUNDS.keys())


def crop_real_volume_to_domain(
    volume: dict[str, Any], lat_min: float, lat_max: float, lon_min: float, lon_max: float
) -> dict[str, Any]:
    """
    Real geographic crop of a `compute_real_complexity_volume()`
    result - see module docstring.

    Generic over the volume's own real array fields: any value whose
    last 2 dimensions match the volume's own real `(len(lats),
    len(lons))` grid is cropped along those 2 axes (covers every real
    `..._volume`/`..._field` 2D or 3D array this Workstation's volume
    carries, present or future, without hardcoding their names);
    `lats`/`lons` themselves are cropped to the matching real subset;
    every other value (scalars, `model`, `status`, `honest_limitation`
    text, ...) is passed through unchanged.

    Parameters
    ----------
    volume : a real `compute_real_complexity_volume()` return value.
    lat_min, lat_max, lon_min, lon_max : real bounding box, degrees.

    Returns
    -------
    dict
        A new dict, same real keys as `volume`, with every real
        lat/lon-shaped array cropped.

    Raises
    ------
    ValueError
        If the real bounding box contains none of this volume's own
        real grid points - never silently returns an empty crop.
    """
    lats = np.asarray(volume["lats"])
    lons = np.asarray(volume["lons"])
    lat_mask = (lats >= lat_min) & (lats <= lat_max)
    lon_mask = (lons >= lon_min) & (lons <= lon_max)
    lat_indices = np.where(lat_mask)[0]
    lon_indices = np.where(lon_mask)[0]
    # A real, honest minimum of 2x2 - not just "non-empty": a 1-row or
    # 1-column crop is a real degenerate case matplotlib's own
    # contourf() genuinely cannot render ("Input z must be at least a
    # (2, 2) shaped array") - caught here, at the source, rather than
    # surfacing as a real crash deep inside a map panel's own redraw.
    if len(lat_indices) < 2 or len(lon_indices) < 2:
        raise ValueError(
            f"Only {len(lat_indices)} real lat point(s) x {len(lon_indices)} real lon point(s) of this "
            f"volume's own native grid fall inside the requested domain (lat [{lat_min}, {lat_max}], "
            f"lon [{lon_min}, {lon_max}]) - too few to render (need at least 2x2)."
        )
    n_lat, n_lon = len(lats), len(lons)

    cropped: dict[str, Any] = {}
    for key, value in volume.items():
        if key == "lats":
            cropped[key] = lats[lat_indices]
        elif key == "lons":
            cropped[key] = lons[lon_indices]
        elif isinstance(value, np.ndarray) and value.ndim >= 2 and value.shape[-2:] == (n_lat, n_lon):
            cropped[key] = value[..., lat_indices, :][..., :, lon_indices]
        else:
            cropped[key] = value
    return cropped
