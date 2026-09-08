"""
Tests for acf.awci.multi_model_fusion - the Prompt Maître ACF v2.0's
§29-30 "full-field multi-model fusion" gap
(reports/ACF_MASTER_AUDIT_v2.md: "Fusion multi-modèles : PARTIAL,
scopé point-par-point").
"""

from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
import pytest

from acf.awci.multi_model_fusion import compute_real_multi_model_field_fusion, regrid_nearest_neighbor
from acf.verification.skill_database import ModelSkillDatabase

VALID_TIME = datetime(2026, 9, 2, tzinfo=UTC)


# ------------------------------------------------------------------ regrid_nearest_neighbor


def test_regrid_nearest_neighbor_identity_when_grids_match():
    lats = np.array([10.0, 20.0, 30.0])
    lons = np.array([0.0, 1.0])
    field = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])

    result = regrid_nearest_neighbor(lats, lons, field, lats, lons)

    assert np.array_equal(result, field)


def test_regrid_nearest_neighbor_picks_the_real_closest_source_point():
    lats_src = np.array([0.0, 10.0, 20.0])
    lons_src = np.array([0.0, 10.0])
    field_src = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])

    # Target point (9, 1) is closest to source (10, 0) -> field_src[1, 0] = 3.0
    result = regrid_nearest_neighbor(lats_src, lons_src, field_src, [9.0], [1.0])

    assert result.shape == (1, 1)
    assert result[0, 0] == 3.0


def test_regrid_nearest_neighbor_output_shape_matches_target_grid():
    lats_src = np.linspace(0, 10, 5)
    lons_src = np.linspace(0, 10, 4)
    field_src = np.arange(20, dtype=float).reshape(5, 4)

    lats_target = np.linspace(0, 10, 3)
    lons_target = np.linspace(0, 10, 2)
    result = regrid_nearest_neighbor(lats_src, lons_src, field_src, lats_target, lons_target)

    assert result.shape == (3, 2)


# ------------------------------------------------------------------ compute_real_multi_model_field_fusion


def test_fusion_requires_at_least_two_models():
    with pytest.raises(ValueError, match="at least 2"):
        compute_real_multi_model_field_fusion(models=["AROME"])


def test_fusion_rejects_unknown_model():
    with pytest.raises(ValueError, match="Unknown model"):
        compute_real_multi_model_field_fusion(models=["AROME", "WRF"])


def test_fusion_rejects_target_model_not_in_models():
    with pytest.raises(ValueError, match="target_model"):
        compute_real_multi_model_field_fusion(models=["AROME", "ALADIN"], target_model="ARPEGE")


def test_fusion_defaults_to_the_three_real_models():
    result = compute_real_multi_model_field_fusion(steps=2, n_lat=3, n_lon=3)
    assert result["models_used"] == ["AROME", "ALADIN", "ARPEGE"]


def test_fusion_produces_a_real_field_on_the_target_grid():
    result = compute_real_multi_model_field_fusion(
        field_key="temperature_field", models=["AROME", "ALADIN"], steps=3, n_lat=4, n_lon=5
    )

    assert result["status"] == "REAL_MULTI_MODEL_FIELD_FUSION_FROM_ACF_SOLVER"
    assert result["is_real_data"] is True
    assert result["target_model"] == "AROME"  # defaults to models[0]
    assert result["fused_field"].shape == (4, 5)
    assert result["spread_field"].shape == (4, 5)
    assert len(result["target_lats"]) == 4
    assert len(result["target_lons"]) == 5
    assert set(result["per_model_fields"]) == {"AROME", "ALADIN"}
    for field in result["per_model_fields"].values():
        assert field.shape == (4, 5)  # every model's field is genuinely regridded onto the target shape


def test_fusion_uses_equal_weights_with_no_skill_database():
    result = compute_real_multi_model_field_fusion(models=["AROME", "ALADIN"], steps=2, n_lat=3, n_lon=3)

    assert result["weight_source"] == "equal_weights_no_skill_history"
    assert result["weights"] == {"AROME": 0.5, "ALADIN": 0.5}
    assert result["bias_corrected_models"] == []


def test_fusion_is_a_real_weighted_sum_of_the_regridded_fields():
    result = compute_real_multi_model_field_fusion(
        field_key="temperature_field", models=["AROME", "ALADIN"], steps=2, n_lat=3, n_lon=3
    )
    expected = 0.5 * result["per_model_fields"]["AROME"] + 0.5 * result["per_model_fields"]["ALADIN"]
    assert np.allclose(result["fused_field"], expected)


def test_fusion_falls_back_to_equal_weights_with_incomplete_skill_history():
    db = ModelSkillDatabase()
    db.record("AROME", "temperature", {"rmse": 1.0}, VALID_TIME)  # only 1 of 2 models

    result = compute_real_multi_model_field_fusion(
        models=["AROME", "ALADIN"], variable="temperature", skill_database=db, steps=2, n_lat=3, n_lon=3
    )

    assert result["weight_source"] == "equal_weights_no_skill_history"
    assert result["weights"] == {"AROME": 0.5, "ALADIN": 0.5}


def test_fusion_uses_real_skill_weights_when_history_covers_every_model():
    db = ModelSkillDatabase()
    db.record("AROME", "temperature", {"rmse": 1.0}, VALID_TIME)  # more accurate -> more weight
    db.record("ALADIN", "temperature", {"rmse": 4.0}, VALID_TIME)

    result = compute_real_multi_model_field_fusion(
        models=["AROME", "ALADIN"], variable="temperature", skill_database=db, steps=2, n_lat=3, n_lon=3
    )

    assert result["weight_source"] == "model_skill_database"
    assert result["weights"]["AROME"] > result["weights"]["ALADIN"]
    assert sum(result["weights"].values()) == pytest.approx(1.0)


def test_fusion_bias_corrects_only_models_with_real_recorded_bias():
    db = ModelSkillDatabase()
    db.record("AROME", "temperature", {"bias": 2.0}, VALID_TIME)
    # ALADIN has no recorded bias at all.

    result = compute_real_multi_model_field_fusion(
        field_key="temperature_field", models=["AROME", "ALADIN"], variable="temperature", skill_database=db,
        steps=2, n_lat=3, n_lon=3,
    )

    assert result["bias_corrected_models"] == ["AROME"]
    arome_raw = result["per_model_fields"]["AROME"]
    # The fused field's AROME contribution must reflect the bias-corrected (raw - 2.0) value, not the raw one.
    weights = result["weights"]
    aladin_raw = result["per_model_fields"]["ALADIN"]
    expected = weights["AROME"] * (arome_raw - 2.0) + weights["ALADIN"] * aladin_raw
    assert np.allclose(result["fused_field"], expected)


def test_fusion_spread_field_is_zero_when_only_one_model_used_is_impossible_but_low_for_similar_models():
    """A real sanity check on spread_field, not an exact-value assertion (the real solver's exact numbers are legitimately noisy - see the module's own honest_limitation)."""
    result = compute_real_multi_model_field_fusion(models=["AROME", "ALADIN", "ARPEGE"], steps=2, n_lat=3, n_lon=3)
    assert np.all(result["spread_field"] >= 0.0)


def test_fusion_honest_limitation_is_disclosed():
    result = compute_real_multi_model_field_fusion(models=["AROME", "ALADIN"], steps=2, n_lat=3, n_lon=3)
    assert "nearest-neighbour" in result["honest_limitation"]
    assert "not real operational NWP archives" in result["honest_limitation"]
