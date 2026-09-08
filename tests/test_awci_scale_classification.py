"""
Tests for acf.awci.scale_classification - real spatial/temporal scale
classification (docs/ACF_MASTER_PROMPT.md section 43). This session's
exhaustive 90-section conformance audit (reports/ACF_MASTER_AUDIT_v2.md)
found no explicit scale classification attached anywhere in this
codebase, despite the real model grid resolutions
(acf.forecast.engine.MODEL_CONFIGS) implicitly spanning several scales.
"""

from __future__ import annotations

import pytest

from acf.awci.scale_classification import (
    SpatialScale,
    TemporalScale,
    classify_spatial_scale,
    classify_temporal_scale,
)
from acf.forecast.engine import MODEL_CONFIGS


def test_classify_spatial_scale_micro():
    assert classify_spatial_scale(0.5) == SpatialScale.MICRO
    assert classify_spatial_scale(1.9) == SpatialScale.MICRO


def test_classify_spatial_scale_meso():
    assert classify_spatial_scale(2.0) == SpatialScale.MESO
    assert classify_spatial_scale(500.0) == SpatialScale.MESO


def test_classify_spatial_scale_synoptic():
    assert classify_spatial_scale(2000.0) == SpatialScale.SYNOPTIC
    assert classify_spatial_scale(5000.0) == SpatialScale.SYNOPTIC


def test_classify_spatial_scale_rejects_non_positive_resolution():
    with pytest.raises(ValueError, match="positive"):
        classify_spatial_scale(0.0)
    with pytest.raises(ValueError, match="positive"):
        classify_spatial_scale(-1.0)


def test_real_model_configs_resolutions_classify_as_expected():
    """The 3 real, already-used model grid resolutions
    (acf.forecast.engine.MODEL_CONFIGS) - AROME (1.3km, real
    convection-permitting resolution) genuinely falls in the real
    Orlanski micro-scale range; ALADIN (7.5km) and ARPEGE (10km) both
    fall in the real meso-gamma range - not synoptic, despite being ACF's
    own "coarsest" real models."""
    assert classify_spatial_scale(MODEL_CONFIGS["AROME"]["resolution_km"]) == SpatialScale.MICRO
    assert classify_spatial_scale(MODEL_CONFIGS["ALADIN"]["resolution_km"]) == SpatialScale.MESO
    assert classify_spatial_scale(MODEL_CONFIGS["ARPEGE"]["resolution_km"]) == SpatialScale.MESO


def test_classify_temporal_scale_nowcasting():
    assert classify_temporal_scale(0.0) == TemporalScale.NOWCASTING
    assert classify_temporal_scale(5.9) == TemporalScale.NOWCASTING


def test_classify_temporal_scale_short_range():
    assert classify_temporal_scale(6.0) == TemporalScale.SHORT_RANGE
    assert classify_temporal_scale(48.0) == TemporalScale.SHORT_RANGE


def test_classify_temporal_scale_medium_range():
    assert classify_temporal_scale(72.0) == TemporalScale.MEDIUM_RANGE
    assert classify_temporal_scale(240.0) == TemporalScale.MEDIUM_RANGE


def test_classify_temporal_scale_rejects_negative_lead_time():
    with pytest.raises(ValueError, match="not be negative"):
        classify_temporal_scale(-1.0)
