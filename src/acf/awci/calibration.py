"""
AWCI Calibration — real separation of calibration from validation
=====================================================================

docs/ACF_MASTER_PROMPT.md section 40:

    DATASET TRAIN → CALIBRATION → MODEL PARAMETERS → LOCKED MODEL
    → INDEPENDENT VALIDATION DATA

    "Ne jamais calibrer et valider sur exactement les mêmes cas sans
    contrôle méthodologique."

Found during this session's exhaustive 90-section conformance audit
(reports/ACF_MASTER_AUDIT_v2.md): no formal train/calibration/
validation separation existed anywhere in this codebase - every
AWCICalculator weight/threshold in production today is `INITIAL`/
`EXPERT_BASED` (see acf.awci.scientific_status), consistent with "no
calibration has happened yet", but also confirming no pipeline existed
to do one properly when real labeled data eventually arrives.

Honest scope - what this module IS and is NOT
-------------------------------------------------
This is the real, general METHODOLOGICAL GUARDRAIL section 40 asks
for: a way to freeze a calibrated AWCICalculator configuration
(weights/interaction terms/level thresholds) against the exact set of
real case IDs it was calibrated on, and a real, enforced check that a
later validation run never reuses any of those same case IDs without
an explicit, disclosed methodological acknowledgment.

This is NOT a weight-fitting/optimization algorithm - there is no real
labeled AWCI ground-truth dataset (real forecaster-verified outcomes
per case) anywhere in this codebase to fit against (see section 36/37
of the same audit: both confirmed absent), and fabricating one from
nothing, or writing an "AutoCalibrator" that pretends to learn optimal
weights from data that doesn't exist, would be exactly the kind of
invented result docs/ACF_MASTER_PROMPT.md's own section 88 exists to
prevent ("si tu dois choisir entre une réponse certaine mais inventée
et une réponse honnête... choisis l'honnête"). A real calibration
ALGORITHM is a separate, future piece of work that needs real data
first - this module is the real infrastructure that algorithm's output
would flow through, usable today with real case IDs from any real
source (a golden dataset, a real METAR-verified event, a manually
curated set) even before that algorithm exists.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime

from acf.awci.calculator import AWCICalculator


class ValidationOverlapError(ValueError):
    """
    Raised when a validation run's case IDs overlap the exact case IDs
    a LockedModel was calibrated on - docs/ACF_MASTER_PROMPT.md section
    40's own explicit rule: "ne jamais calibrer et valider sur
    exactement les mêmes cas sans contrôle méthodologique."
    """


def _now_utc() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True)
class LockedModel:
    """
    A real, frozen AWCICalculator configuration, tagged with a
    calibration version and the exact real case IDs it was calibrated
    against (docs/ACF_MASTER_PROMPT.md section 40's "LOCKED MODEL").

    `frozen=True` prevents reassigning any field after construction;
    every mutable field (`weights`/`interaction_terms`/
    `interaction_weights`/`calibrated_on_case_ids`) is defensively
    copied in `lock_calibration()` below so a caller's later mutation
    of their own original dict/set can never retroactively change an
    already-locked model - the same discipline
    AWCICalculator.__init__() itself already applies to these same
    kinds of arguments.

    Build a real, usable AWCICalculator from this locked configuration
    via `build_calculator()` - never construct AWCICalculator directly
    from a LockedModel's fields by hand, which would risk silently
    drifting from what was actually locked.
    """

    weights: dict[str, float]
    interaction_terms: dict[str, tuple[str, ...]]
    interaction_weights: dict[str, float]
    level_thresholds: tuple[tuple[float, str], ...]
    calibration_version: str
    calibrated_on_case_ids: frozenset[str]
    locked_at: datetime = field(default_factory=_now_utc)
    #: Free-form notes on the real calibration method used (or, honestly,
    #: that none exists yet and these are still the compiled-in
    #: INITIAL/EXPERT_BASED defaults locked as a real baseline) - see
    #: acf.awci.scientific_status for the queryable per-weight status,
    #: which this locking mechanism does not itself alter.
    notes: str = ""

    def build_calculator(self) -> AWCICalculator:
        """Real AWCICalculator constructed from exactly this locked
        configuration - defensive copies again here too, so mutating
        the returned calculator's own instance attributes (which
        AWCICalculator's own __init__ already copies-on-construct)
        can never reach back into this frozen LockedModel."""
        return AWCICalculator(
            weights=dict(self.weights),
            interaction_terms=dict(self.interaction_terms),
            interaction_weights=dict(self.interaction_weights),
            level_thresholds=self.level_thresholds,
        )


def lock_calibration(
    weights: dict[str, float],
    interaction_terms: dict[str, tuple[str, ...]],
    interaction_weights: dict[str, float],
    level_thresholds: tuple[tuple[float, str], ...],
    calibration_version: str,
    calibrated_on_case_ids: Iterable[str],
    notes: str = "",
) -> LockedModel:
    """
    Real constructor for a LockedModel - validates the configuration is
    actually usable (by genuinely constructing an AWCICalculator from
    it - the same validation AWCICalculator.__init__() already performs,
    e.g. interaction_terms/interaction_weights key matching, non-empty
    ascending level_thresholds - reused here, not reimplemented) before
    freezing it, and requires at least one real case ID (an "empty"
    calibration - zero real cases - is not a real calibration, and
    `validate_locked_model()`'s own overlap check would be vacuous
    against an empty set).

    Raises
    ------
    ValueError
        If `calibrated_on_case_ids` is empty, or if the configuration
        itself is invalid (propagated from AWCICalculator.__init__()).
    """
    case_ids = frozenset(calibrated_on_case_ids)
    if not case_ids:
        raise ValueError(
            "calibrated_on_case_ids must not be empty - a LockedModel with no real calibration "
            "cases behind it is not a real calibration, and validate_locked_model()'s overlap "
            "check would never catch anything against an empty set."
        )
    # Real validation, reused from AWCICalculator.__init__() itself -
    # raises ValueError for mismatched interaction keys or invalid
    # level_thresholds, exactly as it would for any other caller.
    AWCICalculator(
        weights=dict(weights),
        interaction_terms=dict(interaction_terms),
        interaction_weights=dict(interaction_weights),
        level_thresholds=level_thresholds,
    )
    return LockedModel(
        weights=dict(weights),
        interaction_terms=dict(interaction_terms),
        interaction_weights=dict(interaction_weights),
        level_thresholds=tuple(level_thresholds),
        calibration_version=calibration_version,
        calibrated_on_case_ids=case_ids,
        notes=notes,
    )


def validate_locked_model(model: LockedModel, validation_case_ids: Iterable[str]) -> None:
    """
    Real enforcement of docs/ACF_MASTER_PROMPT.md section 40's rule:
    "ne jamais calibrer et valider sur exactement les mêmes cas sans
    contrôle méthodologique."

    Parameters
    ----------
    model : LockedModel
        The calibrated, locked model about to be validated.
    validation_case_ids : iterable of str
        The real case IDs the caller is about to validate `model`
        against.

    Raises
    ------
    ValidationOverlapError
        If any validation case ID was also used to calibrate `model` -
        raised BEFORE any real validation computation runs, so a
        methodologically invalid validation can never silently produce
        a number. A caller who has a real, deliberate, disclosed
        reason to validate on overlapping cases (the "contrôle
        méthodologique" section 40 allows for) must catch this
        exception and document that reason explicitly, not bypass this
        check silently.
    """
    overlap = model.calibrated_on_case_ids & set(validation_case_ids)
    if overlap:
        raise ValidationOverlapError(
            f"{len(overlap)} validation case ID(s) overlap this model's own calibration set "
            f"(calibration_version={model.calibration_version!r}): {sorted(overlap)} - build an "
            "independent validation set, or explicitly acknowledge and document the "
            "methodological risk of reusing them."
        )
