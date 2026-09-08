"""
Atmospheric Complexity Framework (ACF)

Geospatial - CRS Metadata
=========================

Standardized metadata describing a coordinate reference system (CRS) and
any reprojection applied to a dataset, so that:

- the original CRS of a dataset is never lost when a copy is reprojected
  (mission rule #11: "Le système de coordonnées des données originales
  doit toujours être conservé dans les métadonnées");
- every ACF cartographic result documents the CRS it was produced in
  (mission section 13).

This module deliberately does not perform any transformation itself -
see reprojection.py for that. It only builds/reads structured metadata
from real pyproj.CRS objects (never invents values).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

try:
    from pyproj import CRS

    HAS_PYPROJ = True
except Exception:  # pragma: no cover - pyproj is a declared ACF dependency
    HAS_PYPROJ = False


@dataclass
class CRSMetadata:
    """
    Structured CRS/reprojection metadata (mission section 13).

    All fields are Optional because a given transformation may not use
    every parameter (e.g. a geographic CRS has no false_easting) - unset
    fields are left as None rather than fabricated, consistent with the
    rest of ACF's "never fabricate a value that wasn't actually
    determined" convention.
    """

    source_crs: str | None = None
    target_crs: str | None = None
    projection_method: str | None = None
    datum: str | None = None
    ellipsoid: str | None = None
    units: str | None = None
    central_meridian: float | None = None
    latitude_of_origin: float | None = None
    standard_parallel_1: float | None = None
    standard_parallel_2: float | None = None
    scale_factor: float | None = None
    false_easting: float | None = None
    false_northing: float | None = None
    transformation_date: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def describe_crs(crs_input: Any) -> dict[str, Any]:
    """
    Build an honest description of a single CRS: whether it is
    geographic or projected, its datum, ellipsoid, units, EPSG code,
    and (if projected) its projection method and parameters.

    Mission section 15: explicitly distinguishes CRS / datum /
    ellipsoid / projection method / projection parameters / units -
    e.g. EPSG:9802 must be identified as a *projection method*
    ("Lambert Conformal Conic 2SP"), never as a complete CRS, and
    EPSG:4326 must be identified as a *geographic CRS*, never as a
    "projection" (mission section 4).

    Parameters
    ----------
    crs_input : Any
        Anything pyproj.CRS.from_user_input() accepts: an EPSG code
        ("EPSG:4326"), an integer EPSG code, a WKT string, a proj4
        string, or an existing pyproj.CRS instance.

    Returns
    -------
    dict
        {"status": "NOT_AVAILABLE_PYPROJ_NOT_INSTALLED"} if pyproj is
        unavailable, or {"status": "INVALID_CRS", "error": ...} if the
        input cannot be parsed - never a silently-guessed CRS
        description (mission rule #13: "Si un CRS est ambigu, ne
        l'invente pas").
    """
    if not HAS_PYPROJ:
        return {"status": "NOT_AVAILABLE_PYPROJ_NOT_INSTALLED"}

    try:
        crs = crs_input if isinstance(crs_input, CRS) else CRS.from_user_input(crs_input)
    except Exception as exc:
        return {"status": "INVALID_CRS", "error": str(exc), "input": str(crs_input)}

    is_geographic = crs.is_geographic
    is_projected = crs.is_projected

    result: dict[str, Any] = {
        "status": "OK",
        "name": crs.name,
        "epsg": crs.to_epsg(),
        "is_geographic": is_geographic,
        "is_projected": is_projected,
        "datum": crs.datum.name if crs.datum is not None else None,
        "ellipsoid": crs.ellipsoid.name if crs.ellipsoid is not None else None,
        "units": None,
        "projection_method": None,
        "parameters": {},
    }

    try:
        axis = crs.axis_info[0] if crs.axis_info else None
        result["units"] = axis.unit_name if axis is not None else None
    except Exception:
        pass

    if is_projected and crs.coordinate_operation is not None:
        op = crs.coordinate_operation
        result["projection_method"] = op.method_name
        result["parameters"] = {p.name: p.value for p in op.params}

    return result


def build_crs_metadata(
    source_crs: Any,
    target_crs: Any | None = None,
) -> CRSMetadata:
    """
    Build a CRSMetadata record from real pyproj CRS descriptions.

    Never fabricates projection parameters: any field pyproj does not
    report for the given CRS (e.g. no standard_parallel for a CRS that
    doesn't use one) is left as None.
    """
    src = describe_crs(source_crs)
    meta = CRSMetadata(
        source_crs=_crs_label(source_crs, src),
        target_crs=None,
        datum=src.get("datum"),
        ellipsoid=src.get("ellipsoid"),
        units=src.get("units"),
        projection_method=src.get("projection_method"),
    )
    _apply_projection_parameters(meta, src.get("parameters", {}))

    if target_crs is not None:
        tgt = describe_crs(target_crs)
        meta.target_crs = _crs_label(target_crs, tgt)
        # A reprojection's own method/datum/ellipsoid/units/parameters
        # describe the *target* CRS (what the data now lives in), not
        # the source.
        meta.projection_method = tgt.get("projection_method")
        meta.datum = tgt.get("datum")
        meta.ellipsoid = tgt.get("ellipsoid")
        meta.units = tgt.get("units")
        _apply_projection_parameters(meta, tgt.get("parameters", {}))

    return meta


def _crs_label(raw_input: Any, described: dict[str, Any]) -> str:
    """Prefer a real EPSG code; fall back to the CRS name; never fabricate one."""
    epsg = described.get("epsg")
    if epsg:
        return f"EPSG:{epsg}"
    if described.get("name"):
        return str(described["name"])
    return str(raw_input)


# PROJ parameter names -> CRSMetadata field, as reported by
# pyproj's CoordinateOperation.params for common conformal/equal-area
# projection methods (Transverse Mercator, LCC 1SP/2SP, Albers).
_PARAM_FIELD_MAP = {
    "Central meridian": "central_meridian",
    "Longitude of natural origin": "central_meridian",
    "Longitude of false origin": "central_meridian",
    "Latitude of natural origin": "latitude_of_origin",
    "Latitude of false origin": "latitude_of_origin",
    "Latitude of 1st standard parallel": "standard_parallel_1",
    "Latitude of 2nd standard parallel": "standard_parallel_2",
    "Scale factor at natural origin": "scale_factor",
    "False easting": "false_easting",
    "Easting at false origin": "false_easting",
    "False northing": "false_northing",
    "Northing at false origin": "false_northing",
}


def _apply_projection_parameters(meta: CRSMetadata, parameters: dict[str, Any]) -> None:
    for proj_name, value in parameters.items():
        field_name = _PARAM_FIELD_MAP.get(proj_name)
        if field_name is not None:
            setattr(meta, field_name, value)
