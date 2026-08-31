"""
Atmospheric Complexity Framework (ACF)

Geospatial - Projections
=========================

Projection configuration, automatic projection recommendation, the
ACF decision matrix (mission section 10), and region-specific logic
for Northern Algeria (mission section 18).

This module recommends *which* CRS to use for a given analysis; it
never performs the actual reprojection (see reprojection.py) and never
hand-rolls projection math (see science/laws/geodesy.py for the
documented formulas, and reprojection.py for the pyproj-backed
transforms).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Section 8: projection configuration table
# ---------------------------------------------------------------------------

PROJECTION_CONFIG: dict[str, dict[str, Any]] = {
    "wgs84": {
        "crs": "EPSG:4326",
        "type": "geographic",
        "unit": "degree",
        "preserves": None,
        "description": "WGS 84 geographic CRS - NOT a planar projection. Storage/exchange CRS "
        "for ERA5, most satellite products, and ACF's original data.",
    },
    "utm": {
        "type": "transverse_mercator",
        "datum": "WGS84",
        "scale_factor": 0.9996,
        "zone_width_deg": 6,
        "unit": "meter",
        "description": "WGS84 / UTM, zone auto-selected from the data's central longitude. "
        "Only valid when the study area fits within a single zone.",
    },
    "lcc": {
        "type": "lambert_conformal_conic",
        "method": "2SP",
        "epsg_method": "EPSG:9802",
        "preserves": "angles",
        "description": "Lambert Conformal Conic (2 standard parallels) - regional meteorological "
        "mapping over mid-latitude east-west-elongated domains (e.g. Northern Algeria).",
    },
    "albers": {
        "type": "albers_equal_area",
        "epsg_method": "EPSG:9822",
        "preserves": "areas",
        "description": "Albers Equal Area Conic - use whenever surface-area comparisons matter.",
    },
    "webmercator": {
        "crs": "EPSG:3857",
        "type": "web_mercator",
        "preserves": None,
        "unit": "meter",
        "description": "Web/Pseudo-Mercator - web-map basemap display ONLY. Never use for "
        "scientific distance or area calculations (severe area distortion at mid/high latitude).",
    },
}


# ---------------------------------------------------------------------------
# Section 5: UTM zone selection
# ---------------------------------------------------------------------------

# WGS84 UTM EPSG codes follow the pattern 326XX (North) / 327XX (South).
_UTM_EPSG_NORTH_BASE = 32600
_UTM_EPSG_SOUTH_BASE = 32700

# UTM zones relevant to Algeria (mission section 5), for quick reference/
# validation - not an exhaustive global table.
ALGERIA_UTM_ZONES: dict[str, str] = {
    "29N": "EPSG:32629",
    "30N": "EPSG:32630",
    "31N": "EPSG:32631",
    "32N": "EPSG:32632",
}


def utm_zone_number(longitude: float) -> int:
    """
    Standard UTM zone number for a given longitude.

    zone = int((longitude + 180) / 6) + 1   (mission section 5)
    """
    if not -180.0 <= longitude <= 180.0:
        raise ValueError(f"Longitude out of range: {longitude}")
    return int((longitude + 180.0) / 6.0) + 1


def utm_epsg_code(longitude: float, latitude: float) -> str:
    """Return the WGS84/UTM EPSG code for a single point (zone + hemisphere)."""
    zone = utm_zone_number(longitude)
    base = _UTM_EPSG_NORTH_BASE if latitude >= 0 else _UTM_EPSG_SOUTH_BASE
    return f"EPSG:{base + zone}"


def determine_utm_zone(bounds: tuple[float, float, float, float]) -> dict[str, Any]:
    """
    Determine the UTM zone for a bounding box (min_lon, min_lat, max_lon, max_lat).

    Mission rule: "Si la zone d'étude traverse plusieurs zones UTM, ne
    pas choisir arbitrairement une seule zone. Signaler le problème et
    proposer LCC ou une autre projection régionale." - if the bounds
    span more than one zone, this returns status="MULTI_ZONE" with a
    recommendation to use LCC instead, rather than silently picking
    one zone.
    """
    min_lon, min_lat, max_lon, max_lat = bounds
    west_zone = utm_zone_number(min_lon)
    east_zone = utm_zone_number(max_lon)

    if west_zone != east_zone:
        return {
            "status": "MULTI_ZONE",
            "zones_spanned": sorted({west_zone, east_zone}),
            "message": f"Bounding box spans UTM zones {west_zone} to {east_zone} - a single UTM "
            "zone would distort data near the zone boundary. Use Lambert Conformal Conic "
            "('lcc') or another regional projection instead.",
            "recommended_alternative": "lcc",
        }

    central_lat = (min_lat + max_lat) / 2.0
    epsg = utm_epsg_code((min_lon + max_lon) / 2.0, central_lat)
    hemisphere = "N" if central_lat >= 0 else "S"
    return {
        "status": "OK",
        "zone": west_zone,
        "hemisphere": hemisphere,
        "epsg": epsg,
        "label": f"{west_zone}{hemisphere}",
    }


# ---------------------------------------------------------------------------
# Section 18: Northern Algeria region logic
# ---------------------------------------------------------------------------

NORTH_ALGERIA_BOUNDS = {
    "min_lat": 30.0,
    "max_lat": 38.0,
    "min_lon": -3.0,
    "max_lon": 10.0,
}


def is_north_algeria(bounds: tuple[float, float, float, float]) -> bool:
    """
    True if the bounding box (min_lon, min_lat, max_lon, max_lat) falls
    approximately within Northern Algeria (30N-38N, -3E-10E), per
    mission section 18. Uses a simple containment test against the
    documented reference box - not a political-boundary lookup.
    """
    min_lon, min_lat, max_lon, max_lat = bounds
    b = NORTH_ALGERIA_BOUNDS
    return min_lat >= b["min_lat"] and max_lat <= b["max_lat"] and min_lon >= b["min_lon"] and max_lon <= b["max_lon"]


# ---------------------------------------------------------------------------
# Section 10: decision matrix
# ---------------------------------------------------------------------------

DECISION_MATRIX: dict[str, str] = {
    "storage": "wgs84",
    "era5_original": "wgs84",
    "gpm_original": "native",
    "cape_cin": "lcc",
    "meteorological_fields": "lcc",
    "regional_climatology_maps": "lcc",
    "idw": "utm",
    "kriging": "utm",
    "distance": "utm",
    "buffer": "utm",
    "area": "albers",
    "area_comparison": "albers",
    "world_mapping": "adapted",
    "web_mapping": "webmercator",
}


@dataclass
class ProjectionRecommendation:
    """Result of recommend_projection(): the recommended CRS plus its justification."""

    recommended: str
    crs: str | None
    reason: str
    analysis_type: str
    warnings: list[str]


# analysis_type aliases -> DECISION_MATRIX key, so callers can spell the
# same concept a few natural ways without silently guessing anything.
_ANALYSIS_TYPE_ALIASES: dict[str, str] = {
    "storage": "storage",
    "era5": "era5_original",
    "era5_original": "era5_original",
    "gpm": "gpm_original",
    "gpm_original": "gpm_original",
    "cape": "cape_cin",
    "cin": "cape_cin",
    "cape_cin": "cape_cin",
    "meteorological_fields": "meteorological_fields",
    "climatology": "regional_climatology_maps",
    "regional_climatology_maps": "regional_climatology_maps",
    "idw": "idw",
    "interpolation": "idw",
    "kriging": "kriging",
    "distance": "distance",
    "buffer": "buffer",
    "area": "area",
    "surface": "area",
    "area_comparison": "area_comparison",
    "world_mapping": "world_mapping",
    "web_mapping": "web_mapping",
    "web": "web_mapping",
}


def recommend_projection(
    bounds: tuple[float, float, float, float] | None,
    analysis_type: str,
    data_crs: Any = "EPSG:4326",
    region: str | None = None,
) -> ProjectionRecommendation:
    """
    Recommend a CRS for a given analysis (mission section 9).

    Parameters
    ----------
    bounds : (min_lon, min_lat, max_lon, max_lat) or None
        Required for analyses whose recommendation depends on spatial
        extent (utm, and detecting the Northern Algeria case).
    analysis_type : str
        One of the DECISION_MATRIX keys/aliases above (e.g. "distance",
        "cape_cin", "area", "storage", "web_mapping"...).
    data_crs : Any
        The CRS the data is currently in (defaults to WGS84, ACF's
        standard storage CRS).
    region : str, optional
        Explicit region hint ("north_algeria"). If not given, the
        region is auto-detected from `bounds` when possible - this
        never overrides an explicit CRS choice by the caller, it only
        informs the recommendation.
    """
    warnings: list[str] = []
    key = _ANALYSIS_TYPE_ALIASES.get(analysis_type.strip().lower())
    if key is None:
        return ProjectionRecommendation(
            recommended="UNKNOWN",
            crs=None,
            reason=f"Unrecognized analysis_type '{analysis_type}'. Known types: "
            f"{sorted(set(_ANALYSIS_TYPE_ALIASES.values()))}",
            analysis_type=analysis_type,
            warnings=warnings,
        )

    recommended = DECISION_MATRIX[key]

    region_detected = region == "north_algeria"
    if region is None and bounds is not None and is_north_algeria(bounds):
        region_detected = True
        warnings.append("Bounding box detected as Northern Algeria (mission section 18).")

    if recommended == "wgs84":
        return ProjectionRecommendation(
            recommended="wgs84",
            crs="EPSG:4326",
            reason="Original/storage data must remain in its native geographic CRS "
            "(never silently reprojected in place - mission rules #9-11).",
            analysis_type=analysis_type,
            warnings=warnings,
        )

    if recommended == "native":
        return ProjectionRecommendation(
            recommended="native",
            crs=None,
            reason="This product (e.g. GPM) should be kept in its own native CRS as delivered; "
            "ACF does not force a specific CRS here.",
            analysis_type=analysis_type,
            warnings=warnings,
        )

    if recommended == "utm":
        if bounds is None:
            warnings.append("No bounds provided - cannot select a UTM zone without them.")
            return ProjectionRecommendation(
                recommended="utm",
                crs=None,
                reason="UTM is appropriate for metric distance/interpolation, but bounds are "
                "required to select a compatible zone.",
                analysis_type=analysis_type,
                warnings=warnings,
            )
        zone_info = determine_utm_zone(bounds)
        if zone_info["status"] == "MULTI_ZONE":
            warnings.append(zone_info["message"])
            return ProjectionRecommendation(
                recommended="lcc",
                crs=None,
                reason="Requested extent spans multiple UTM zones; falling back to Lambert "
                "Conformal Conic per mission rule (never pick one UTM zone arbitrarily).",
                analysis_type=analysis_type,
                warnings=warnings,
            )
        return ProjectionRecommendation(
            recommended="utm",
            crs=zone_info["epsg"],
            reason=f"Metric distance/interpolation requires a projected CRS; the extent fits "
            f"entirely within UTM zone {zone_info['label']}.",
            analysis_type=analysis_type,
            warnings=warnings,
        )

    if recommended == "lcc":
        reason = "Conformal (angle-preserving) regional projection appropriate for meteorological "
        "field mapping over a mid-latitude, east-west-elongated domain."
        if region_detected:
            reason += " Northern Algeria falls in this category (mission section 18)."
        return ProjectionRecommendation(
            recommended="lcc", crs=None, reason=reason, analysis_type=analysis_type, warnings=warnings
        )

    if recommended in ("albers", "area_comparison"):
        return ProjectionRecommendation(
            recommended="albers",
            crs=None,
            reason="Equal-area projection required: computing or comparing surface areas on "
            "unprojected lat/lon degrees, or on a conformal/web-Mercator CRS, is scientifically "
            "invalid (mission section: avoid degree-based area/distance errors).",
            analysis_type=analysis_type,
            warnings=warnings,
        )

    if recommended == "webmercator":
        warnings.append(
            "EPSG:3857 is for web-map DISPLAY ONLY - never use it for scientific distance/area "
            "calculations (mission section 9)."
        )
        return ProjectionRecommendation(
            recommended="webmercator",
            crs="EPSG:3857",
            reason="Web-map basemap display.",
            analysis_type=analysis_type,
            warnings=warnings,
        )

    if recommended == "adapted":
        return ProjectionRecommendation(
            recommended="adapted",
            crs=None,
            reason="World-scale mapping needs a projection chosen for the specific display "
            "purpose (e.g. Robinson, Winkel Tripel, Equal Earth) - see the projection catalog "
            "in this module's documentation.",
            analysis_type=analysis_type,
            warnings=warnings,
        )

    # Should be unreachable given DECISION_MATRIX's own values, but
    # fail closed rather than silently returning something wrong.
    return ProjectionRecommendation(
        recommended="UNKNOWN",
        crs=None,
        reason=f"Decision matrix entry '{recommended}' has no handler.",
        analysis_type=analysis_type,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Section 16-17: projection family documentation catalog
# ---------------------------------------------------------------------------


@dataclass
class ProjectionCatalogEntry:
    """One documented entry in the projection reference catalog (mission section 17)."""

    name: str
    family: str
    geometry: str
    property_preserved: str
    main_parameters: str
    distortion_behavior: str
    typical_use: str
    epsg_method: str | None
    common_crs: str | None
    acf_relevance: str


PROJECTION_CATALOG: list[ProjectionCatalogEntry] = [
    ProjectionCatalogEntry(
        "Plate Carrée", "Equidistant/Cylindrical", "Cylindrical", "None (raw lat/lon grid)",
        "None", "Severe area/shape distortion away from the equator",
        "Native storage grid for most NWP/reanalysis data", None, "EPSG:4326",
        "ACF's default storage/exchange CRS (not a real projection).",
    ),
    ProjectionCatalogEntry(
        "Mercator", "Conformal/Cylindrical", "Cylindrical", "Angles/shape",
        "Standard parallel", "Extreme area inflation at high latitude",
        "Navigation charts", "EPSG:9804", None,
        "Rarely appropriate for ACF's mid/high-latitude domains.",
    ),
    ProjectionCatalogEntry(
        "Web Mercator", "Conformal/Cylindrical (spherical)", "Cylindrical", "Angles/shape (approx.)",
        "None (spherical Earth assumption)", "Same as Mercator, plus a spherical-Earth approximation error",
        "Web basemaps (Leaflet, Google/Bing/OSM tiles)", "EPSG:3785 (deprecated)/EPSG:3857",
        "EPSG:3857", "Display-only in ACF's web/GUI layers - never for scientific calculations.",
    ),
    ProjectionCatalogEntry(
        "Transverse Mercator", "Conformal/Cylindrical", "Cylindrical (transverse axis)", "Angles/shape",
        "Central meridian, scale factor", "Distortion grows away from the central meridian",
        "Base projection underlying UTM", "EPSG:9807", None,
        "Underlies every UTM zone ACF uses for metric distance calculations.",
    ),
    ProjectionCatalogEntry(
        "UTM", "Conformal/Cylindrical (zoned Transverse Mercator)", "Cylindrical, 6-degree zones",
        "Angles/shape locally", "Zone, k0=0.9996, false easting 500000m",
        "Low within a zone; grows fast beyond +/-3 degrees from the central meridian",
        "Metric distance, interpolation (IDW/Kriging), buffering", "EPSG:9807",
        "EPSG:326xx (N) / 327xx (S)", "ACF's default for local metric analysis in Northern Algeria (zones 29N-32N).",
    ),
    ProjectionCatalogEntry(
        "Lambert Conformal Conic 1SP", "Conformal/Conic", "Conic (one standard parallel)", "Angles/shape",
        "Latitude of origin, scale factor", "Low near the standard parallel, grows away from it",
        "Regional mapping with a single reference parallel", "EPSG:9801", None,
        "Alternative to 2SP when only one standard parallel is specified.",
    ),
    ProjectionCatalogEntry(
        "Lambert Conformal Conic 2SP", "Conformal/Conic", "Conic (two standard parallels)", "Angles/shape",
        "Two standard parallels, central meridian, latitude of origin", "Low between the two parallels",
        "ACF regional meteorological mapping (CAPE/CIN fields, climatology maps)", "EPSG:9802", None,
        "ACF's recommended projection for meteorological field maps over Northern Algeria.",
    ),
    ProjectionCatalogEntry(
        "Albers Equal Area", "Equal-area/Conic", "Conic (two standard parallels)", "Area",
        "Two standard parallels, central meridian", "Shape distortion grows away from the standard parallels",
        "Surface-area computation and comparison, land-cover statistics", "EPSG:9822", None,
        "ACF's recommended projection whenever surface areas must be computed or compared.",
    ),
    ProjectionCatalogEntry(
        "Lambert Azimuthal Equal Area", "Equal-area/Azimuthal", "Azimuthal", "Area",
        "Center longitude/latitude", "Shape distortion grows with distance from the center point",
        "Polar or regional equal-area analysis centered on a point", "EPSG:9820", None,
        "Alternative to Albers for polar/point-centered equal-area needs.",
    ),
    ProjectionCatalogEntry(
        "Azimuthal Equidistant", "Equidistant/Azimuthal", "Azimuthal", "Distance from center point",
        "Center longitude/latitude", "True distances only from the center point",
        "Radar/observatory range rings, great-circle distance-from-a-point maps", "EPSG:1028", None,
        "Useful for radar/aviation range-ring visualizations.",
    ),
    ProjectionCatalogEntry(
        "Stereographic", "Conformal/Azimuthal", "Azimuthal", "Angles/shape",
        "Center point, scale factor", "Grows with distance from the center point",
        "Polar/regional conformal mapping", "EPSG:9809/EPSG:9810", None,
        "Basis for Polar Stereographic products.",
    ),
    ProjectionCatalogEntry(
        "Polar Stereographic", "Conformal/Azimuthal", "Azimuthal (polar aspect)", "Angles/shape",
        "Standard parallel or scale factor at pole", "Low near the pole, grows toward the equator",
        "Polar meteorology/sea-ice products", "EPSG:9810", "EPSG:3413 (Arctic)/EPSG:3031 (Antarctic)",
        "Used by ACF's space-weather/cryosphere subsystems for polar products.",
    ),
    ProjectionCatalogEntry(
        "Orthographic", "Perspective/Azimuthal", "Azimuthal", "None (true perspective view)",
        "Center point", "Severe distortion approaching the visible hemisphere's edge",
        "3D-globe-style visualization", None, None,
        "Used by ACF's GUI 'photorealistic globe' view mode.",
    ),
    ProjectionCatalogEntry(
        "Gnomonic", "Azimuthal", "Azimuthal", "Great circles as straight lines",
        "Center point", "Extreme distortion away from the center; cannot show a full hemisphere",
        "Great-circle route planning", None, None,
        "Not currently used operationally in ACF.",
    ),
    ProjectionCatalogEntry(
        "Robinson", "Compromise/Pseudocylindrical", "Pseudocylindrical", "None (balanced compromise)",
        "None", "Moderate area and shape distortion, both minimized rather than eliminated",
        "World thematic/general-reference maps", None, None,
        "Available as an ACF GUI world-map view mode.",
    ),
    ProjectionCatalogEntry(
        "Winkel Tripel", "Compromise/Pseudoazimuthal", "Pseudoazimuthal (averaged)", "None (balanced compromise)",
        "Standard parallel", "Low overall distortion of area, direction, and distance combined",
        "World reference maps (National Geographic standard)", None, None,
        "Candidate world-map projection; not yet wired into ACF's GUI registry.",
    ),
    ProjectionCatalogEntry(
        "Mollweide", "Equal-area/Pseudocylindrical", "Pseudocylindrical (elliptical)", "Area",
        "None", "Shape distortion grows toward the map edges",
        "World thematic equal-area maps", "EPSG:53009 (ESRI)", None,
        "Candidate for global equal-area climatology summaries.",
    ),
    ProjectionCatalogEntry(
        "Sinusoidal", "Equal-area/Pseudocylindrical", "Pseudocylindrical", "Area",
        "Central meridian", "Shape distortion grows toward the map edges/high latitude",
        "MODIS-grid remote-sensing products", "EPSG:53008 (ESRI)", "EPSG:53008 (ESRI)/54008 (ESRI)",
        "Relevant if ACF ever ingests MODIS-native-grid remote sensing products.",
    ),
    ProjectionCatalogEntry(
        "Eckert IV", "Equal-area/Pseudocylindrical", "Pseudocylindrical", "Area",
        "None", "Moderate shape distortion, lower than Sinusoidal/Mollweide at the poles",
        "World thematic equal-area maps", None, None,
        "Candidate alternative to Mollweide for global equal-area display.",
    ),
    ProjectionCatalogEntry(
        "Bonne", "Equal-area/Pseudoconic", "Pseudoconic", "Area",
        "Standard parallel, central meridian", "Shape distortion grows away from the central meridian",
        "Historical topographic/regional equal-area mapping", "EPSG:9827", None,
        "Not currently used operationally in ACF; documented for completeness.",
    ),
    ProjectionCatalogEntry(
        "Cassini-Soldner", "Equidistant/Cylindrical (transverse)", "Cylindrical (transverse axis)",
        "Distance along the central meridian", "Central meridian",
        "Grows away from the central meridian", "Historical large-scale/cadastral mapping", "EPSG:9806", None,
        "Not currently used operationally in ACF; documented for completeness.",
    ),
    ProjectionCatalogEntry(
        "Equidistant Conic", "Equidistant/Conic", "Conic (two standard parallels)",
        "Distance along meridians", "Two standard parallels, central meridian",
        "Low between standard parallels", "Regional distance-preserving reference maps", "EPSG:9823", None,
        "Alternative to LCC when meridian-distance preservation matters more than conformality.",
    ),
    ProjectionCatalogEntry(
        "Lambert Cylindrical Equal Area", "Equal-area/Cylindrical", "Cylindrical", "Area",
        "Standard parallel", "Severe shape distortion at high latitude",
        "World/regional equal-area statistical maps", "EPSG:9835", None,
        "Simple cylindrical alternative to Albers for equal-area needs at low latitude.",
    ),
    ProjectionCatalogEntry(
        "Equal Earth", "Equal-area/Pseudocylindrical", "Pseudocylindrical", "Area",
        "None", "Low, visually balanced shape distortion (modern Robinson-like alternative)",
        "Modern world thematic equal-area maps", None, "EPSG:8857",
        "Modern recommended alternative to Mollweide/Sinusoidal for world equal-area display.",
    ),
]


def get_projection_catalog() -> list[dict[str, Any]]:
    """Return the projection catalog as plain dicts (for reports/JSON export)."""
    return [entry.__dict__.copy() for entry in PROJECTION_CATALOG]
