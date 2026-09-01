"""
Atmospheric Complexity Framework (ACF)

Geospatial CRS/Projection Module Test Suite (MISSION: intégration du
module Systèmes de Coordonnées et Projections Cartographiques)

Covers the 7 test scenarios required by the mission (section 20):
1. EPSG:4326 -> UTM
2. EPSG:4326 -> LCC
3. EPSG:4326 -> Albers
4. Reversibility: WGS84 -> projected -> WGS84 (documented tolerance)
5. Metric distance in a projected CRS returns meters, not degrees
6. Area computation uses an appropriate (equal-area) projection
7. A multi-UTM-zone extent is not silently forced into one zone

Plus coverage of CRS detection/validation, the Algeria region logic,
the decision matrix, and non-mutation of the original Dataset on
reprojection.
"""

import numpy as np
import pyproj
import pytest

from acf.data.dataset import Dataset
from acf.geospatial import crs_manager, distortion, metadata, projections, reprojection
from acf.science.registry import ScientificRegistry

# Northern Algeria-ish bounding box, single UTM zone (31N).
NORTH_ALGERIA_SINGLE_ZONE = (2.0, 34.0, 5.0, 37.0)
# Spans zones 29-32 (well outside a single UTM zone).
NORTH_ALGERIA_MULTI_ZONE = (-3.0, 34.0, 8.0, 37.0)


# ---------------------------------------------------------------------------
# CRS detection
# ---------------------------------------------------------------------------


def test_detect_crs_from_grid_mapping_name():
    result = crs_manager.detect_crs({"grid_mapping_name": "latitude_longitude"})
    assert result["status"] == "OK"
    assert result["detected"] == "EPSG:4326"
    assert result["description"]["is_geographic"] is True


def test_detect_crs_does_not_invent_an_ambiguous_projected_crs():
    """A 'Projected' hint with no real CRS attached must not be guessed (mission rule #13)."""

    class FakeDataset:
        metadata = {}
        dimensions = ["x", "y"]

    result = crs_manager.detect_crs(FakeDataset())
    assert result["status"] == "AMBIGUOUS"
    assert result["detected"] is None


def test_detect_crs_family_label_is_not_silently_resolved_by_pyproj():
    """
    Regression guard: pyproj.CRS.from_user_input("latlon") resolves to
    an unrelated real geodetic frame (IGS20/EPSG:10178), not a generic
    WGS84 equivalent - a family-only label like "lambert" must never
    be forwarded to pyproj directly.
    """
    result = crs_manager.detect_crs({"grid_mapping_name": "lambert_conformal_conic"})
    assert result["status"] == "PARTIAL"
    assert result["detected"] == "lambert"
    assert result["description"] is None


def test_describe_crs_distinguishes_geographic_from_projected():
    """Mission section 15: EPSG:4326 is a geographic CRS, never a 'projection'."""
    wgs84 = metadata.describe_crs("EPSG:4326")
    assert wgs84["is_geographic"] is True
    assert wgs84["is_projected"] is False
    assert wgs84["projection_method"] is None

    utm31n = metadata.describe_crs("EPSG:32631")
    assert utm31n["is_geographic"] is False
    assert utm31n["is_projected"] is True
    assert utm31n["projection_method"] is not None


def test_describe_crs_invalid_input_reports_error_not_a_guess():
    result = metadata.describe_crs("NOT_A_REAL_CRS_STRING")
    assert result["status"] == "INVALID_CRS"


# ---------------------------------------------------------------------------
# UTM zone selection (mission section 5)
# ---------------------------------------------------------------------------


def test_utm_zone_number_formula():
    # zone = int((longitude + 180) / 6) + 1
    assert projections.utm_zone_number(3.0) == 31
    assert projections.utm_zone_number(-1.0) == 30
    assert projections.utm_zone_number(7.0) == 32


def test_determine_utm_zone_single_zone():
    result = projections.determine_utm_zone(NORTH_ALGERIA_SINGLE_ZONE)
    assert result["status"] == "OK"
    assert result["zone"] == 31
    assert result["hemisphere"] == "N"
    assert result["epsg"] == "EPSG:32631"


def test_determine_utm_zone_multi_zone_is_not_silently_forced():
    """Test scenario 7: a multi-zone extent must not be arbitrarily assigned one zone."""
    result = projections.determine_utm_zone(NORTH_ALGERIA_MULTI_ZONE)
    assert result["status"] == "MULTI_ZONE"
    assert result["recommended_alternative"] == "lcc"
    assert len(result["zones_spanned"]) > 1


# ---------------------------------------------------------------------------
# Algeria region detection & recommendation (mission section 18)
# ---------------------------------------------------------------------------


def test_is_north_algeria():
    assert projections.is_north_algeria(NORTH_ALGERIA_SINGLE_ZONE) is True
    assert projections.is_north_algeria((-10.0, 45.0, -5.0, 50.0)) is False  # e.g. France


def test_recommend_projection_storage_stays_wgs84():
    rec = projections.recommend_projection(None, "storage")
    assert rec.recommended == "wgs84"
    assert rec.crs == "EPSG:4326"


def test_recommend_projection_distance_over_algeria_gives_utm():
    """Test scenario 1: EPSG:4326 -> UTM recommendation."""
    rec = projections.recommend_projection(NORTH_ALGERIA_SINGLE_ZONE, "distance")
    assert rec.recommended == "utm"
    assert rec.crs == "EPSG:32631"
    assert any("Algeria" in w for w in rec.warnings)


def test_recommend_projection_meteorological_fields_gives_lcc():
    """Test scenario 2: EPSG:4326 -> LCC recommendation."""
    rec = projections.recommend_projection(NORTH_ALGERIA_SINGLE_ZONE, "cape_cin")
    assert rec.recommended == "lcc"


def test_recommend_projection_area_gives_albers():
    """Test scenario 3: EPSG:4326 -> Albers recommendation."""
    rec = projections.recommend_projection(NORTH_ALGERIA_SINGLE_ZONE, "area")
    assert rec.recommended == "albers"


def test_recommend_projection_multi_zone_distance_falls_back_to_lcc():
    rec = projections.recommend_projection(NORTH_ALGERIA_MULTI_ZONE, "distance")
    assert rec.recommended == "lcc"
    assert any("multiple UTM zones" in w or "zones" in w for w in rec.warnings)


def test_recommend_projection_web_mapping_warns_against_scientific_use():
    rec = projections.recommend_projection(None, "web_mapping")
    assert rec.crs == "EPSG:3857"
    assert any("DISPLAY ONLY" in w for w in rec.warnings)


def test_recommend_projection_unknown_analysis_type():
    rec = projections.recommend_projection(None, "not_a_real_analysis_type")
    assert rec.recommended == "UNKNOWN"


# ---------------------------------------------------------------------------
# CRS validation (mission section 12)
# ---------------------------------------------------------------------------


def test_validate_crs_passes_for_valid_transformation():
    result = crs_manager.validate_crs("EPSG:4326", "EPSG:32631", NORTH_ALGERIA_SINGLE_ZONE)
    assert result["status"] == "PASSED"
    assert result["errors"] == []


def test_validate_crs_fails_for_invalid_bounds():
    bad_bounds = (2.0, 34.0, -5.0, 37.0)  # min_lon > max_lon
    result = crs_manager.validate_crs("EPSG:4326", "EPSG:32631", bad_bounds)
    assert result["status"] == "FAILED"
    assert any("Invalid bounding box" in e for e in result["errors"])


def test_validate_crs_fails_for_out_of_range_latitude():
    result = crs_manager.validate_crs("EPSG:4326", bounds=(0.0, -95.0, 1.0, 1.0))
    assert result["status"] == "FAILED"
    assert any("Latitude out of" in e for e in result["errors"])


def test_validate_crs_fails_for_unparseable_source():
    result = crs_manager.validate_crs("TOTALLY_NOT_A_CRS")
    assert result["status"] == "FAILED"
    assert result["checks"]["source_crs_defined"] is False


# ---------------------------------------------------------------------------
# Reprojection (mission sections 9-11, 20)
# ---------------------------------------------------------------------------


def test_reproject_points_wgs84_to_utm():
    """Test scenario 1 (continued): actual coordinate transform EPSG:4326 -> UTM 31N."""
    lon = np.array([3.0])
    lat = np.array([36.0])
    x, y = reprojection.reproject_points(lon, lat, "EPSG:4326", "EPSG:32631")
    # A point near the zone's central meridian (3E for zone 31) should
    # land close to the 500000m false easting.
    assert abs(x[0] - 500000.0) < 20000.0
    assert y[0] > 0.0


def test_reproject_points_wgs84_to_lcc():
    """Test scenario 2 (continued): actual coordinate transform EPSG:4326 -> LCC."""
    lcc_crs = pyproj.CRS.from_proj4(
        "+proj=lcc +lat_1=32 +lat_2=36 +lat_0=34 +lon_0=3 +x_0=0 +y_0=0 +datum=WGS84 +units=m"
    )
    x, y = reprojection.reproject_points([3.0], [34.0], "EPSG:4326", lcc_crs)
    assert abs(x[0]) < 1.0  # on the central meridian at the origin latitude
    assert abs(y[0]) < 1.0


def test_reproject_points_wgs84_to_albers():
    """Test scenario 3 (continued): actual coordinate transform EPSG:4326 -> Albers."""
    albers_crs = pyproj.CRS.from_proj4(
        "+proj=aea +lat_1=32 +lat_2=36 +lat_0=34 +lon_0=3 +x_0=0 +y_0=0 +datum=WGS84 +units=m"
    )
    x, y = reprojection.reproject_points([5.0], [35.0], "EPSG:4326", albers_crs)
    assert x[0] > 0.0
    assert y[0] > 0.0


def test_round_trip_reversibility():
    """
    Test scenario 4: WGS84 -> UTM -> WGS84 must round-trip within a
    documented tolerance (sub-millimeter for a double-precision
    ellipsoidal transform).
    """
    result = reprojection.round_trip_error([3.0, 4.5], [35.0, 36.2], "EPSG:4326", "EPSG:32631")
    assert result["status"] == "OK"
    assert result["max_error_m"] < 0.001  # documented tolerance: < 1 mm


def test_distance_in_projected_crs_is_metres_not_degrees():
    """Test scenario 5: a distance computed after reprojection is in meters."""
    x, y = reprojection.reproject_points([3.0, 3.0], [34.0, 35.0], "EPSG:4326", "EPSG:32631")
    distance_m = float(np.hypot(x[1] - x[0], y[1] - y[0]))
    # 1 degree of latitude is ~111 km - a raw-degree "distance" of 1.0
    # would be nonsensical; the real metric distance must be near 111 km.
    assert 105_000.0 < distance_m < 115_000.0


def test_reproject_dataset_copy_does_not_mutate_original():
    """Mission rules #9-11: reprojection must happen on a copy, original CRS preserved."""
    ds = Dataset(name="test_ds", filetype="test")
    ds.add_variable("longitude", np.array([3.0, 4.0]))
    ds.add_variable("latitude", np.array([35.0, 36.0]))
    ds.set_metadata("crs", "EPSG:4326")

    original_lon = ds.get_variable("longitude").copy()
    original_lat = ds.get_variable("latitude").copy()

    reprojected = reprojection.reproject_dataset_copy(ds, "EPSG:32631")

    # Original dataset is untouched.
    np.testing.assert_array_equal(ds.get_variable("longitude"), original_lon)
    np.testing.assert_array_equal(ds.get_variable("latitude"), original_lat)
    assert ds.get_metadata("crs") == "EPSG:4326"

    # The copy is genuinely reprojected and remembers the original CRS.
    assert reprojected is not ds
    assert not np.allclose(reprojected.get_variable("longitude"), original_lon)
    assert reprojected.get_metadata("original_crs") == "EPSG:4326"
    assert reprojected.get_metadata("crs")["target_crs"] == "EPSG:32631"


def test_reproject_dataset_copy_requires_recognizable_coordinates():
    ds = Dataset(name="no_coords")
    ds.add_variable("temperature", np.array([1.0, 2.0]))
    with pytest.raises(ValueError):
        reprojection.reproject_dataset_copy(ds, "EPSG:32631")


# ---------------------------------------------------------------------------
# Distortion diagnostics (mission section 11) / area computation (scenario 6)
# ---------------------------------------------------------------------------


def test_distortion_geographic_crs_is_flagged_not_measured():
    report = distortion.assess_distortion("EPSG:4326", NORTH_ALGERIA_SINGLE_ZONE)
    assert report.is_geographic is True
    assert report.distance_distortion_pct is None
    assert report.warning is not None


def test_distortion_utm_is_low_over_a_single_zone():
    report = distortion.assess_distortion("EPSG:32631", NORTH_ALGERIA_SINGLE_ZONE)
    assert report.is_geographic is False
    assert abs(report.distance_distortion_pct) < 1.0  # well under 1% within one UTM zone


def test_area_computation_uses_equal_area_projection_not_web_mercator():
    """
    Test scenario 6: area computed via the recommended equal-area (Albers)
    projection must be dramatically less distorted than the same area
    computed via Web Mercator, which the module explicitly forbids for
    scientific use.
    """
    albers_report = distortion.assess_distortion(
        "+proj=aea +lat_1=32 +lat_2=36 +lat_0=34 +lon_0=3 +datum=WGS84 +units=m",
        NORTH_ALGERIA_SINGLE_ZONE,
    )
    web_mercator_report = distortion.assess_distortion("EPSG:3857", NORTH_ALGERIA_SINGLE_ZONE)

    assert abs(albers_report.area_distortion_pct) < abs(web_mercator_report.area_distortion_pct)
    assert abs(albers_report.area_distortion_pct) < 1.0


def test_distortion_confidently_reports_false_not_just_unknown():
    """
    CORRECTED: is_conformal/is_equal_area used to be built as
    "any(...) or None", which can only ever produce True or None -
    `False or None` evaluates to None - so a CRS whose method name
    confidently matched the OTHER category (e.g. Albers, definitely
    NOT conformal) was reported as is_conformal=None ("unknown")
    instead of the knowable False. See distortion.py.
    """
    albers_report = distortion.assess_distortion(
        "+proj=aea +lat_1=32 +lat_2=36 +lat_0=34 +lon_0=3 +datum=WGS84 +units=m",
        NORTH_ALGERIA_SINGLE_ZONE,
    )
    assert albers_report.is_equal_area is True
    assert albers_report.is_conformal is False  # known NOT conformal, not just "unknown"

    utm_report = distortion.assess_distortion("EPSG:32631", NORTH_ALGERIA_SINGLE_ZONE)
    assert utm_report.is_conformal is True
    assert utm_report.is_equal_area is False  # known NOT equal-area, not just "unknown"


# ---------------------------------------------------------------------------
# Metadata (mission section 13)
# ---------------------------------------------------------------------------


def test_build_crs_metadata_records_lcc_parameters():
    lcc_crs = pyproj.CRS.from_proj4(
        "+proj=lcc +lat_1=32 +lat_2=36 +lat_0=34 +lon_0=3 +x_0=0 +y_0=0 +datum=WGS84 +units=m"
    )
    meta = metadata.build_crs_metadata("EPSG:4326", lcc_crs)
    assert meta.source_crs == "EPSG:4326"
    assert meta.projection_method is not None
    assert "Lambert" in meta.projection_method or "Conic" in meta.projection_method
    assert meta.standard_parallel_1 == pytest.approx(32.0)
    assert meta.standard_parallel_2 == pytest.approx(36.0)
    assert meta.transformation_date is not None


def test_build_crs_metadata_never_fabricates_missing_parameters():
    """A geographic CRS has no false_easting/standard_parallel - must stay None, not 0.0."""
    meta = metadata.build_crs_metadata("EPSG:4326")
    assert meta.false_easting is None
    assert meta.standard_parallel_1 is None


# ---------------------------------------------------------------------------
# Projection catalog & registry integration (mission sections 6-7, 16-17)
# ---------------------------------------------------------------------------


def test_projection_catalog_has_minimum_required_entries():
    names = {entry.name for entry in projections.PROJECTION_CATALOG}
    required = {
        "Plate Carrée", "Mercator", "Web Mercator", "Transverse Mercator", "UTM",
        "Lambert Conformal Conic 2SP", "Albers Equal Area", "Robinson", "Winkel Tripel",
        "Mollweide", "Sinusoidal", "Equal Earth",
    }
    assert required <= names
    assert len(projections.PROJECTION_CATALOG) >= 23


def test_geodesy_laws_registered_in_scientific_registry():
    """LCC 2SP / Albers / UTM formulas must be discoverable via the existing registry."""
    lcc = ScientificRegistry.get("lambert_conformal_conic_2sp")
    assert lcc is not None
    assert "EPSG:9802" in " ".join(lcc.references) or "9802" in " ".join(lcc.references)

    albers = ScientificRegistry.get("albers_equal_area_conic")
    assert albers is not None

    utm = ScientificRegistry.get("utm_zone_selection")
    assert utm.calculate(longitude_deg=3.0) == 31
