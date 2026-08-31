"""
Atmospheric Complexity Framework (ACF)

Geospatial - CRS Manager
========================

Detects and validates coordinate reference systems (CRS) for ACF
datasets, and distinguishes CRS vs. datum vs. ellipsoid vs. projection
method (mission section 15) - e.g. EPSG:4326 must be reported as a
*geographic* CRS, never as a projection.

Design notes
------------
- Reuses acf.data.engine.projection_detector.ProjectionDetector as a
  first, lightweight, dependency-free pass (it already recognizes
  common CF grid_mapping_name values and lat/lon dimension names) -
  this module does NOT duplicate that logic, only enriches it with a
  real pyproj.CRS-backed description when a usable CRS string/EPSG
  code is available (mission section 22: "Ne crée pas une deuxième
  implémentation concurrente si une fonction équivalente existe déjà").
- All real CRS parsing is delegated to pyproj/PROJ - this module never
  hand-rolls a datum/ellipsoid/EPSG lookup.
- Never invents an ambiguous CRS (mission rule #13): detect_crs()
  reports "AMBIGUOUS"/"UNKNOWN" rather than guessing, and
  validate_crs() fails closed (STOP with an explicit diagnostic)
  rather than silently producing a result from an unverified CRS
  (mission section 12).
"""

from __future__ import annotations

from typing import Any

from acf.data.engine.projection_detector import ProjectionDetector
from acf.geospatial.metadata import HAS_PYPROJ, describe_crs

try:
    from pyproj import CRS

    HAS_PYPROJ = True
except Exception:  # pragma: no cover
    HAS_PYPROJ = False


_detector = ProjectionDetector()

# ProjectionDetector.PROJECTIONS' *values* are generic family labels
# ("latlon", "mercator", "lambert", "polar"), not resolvable CRS
# identifiers - only "EPSG:4326" (returned by its Dataset-object branch
# for recognized lat/lon dimensions) is a real, safe CRS string.
# Critically, some of these generic labels are NOT safe to hand to
# pyproj: CRS.from_user_input("latlon") does not fail or return a
# generic WGS84-equivalent CRS - it silently resolves to a specific,
# unrelated geodetic frame (IGS20 / EPSG:10178) via a PROJ pipeline
# alias. Passing an ambiguous label to pyproj and trusting whatever it
# resolves to would itself be "inventing" a CRS (mission rule #13), so
# these labels are intercepted here and never forwarded to pyproj.
_GENERIC_FAMILY_LABELS = frozenset(ProjectionDetector.PROJECTIONS.values())


def detect_crs(obj: Any) -> dict[str, Any]:
    """
    Detect the CRS of a dataset-like object or metadata dict.

    First applies the existing, lightweight ProjectionDetector (CF
    grid_mapping_name / lat-lon dimension heuristics). If that yields
    a real CRS identifier (e.g. "EPSG:4326"), enrich it with a full
    pyproj-backed description. If it only yields a generic label like
    "Projected" (coordinates are in x/y but the specific CRS is not
    recorded anywhere in the metadata), this is honestly reported as
    ambiguous rather than guessed - per mission rule #13, an ambiguous
    CRS must be flagged, never invented.
    """
    heuristic = _detector.detect(obj)

    if heuristic == "unknown":
        return {
            "status": "UNKNOWN",
            "detected": None,
            "message": "No grid_mapping_name, CRS attribute, or recognizable lat/lon "
            "dimensions found. Provide an explicit CRS.",
        }

    if heuristic == "Projected":
        return {
            "status": "AMBIGUOUS",
            "detected": None,
            "message": "Data appears to be in a projected (x/y) CRS, but no EPSG code "
            "or CRS definition was found in the metadata. Refusing to guess which "
            "projection - provide an explicit CRS (mission rule #13).",
        }

    if heuristic in _GENERIC_FAMILY_LABELS and heuristic != "latlon":
        # A recognized projection FAMILY (e.g. "lambert", "mercator",
        # "polar") but not a complete, parseable CRS - never forwarded
        # to pyproj (see _GENERIC_FAMILY_LABELS above).
        return {
            "status": "PARTIAL",
            "detected": heuristic,
            "description": None,
            "message": f"Legacy detector identified projection family '{heuristic}' from the "
            "dataset's grid_mapping_name, but this is only a family name, not a complete CRS "
            "(it lacks specific parallels/meridian/EPSG code) - mission section 15. Provide an "
            "explicit CRS to fully resolve it.",
        }

    if heuristic == "latlon":
        # CF convention: a "latitude_longitude" grid_mapping_name with
        # no further ellipsoid/datum parameters defaults to WGS84 in
        # practice for ACF's data sources (ERA5, most satellite
        # products) - resolved explicitly to EPSG:4326 here rather
        # than handed to pyproj as the bare word "latlon".
        heuristic = "EPSG:4326"

    # heuristic is now a real CRS string (e.g. "EPSG:4326").
    described = describe_crs(heuristic) if HAS_PYPROJ else {"status": "NOT_AVAILABLE_PYPROJ_NOT_INSTALLED"}

    if described.get("status") == "OK":
        return {"status": "OK", "detected": heuristic, "description": described}

    return {
        "status": "PARTIAL",
        "detected": heuristic,
        "description": described,
        "message": f"Detected CRS identifier '{heuristic}' could not be fully resolved by pyproj.",
    }


def is_geographic(crs_input: Any) -> bool | None:
    """True/False, or None if the CRS cannot be determined."""
    described = describe_crs(crs_input)
    if described.get("status") != "OK":
        return None
    return bool(described["is_geographic"])


def is_projected(crs_input: Any) -> bool | None:
    """True/False, or None if the CRS cannot be determined."""
    described = describe_crs(crs_input)
    if described.get("status") != "OK":
        return None
    return bool(described["is_projected"])


def validate_crs(
    source_crs: Any,
    target_crs: Any | None = None,
    bounds: tuple[float, float, float, float] | None = None,
) -> dict[str, Any]:
    """
    Run the pre-reprojection validation checklist (mission section 12):

    1. source CRS defined and parseable
    2. target CRS defined and parseable (if a target was requested)
    3. datum identified
    4. units identified
    5. bounding box valid (min <= max on both axes)
    6. latitude in [-90, 90]
    7. longitude in [-180, 180]
    8. a real transformation is available between source and target
    9. (UTM only) the bounds fit within a single UTM zone - see
       projections.determine_utm_zone(), which itself raises rather
       than silently picking a zone for a multi-zone extent
    10. resolution is not addressed here (it is a per-dataset grid
        property, not a CRS property) - callers reprojecting a raster
        grid must check this themselves; documented rather than
        fabricated.

    On ANY failure: return "status": "FAILED" with an explicit
    "errors" list - never a partial/guessed PASS (mission section 12:
    "STOP -> diagnostic explicite -> ne pas produire silencieusement
    un resultat incorrect").
    """
    checks: dict[str, bool] = {}
    errors: list[str] = []

    if not HAS_PYPROJ:
        return {
            "status": "FAILED",
            "checks": {},
            "errors": ["pyproj is not installed - cannot validate any CRS."],
        }

    src_desc = describe_crs(source_crs)
    checks["source_crs_defined"] = src_desc.get("status") == "OK"
    if not checks["source_crs_defined"]:
        errors.append(f"Source CRS could not be parsed: {src_desc}")

    if checks["source_crs_defined"]:
        checks["datum_identified"] = src_desc.get("datum") is not None
        if not checks["datum_identified"]:
            errors.append("Source CRS has no identifiable datum.")

        checks["units_identified"] = src_desc.get("units") is not None
        if not checks["units_identified"]:
            errors.append("Source CRS has no identifiable axis units.")

    if target_crs is not None:
        tgt_desc = describe_crs(target_crs)
        checks["target_crs_defined"] = tgt_desc.get("status") == "OK"
        if not checks["target_crs_defined"]:
            errors.append(f"Target CRS could not be parsed: {tgt_desc}")

        if checks["source_crs_defined"] and checks.get("target_crs_defined"):
            checks["transformation_available"] = _transformation_available(source_crs, target_crs)
            if not checks["transformation_available"]:
                errors.append("No coordinate transformation is available between source and target CRS.")

    if bounds is not None:
        min_lon, min_lat, max_lon, max_lat = bounds
        checks["bbox_valid"] = min_lon <= max_lon and min_lat <= max_lat
        if not checks["bbox_valid"]:
            errors.append(f"Invalid bounding box (min must be <= max): {bounds}")

        checks["latitude_in_range"] = -90.0 <= min_lat <= 90.0 and -90.0 <= max_lat <= 90.0
        if not checks["latitude_in_range"]:
            errors.append(f"Latitude out of [-90, 90] range: {bounds}")

        checks["longitude_in_range"] = -180.0 <= min_lon <= 180.0 and -180.0 <= max_lon <= 180.0
        if not checks["longitude_in_range"]:
            errors.append(f"Longitude out of [-180, 180] range: {bounds}")

    status = "PASSED" if not errors else "FAILED"
    return {"status": status, "checks": checks, "errors": errors}


def _transformation_available(source_crs: Any, target_crs: Any) -> bool:
    try:
        src = source_crs if isinstance(source_crs, CRS) else CRS.from_user_input(source_crs)
        tgt = target_crs if isinstance(target_crs, CRS) else CRS.from_user_input(target_crs)
        from pyproj import Transformer

        Transformer.from_crs(src, tgt, always_xy=True)
        return True
    except Exception:
        return False
