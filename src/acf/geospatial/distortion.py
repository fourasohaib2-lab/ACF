"""
Atmospheric Complexity Framework (ACF)

Geospatial - Distortion Diagnostics
=====================================

Reports how much a CRS distorts angles, area, distance, and scale over
a given bounding box (mission section 11), by comparing a real
geodesic computation (pyproj.Geod, i.e. the true ellipsoidal answer)
against the same computation carried out naively in the CRS itself.

This intentionally does not implement a general Tissot's-indicatrix
distortion model - pyproj/PROJ already provides everything needed to
measure the distortion that actually matters for ACF's use cases
(is a distance/area computed in this CRS trustworthy or not), and the
mission itself says not to reimplement what a reliable library already
provides (section 11).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

try:
    from pyproj import CRS, Geod, Transformer

    HAS_PYPROJ = True
except Exception:  # pragma: no cover
    HAS_PYPROJ = False


@dataclass
class DistortionReport:
    """
    Distortion diagnostic for one CRS over one bounding box.

    distance_distortion_pct : how far a naive Euclidean distance in
        the CRS's own coordinates/units diverges from the true
        geodesic distance across the box's diagonal, as a percentage.
    area_distortion_pct : same, but for the box's area.
    is_conformal / is_equal_area : whether pyproj reports the CRS as
        angle-preserving / area-preserving by construction (from the
        CRS's own coordinate operation metadata, not measured).
    """

    crs: str
    is_geographic: bool
    is_conformal: bool | None
    is_equal_area: bool | None
    distance_distortion_pct: float | None
    area_distortion_pct: float | None
    warning: str | None = None


def assess_distortion(crs_input: Any, bounds: tuple[float, float, float, float]) -> DistortionReport:
    """
    Assess distortion of `crs_input` over bounds (min_lon, min_lat,
    max_lon, max_lat).

    For a geographic CRS (e.g. EPSG:4326), degree-based distance/area
    are not meaningful at all, so this reports the CRS as geographic
    and flags a warning instead of computing a misleading percentage
    (mission's core concern: never use raw lat/lon degrees for
    distance/area).
    """
    min_lon, min_lat, max_lon, max_lat = bounds

    if not HAS_PYPROJ:
        return DistortionReport(
            crs=str(crs_input),
            is_geographic=False,
            is_conformal=None,
            is_equal_area=None,
            distance_distortion_pct=None,
            area_distortion_pct=None,
            warning="pyproj not installed - cannot assess distortion.",
        )

    crs = crs_input if isinstance(crs_input, CRS) else CRS.from_user_input(crs_input)

    if crs.is_geographic:
        return DistortionReport(
            crs=str(crs_input),
            is_geographic=True,
            is_conformal=None,
            is_equal_area=None,
            distance_distortion_pct=None,
            area_distortion_pct=None,
            warning="Geographic CRS (degrees) - distance/area cannot be measured directly in "
            "this CRS; reproject to a projected CRS first (e.g. via recommend_projection()).",
        )

    method_name = (crs.coordinate_operation.method_name or "").lower() if crs.coordinate_operation else ""
    is_conformal = any(term in method_name for term in ("mercator", "conformal", "stereographic")) or None
    is_equal_area = "equal area" in method_name or "albers" in method_name or None

    geod = Geod(ellps="WGS84")
    true_distance_m = geod.inv(min_lon, min_lat, max_lon, max_lat)[2]
    _, _, true_area_m2, _ = _geodesic_polygon_area(geod, min_lon, min_lat, max_lon, max_lat)

    transformer = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    x0, y0 = transformer.transform(min_lon, min_lat)
    x1, y1 = transformer.transform(max_lon, max_lat)
    naive_distance = float(np.hypot(x1 - x0, y1 - y0))
    naive_area = float(abs(x1 - x0) * abs(y1 - y0))

    distance_pct = _pct_diff(naive_distance, true_distance_m)
    area_pct = _pct_diff(naive_area, true_area_m2)

    return DistortionReport(
        crs=str(crs_input),
        is_geographic=False,
        is_conformal=is_conformal,
        is_equal_area=is_equal_area,
        distance_distortion_pct=distance_pct,
        area_distortion_pct=area_pct,
    )


def _geodesic_polygon_area(geod: Geod, min_lon: float, min_lat: float, max_lon: float, max_lat: float):
    lons = [min_lon, max_lon, max_lon, min_lon]
    lats = [min_lat, min_lat, max_lat, max_lat]
    area_m2, perimeter_m = geod.polygon_area_perimeter(lons, lats)
    return lons, lats, abs(area_m2), perimeter_m


def _pct_diff(measured: float, reference: float) -> float | None:
    if reference == 0:
        return None
    return round(100.0 * (measured - reference) / reference, 4)
