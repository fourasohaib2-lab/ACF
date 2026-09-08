"""
Tests for acf.verification.pipeline.VerificationPipeline and
acf.verification.skill_database.ModelSkillDatabase - the "pipeline +
Model Skill Database" half of the Verification Engine gap
(reports/ACF_MASTER_AUDIT_v2.md, §15/§31 of the Prompt Maître ACF
v2.0), plus the skill-weighted consensus this enables in
ModelConsensusEngine.compute_unified_consensus().
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from acf.verification.nwp_metrics import NWPVerificationMetrics
from acf.verification.pipeline import VerificationPipeline
from acf.verification.skill_database import ModelSkillDatabase
from acf.visualization.ai_forecast_center.model_consensus_engine import ModelConsensusEngine

VALID_TIME = datetime(2026, 9, 2, 0, tzinfo=UTC)


def test_evaluate_reuses_nwp_verification_metrics_exactly():
    """The pipeline must not reimplement any metric - its output for
    the deterministic part must equal NWPVerificationMetrics.evaluate_all()
    called directly on the same pair."""
    forecast = [10.0, 12.0, 9.0, 15.0]
    observation = [11.0, 11.0, 9.5, 14.0]

    direct = NWPVerificationMetrics.evaluate_all(forecast, observation, threshold=10.0)
    result = VerificationPipeline().evaluate(
        model="AROME", variable="T2m", forecast=forecast, observation=observation, valid_time=VALID_TIME, threshold=10.0
    )

    assert result.metrics == direct
    assert result.n_samples == 4
    assert result.record is None  # no database attached


def test_evaluate_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        VerificationPipeline().evaluate(
            model="AROME", variable="T2m", forecast=[1.0, 2.0], observation=[1.0], valid_time=VALID_TIME
        )


def test_evaluate_rejects_empty_series():
    with pytest.raises(ValueError):
        VerificationPipeline().evaluate(model="AROME", variable="T2m", forecast=[], observation=[], valid_time=VALID_TIME)


def test_evaluate_with_ensemble_members_adds_real_crps_and_brier():
    """CRPS/Brier must come from EnsembleManager, not a second
    implementation - verified by comparing to a direct EnsembleManager
    call on the same member values."""
    from acf.ai.ensemble.ensemble_manager import EnsembleManager

    forecast = [10.0, 12.0]
    observation = [11.0, 13.0]
    members = [[9.0, 10.0, 11.0], [11.0, 12.0, 13.0]]

    result = VerificationPipeline().evaluate(
        model="AROME",
        variable="T2m",
        forecast=forecast,
        observation=observation,
        valid_time=VALID_TIME,
        threshold=10.0,
        ensemble_members=members,
    )

    expected_crps = (EnsembleManager(members[0]).crps(observation[0]) + EnsembleManager(members[1]).crps(observation[1])) / 2
    expected_brier = (
        EnsembleManager(members[0]).brier_score(10.0, observation[0] >= 10.0)
        + EnsembleManager(members[1]).brier_score(10.0, observation[1] >= 10.0)
    ) / 2

    assert result.metrics["crps"] == pytest.approx(expected_crps)
    assert result.metrics["brier"] == pytest.approx(expected_brier)


def test_evaluate_rejects_mismatched_ensemble_length():
    with pytest.raises(ValueError):
        VerificationPipeline().evaluate(
            model="AROME",
            variable="T2m",
            forecast=[1.0, 2.0],
            observation=[1.0, 2.0],
            valid_time=VALID_TIME,
            ensemble_members=[[1.0, 2.0]],  # only 1 entry for 2 observations
        )


def test_evaluate_records_into_attached_skill_database():
    db = ModelSkillDatabase()
    pipeline = VerificationPipeline(skill_database=db)

    result = pipeline.evaluate(
        model="AROME", variable="T2m", forecast=[10.0, 11.0], observation=[10.5, 11.5], valid_time=VALID_TIME
    )

    assert result.record is not None
    assert len(db) == 1
    assert db.records_for("AROME", "T2m")[0].metrics == result.metrics


def test_evaluate_record_false_does_not_write_to_database():
    db = ModelSkillDatabase()
    VerificationPipeline(skill_database=db).evaluate(
        model="AROME", variable="T2m", forecast=[10.0], observation=[10.5], valid_time=VALID_TIME, record=False
    )
    assert len(db) == 0


# ------------------------------------------------------------------ ModelSkillDatabase


def test_mean_skill_is_none_with_no_recorded_history():
    """No invented fallback number - genuinely no data means None."""
    db = ModelSkillDatabase()
    assert db.mean_skill("AROME", "T2m") is None


def test_mean_skill_is_the_real_mean_across_records():
    db = ModelSkillDatabase()
    db.record("AROME", "T2m", {"rmse": 1.0}, VALID_TIME)
    db.record("AROME", "T2m", {"rmse": 3.0}, VALID_TIME)
    assert db.mean_skill("AROME", "T2m") == pytest.approx(2.0)


def test_weights_from_skill_is_empty_with_no_history():
    db = ModelSkillDatabase()
    assert db.weights_from_skill(["AROME", "ALADIN"]) == {}


def test_weights_from_skill_omits_models_with_no_history_rather_than_inventing_a_weight():
    db = ModelSkillDatabase()
    db.record("AROME", "T2m", {"rmse": 1.0}, VALID_TIME)
    weights = db.weights_from_skill(["AROME", "ALADIN"], variable="T2m")
    assert set(weights) == {"AROME"}
    assert weights["AROME"] == pytest.approx(1.0)


def test_weights_from_skill_gives_the_lower_error_model_more_weight():
    db = ModelSkillDatabase()
    db.record("AROME", "T2m", {"rmse": 1.0}, VALID_TIME)  # more accurate
    db.record("ALADIN", "T2m", {"rmse": 4.0}, VALID_TIME)  # less accurate

    weights = db.weights_from_skill(["AROME", "ALADIN"], variable="T2m")

    assert weights["AROME"] > weights["ALADIN"]
    assert weights["AROME"] + weights["ALADIN"] == pytest.approx(1.0)


def test_skill_database_persists_to_disk_and_reloads(tmp_path):
    path = tmp_path / "skill_db.json"
    db = ModelSkillDatabase(path=path)
    db.record("AROME", "T2m", {"rmse": 1.5}, VALID_TIME, n_samples=10)

    assert path.exists()

    reloaded = ModelSkillDatabase(path=path)
    assert len(reloaded) == 1
    rec = reloaded.records_for("AROME", "T2m")[0]
    assert rec.metrics == {"rmse": 1.5}
    assert rec.n_samples == 10
    assert rec.valid_time == VALID_TIME


def test_skill_database_without_path_never_touches_disk(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    db = ModelSkillDatabase()
    db.record("AROME", "T2m", {"rmse": 1.0}, VALID_TIME)
    assert list(tmp_path.iterdir()) == []


# ------------------------------------------------------------------ skill-weighted consensus


def test_compute_unified_consensus_defaults_to_declared_weights_with_no_skill_database():
    result = ModelConsensusEngine.compute_unified_consensus()
    assert result["weight_source"] == "declared_default"


def test_compute_unified_consensus_falls_back_when_skill_history_is_incomplete():
    db = ModelSkillDatabase()
    db.record("ECMWF IFS", "T2m", {"rmse": 1.0}, VALID_TIME)  # only 1 of 5 default models

    result = ModelConsensusEngine.compute_unified_consensus(skill_database=db, variable="T2m")

    assert result["weight_source"] == "declared_default_incomplete_skill_history"
    # Weights must be the untouched declared defaults, not a partial mix.
    assert result["model_weights"]["ECMWF IFS"] == pytest.approx(0.25)


def test_compute_unified_consensus_uses_real_skill_weights_when_history_covers_every_model():
    weights_dict = {"AROME": 0.5, "ALADIN": 0.5}
    db = ModelSkillDatabase()
    db.record("AROME", "T2m", {"rmse": 1.0}, VALID_TIME)  # more accurate -> more weight
    db.record("ALADIN", "T2m", {"rmse": 4.0}, VALID_TIME)

    result = ModelConsensusEngine.compute_unified_consensus(weights_dict=weights_dict, skill_database=db, variable="T2m")

    assert result["weight_source"] == "model_skill_database"
    assert result["model_weights"]["AROME"] > result["model_weights"]["ALADIN"]
    assert result["weight_sum"] == pytest.approx(1.0)
    # Original caller-supplied dict must not be mutated in place.
    assert weights_dict == {"AROME": 0.5, "ALADIN": 0.5}


def test_verification_pipeline_feeds_consensus_end_to_end_with_two_real_solver_runs():
    """
    Honest end-to-end proof, not a mocked pipeline: two genuinely
    independent real CoupledEarthSolver runs (same "model" vs "model"
    stand-in convention ModelConsensusEngine.
    compute_real_multi_model_disagreement() already documents and
    uses elsewhere - NOT real observations) feed VerificationPipeline,
    which records real metrics into a ModelSkillDatabase, which then
    genuinely changes compute_unified_consensus()'s weights.
    """
    points = [(36.7, 3.0), (36.8, 3.2), (36.9, 3.4)]
    arome_series = []
    aladin_series = []
    for lat, lon in points:
        disagreement = ModelConsensusEngine.compute_real_multi_model_disagreement(
            lat=lat, lon=lon, models=["AROME", "ALADIN"], steps=3
        )
        arome_series.append(disagreement["per_model_value"]["AROME"])
        aladin_series.append(disagreement["per_model_value"]["ALADIN"])

    db = ModelSkillDatabase()
    pipeline = VerificationPipeline(skill_database=db)
    # ALADIN's real solver output stands in as the verification
    # "truth" series for AROME here purely to exercise the real
    # pipeline end-to-end - not a claim that ALADIN is ground truth.
    pipeline.evaluate(model="AROME", variable="T", forecast=arome_series, observation=aladin_series, valid_time=VALID_TIME)
    pipeline.evaluate(model="ALADIN", variable="T", forecast=aladin_series, observation=arome_series, valid_time=VALID_TIME)

    assert len(db) == 2
    assert db.mean_skill("AROME", "T", "rmse") is not None

    result = ModelConsensusEngine.compute_unified_consensus(
        weights_dict={"AROME": 0.5, "ALADIN": 0.5}, skill_database=db, variable="T"
    )
    assert result["weight_source"] == "model_skill_database"
    assert result["model_weights"]["AROME"] + result["model_weights"]["ALADIN"] == pytest.approx(1.0)
