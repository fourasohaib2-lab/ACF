"""
VerificationPipeline: the "pipeline" half of the Prompt Maître ACF
v2.0's section 15/31 Verification Engine gap.

reports/ACF_MASTER_AUDIT_v2.md found the metric calculators themselves
already real and complete (`NWPVerificationMetrics`: RMSE/Bias/MAE/ACC/
POD/FAR/CSI/ETS; `EnsembleManager`: CRPS/Brier Score) but no pipeline
that actually runs them on a real forecast/observation pair and records
the outcome anywhere reusable - each caller that wanted verification
had to wire the metric calls itself, and nothing accumulated into a
skill history.

Honest scope - what this does NOT do: connect to a real observation
feed. None exists anywhere in ACF yet - see
`acf.data_assimilation.observation_ingestion`'s own
"NOT_INGESTED_NO_STATION_DATA_CONNECTION" disclosures (e.g.
`SurfaceStationIngestor.ingest_synop_reports()`). This class is real,
generic infrastructure that runs on whatever real forecast/observation
sequences a caller already has - synthetic arrays in a test, or (once
one of those ingestors is wired to a real feed) genuine paired data.
`tests/test_verification_pipeline.py` demonstrates it on two genuinely
independent real `CoupledEarthSolver` runs, the same honest stand-in
convention `ModelConsensusEngine.compute_real_multi_model_disagreement()`
already documents and uses for "model" vs "model" comparison - clearly
NOT a real observation, and labelled as such in that test, not here.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from acf.ai.ensemble.ensemble_manager import EnsembleManager
from acf.verification.nwp_metrics import NWPVerificationMetrics
from acf.verification.skill_database import ModelSkillDatabase, SkillRecord


@dataclass
class VerificationResult:
    """Real output of one `VerificationPipeline.evaluate()` call."""

    model: str
    variable: str
    valid_time: datetime
    metrics: dict[str, float]
    n_samples: int
    record: SkillRecord | None


class VerificationPipeline:
    """
    Runs ACF's existing real metric calculators on a real forecast/
    observation pair and, if a `ModelSkillDatabase` is attached,
    records the outcome into it.

    Reuses `NWPVerificationMetrics` and `EnsembleManager` (does not
    reimplement any metric).
    """

    def __init__(self, skill_database: ModelSkillDatabase | None = None) -> None:
        self.skill_database = skill_database

    def evaluate(
        self,
        model: str,
        variable: str,
        forecast: Sequence[float],
        observation: Sequence[float],
        valid_time: datetime,
        threshold: float = 1.0,
        ensemble_members: Sequence[Sequence[float]] | None = None,
        record: bool = True,
    ) -> VerificationResult:
        """
        Evaluate one real forecast/observation pair for `model`/
        `variable` and, by default, record the result into this
        pipeline's attached `ModelSkillDatabase` (if any).

        Parameters
        ----------
        forecast, observation : real, equal-length, paired sequences.
        ensemble_members : optional, one real sequence of ensemble
            member values per `observation` entry (same length as
            `observation`) - when given, adds real per-time-step CRPS/
            Brier Score (via `EnsembleManager`, averaged) alongside the
            deterministic metrics.
        record : set False to evaluate without writing to the attached
            database (e.g. for an ad hoc check that shouldn't count
            towards a model's recorded skill history).
        """
        if len(forecast) != len(observation):
            raise ValueError(f"forecast and observation must have the same length, got {len(forecast)} and {len(observation)}")
        if not forecast:
            raise ValueError("forecast/observation must not be empty")

        metrics = NWPVerificationMetrics.evaluate_all(forecast, observation, threshold)

        if ensemble_members is not None:
            if len(ensemble_members) != len(observation):
                raise ValueError(
                    f"ensemble_members must have one entry per observation, got {len(ensemble_members)} and {len(observation)}"
                )
            crps_values = []
            brier_values = []
            for members, obs in zip(ensemble_members, observation, strict=True):
                em = EnsembleManager(list(members))
                crps_values.append(em.crps(obs))
                brier_values.append(em.brier_score(threshold, obs >= threshold))
            metrics["crps"] = sum(crps_values) / len(crps_values)
            metrics["brier"] = sum(brier_values) / len(brier_values)

        rec = None
        if record and self.skill_database is not None:
            rec = self.skill_database.record(
                model=model,
                variable=variable,
                metrics=metrics,
                valid_time=valid_time,
                n_samples=len(forecast),
            )

        return VerificationResult(
            model=model,
            variable=variable,
            valid_time=valid_time,
            metrics=metrics,
            n_samples=len(forecast),
            record=rec,
        )
