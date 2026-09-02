"""
UncertaintyInfo: lightweight uncertainty metadata attachable to a Dataset.

Deliberately small - a single (kind, value, unit) triple, not a
reimplementation of a full uncertainty-quantification engine. Real
sources of a value here already exist in ACF: acf.ai.ensemble.
ensemble_manager.EnsembleManager.spread (ensemble uncertainty),
acf.visualization.ai_forecast_center.model_consensus_engine.
ModelConsensusEngine.compute_real_multi_model_disagreement()'s
disagreement_spread (model uncertainty). This class is the metadata
container that lets a Dataset honestly say "unassessed" instead of
silently implying certainty when no real uncertainty computation was
run - it is not itself a new uncertainty computation.
"""

from dataclasses import dataclass

#: Matches the Prompt Maître's own section 32 taxonomy - only the two
#: kinds ACF has a real computation for today are usable without
#: fabricating a number; the others are named so a caller can at least
#: label an uncertainty source honestly even before ACF computes it.
KNOWN_KINDS = (
    "not_assessed",
    "ensemble",
    "model_disagreement",
    "observational",
    "numerical",
    "representation",
    "temporal",
)


@dataclass
class UncertaintyInfo:
    kind: str = "not_assessed"
    value: float | None = None
    unit: str | None = None

    def __post_init__(self) -> None:
        if self.kind not in KNOWN_KINDS:
            raise ValueError(f"kind must be one of {KNOWN_KINDS}, got {self.kind!r}")
        if self.kind != "not_assessed" and self.value is None:
            raise ValueError(f"kind={self.kind!r} requires a real value - use kind='not_assessed' if none was computed")
