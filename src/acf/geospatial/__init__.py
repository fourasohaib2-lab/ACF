"""
Atmospheric Complexity Framework (ACF)

Geospatial - CRS & Projection Manager
=======================================

Coordinate reference system (CRS) detection, validation, projection
recommendation, and safe reprojection for ACF datasets.

This package is an ADDITIVE layer on top of the existing ACF pipeline
(mission section 25: "ACF EXISTANT + CRS/PROJECTION MANAGER", not a
rewrite). Nothing elsewhere in ACF imports from this package by
default, so it is trivially "disable-able" per the mission's own
requirement (section 8: "facilement désactivable") - simply do not
call into it, or flip GEOSPATIAL_ENABLED below and check it in calling
code that wants an explicit opt-out switch.

Recommended entry points
-------------------------
- crs_manager.detect_crs(dataset_or_metadata) -> CRS detection
- crs_manager.validate_crs(source, target, bounds) -> pre-reprojection checks
- projections.recommend_projection(bounds, analysis_type, data_crs) -> recommendation
- reprojection.reproject_dataset_copy(dataset, target_crs) -> safe, copy-based reprojection
- distortion.assess_distortion(crs, bounds) -> distortion diagnostics
- metadata.build_crs_metadata(source, target) -> structured CRS metadata

See docs/ACF_GEOSPATIAL_CRS_PROJECTION_MODULE.md for the full
scientific documentation, decision matrix, and projection catalog.
"""

from __future__ import annotations

import logging
from typing import Any

from acf.geospatial import crs_manager, distortion, metadata, projections, reprojection

# Explicit opt-out switch (mission section 8). Off by default has no
# meaning here since nothing else in ACF calls into this package
# automatically; this flag exists for callers who want a single place
# to gate their own use of the geospatial layer.
GEOSPATIAL_ENABLED = True

logger = logging.getLogger("acf.geospatial")

__all__ = [
    "GEOSPATIAL_ENABLED",
    "crs_manager",
    "projections",
    "reprojection",
    "distortion",
    "metadata",
    "log_crs_decision",
]


def log_crs_decision(
    source_crs: Any,
    analysis_type: str,
    recommendation: "projections.ProjectionRecommendation",
    region: str | None = None,
    validation_status: str | None = None,
) -> None:
    """
    Emit the standardized [ACF-CRS] log block described in mission
    section 21, e.g.:

        [ACF-CRS] Source CRS: EPSG:4326
        [ACF-CRS] Spatial extent: North Algeria
        [ACF-CRS] Analysis type: spatial interpolation
        [ACF-CRS] Recommended CRS: WGS84 / UTM
        [ACF-CRS] Reason: metric distance required
        [ACF-CRS] Reprojection: enabled
        [ACF-CRS] Validation: PASSED
    """
    logger.info("[ACF-CRS] Source CRS: %s", source_crs)
    if region:
        logger.info("[ACF-CRS] Spatial extent: %s", region)
    logger.info("[ACF-CRS] Analysis type: %s", analysis_type)
    logger.info("[ACF-CRS] Recommended CRS: %s", recommendation.recommended)
    logger.info("[ACF-CRS] Reason: %s", recommendation.reason)
    logger.info("[ACF-CRS] Reprojection: %s", "enabled" if GEOSPATIAL_ENABLED else "disabled")
    if validation_status:
        logger.info("[ACF-CRS] Validation: %s", validation_status)
