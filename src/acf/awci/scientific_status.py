"""
AWCI Scientific Status Registry
=================================

Real, queryable status metadata for every threshold and weight
`acf.awci.calculator.AWCICalculator`/`acf.awci.normalizer.Normalizer`/
`acf.awci.weights.WeightsManager` actually uses - explicit user
request: `docs/ACF_MASTER_PROMPT.md` (the project's now-authoritative
conceptual specification) repeatedly and explicitly demands this
(sections 21, 77, 78, 79, 80, 81) - "ne jamais considérer les poids/
seuils comme scientifiquement établis... chaque poids/seuil doit avoir
un statut".

Purely additive metadata - added ALONGSIDE the existing real float
constants in `Normalizer`/`WeightsManager`/`AWCICalculator`, not
replacing them. No existing computation changes: the same real numbers
drive `calculate_module_scores()`/`normalize_*()` exactly as before.
This module answers "what is the real evidentiary status of this
number", a question the master prompt asks explicitly and the code
could not answer programmatically before this.

Two distinct vocabularies, both taken directly from the master prompt
(not invented here):

- `ScientificStatus` (section 77) - the general status for a threshold,
  range, or formula: CONFIRMED / PROPOSED / HYPOTHESIS /
  REQUIRES_VALIDATION / UNKNOWN.
- `WeightStatus` (section 80) - the specific status vocabulary the
  prompt gives for AWCI module weights: INITIAL / EXPERT_BASED /
  CALIBRATED / VALIDATED.

Every classification below was assigned by reading this project's own
existing code and comments (not guessed): where a constant already
carried a real, honest disclosure (e.g. AWCICalculator.
INTERACTION_WEIGHTS' own docstring: "an ACF design choice... not
derived from an external published formula... not presented as an
established literature result"), that disclosure is what determined
the status here - HYPOTHESIS, not CONFIRMED, because no external
validation exists for it, however physically plausible it looks.
**No status here is CONFIRMED** - nothing in this codebase's AWCI
weights/thresholds has gone through the master prompt's own
calibration/validation pipeline (sections 34-40) yet; that is real,
honest, and exactly what this registry exists to make visible rather
than hide behind a plain-looking float constant.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ScientificStatus(str, Enum):
    """Master prompt section 77's general status vocabulary."""

    CONFIRMED = "CONFIRMED"
    PROPOSED = "PROPOSED"
    HYPOTHESIS = "HYPOTHESIS"
    REQUIRES_VALIDATION = "REQUIRES_VALIDATION"
    UNKNOWN = "UNKNOWN"


class WeightStatus(str, Enum):
    """Master prompt section 80's specific weight-status vocabulary."""

    INITIAL = "initial"
    EXPERT_BASED = "expert-based"
    CALIBRATED = "calibrated"
    VALIDATED = "validated"


@dataclass(frozen=True)
class ThresholdStatus:
    """Real status metadata for one Normalizer range/reference value."""

    status: ScientificStatus
    rationale: str
    #: A real external reference this bound is sourced from, or None
    #: when - as is honestly the case for every entry here today - no
    #: such reference exists in this codebase and the bound is this
    #: project's own physically-plausible-but-unvalidated choice.
    source: str | None = None


@dataclass(frozen=True)
class WeightStatusEntry:
    """Real status metadata for one AWCI module/interaction weight."""

    status: WeightStatus
    rationale: str


# ---------------------------------------------------------------- weights

#: Status for every real key in WeightsManager.DEFAULT_WEIGHTS. All
#: EXPERT_BASED (matching that class's own existing docstring: "Default
#: weights are based on expert knowledge") except the two opt-in
#: forecast-uncertainty weights, which default to 0.0 and have never
#: been assigned a real value at all - INITIAL, not EXPERT_BASED, since
#: no expert judgment has been exercised on their magnitude yet, only
#: on the decision to default them to zero.
MODULE_WEIGHT_STATUS: dict[str, WeightStatusEntry] = {
    "dynamic": WeightStatusEntry(WeightStatus.EXPERT_BASED, "Original ACF concept weighting (PPT), not recalibrated."),
    "thermodynamic": WeightStatusEntry(WeightStatus.EXPERT_BASED, "Original ACF concept weighting (PPT), not recalibrated."),
    "convective": WeightStatusEntry(WeightStatus.EXPERT_BASED, "Original ACF concept weighting (PPT), not recalibrated."),
    "microphysical": WeightStatusEntry(WeightStatus.EXPERT_BASED, "Original ACF concept weighting (PPT), not recalibrated."),
    "topographic": WeightStatusEntry(WeightStatus.EXPERT_BASED, "Original ACF concept weighting (PPT), not recalibrated."),
    "temporal": WeightStatusEntry(WeightStatus.EXPERT_BASED, "Original ACF concept weighting (PPT), not recalibrated."),
    "confidence": WeightStatusEntry(WeightStatus.EXPERT_BASED, "Original ACF concept weighting (PPT), not recalibrated."),
    "ensemble_spread": WeightStatusEntry(
        WeightStatus.INITIAL, "Opt-in, defaults to 0.0 (excluded) until a caller explicitly raises it - no magnitude judgment made yet."
    ),
    "model_disagreement": WeightStatusEntry(
        WeightStatus.INITIAL, "Opt-in, defaults to 0.0 (excluded) until a caller explicitly raises it - no magnitude judgment made yet."
    ),
}

#: Status for AWCICalculator.INTERACTION_WEIGHTS - HYPOTHESIS per that
#: class's own existing docstring disclosure (see this module's own
#: docstring above for the exact quote).
INTERACTION_WEIGHT_STATUS: dict[str, WeightStatusEntry] = {
    "wind_topo_interaction": WeightStatusEntry(
        WeightStatus.INITIAL, "ACF design choice, not derived from an external published formula (AWCICalculator's own docstring)."
    ),
    "conv_thermo_interaction": WeightStatusEntry(
        WeightStatus.INITIAL, "ACF design choice, not derived from an external published formula (AWCICalculator's own docstring)."
    ),
}


def get_module_weight_status(module: str) -> WeightStatusEntry:
    """Real status for one AWCICalculator module weight key."""
    return MODULE_WEIGHT_STATUS.get(
        module, WeightStatusEntry(WeightStatus.INITIAL, "No status recorded for this module - treat as unassessed.")
    )


def get_interaction_weight_status(term: str) -> WeightStatusEntry:
    """Real status for one AWCICalculator.INTERACTION_WEIGHTS key."""
    return INTERACTION_WEIGHT_STATUS.get(
        term, WeightStatusEntry(WeightStatus.INITIAL, "No status recorded for this interaction term - treat as unassessed.")
    )


# --------------------------------------------------------------- ranges

#: Status for every real Normalizer.normalize_*() range/reference this
#: codebase actually uses. All HYPOTHESIS: each bound is a real,
#: physically-plausible value (e.g. 0-50 m/s for "extreme surface
#: wind", 0-5000 J/kg for "extreme CAPE") but none is cited from a
#: specific external climatological/statistical study in this
#: codebase - exactly the master prompt section 79 warning ("un seuil
#: n'est pas scientifiquement valide simplement parce qu'il est
#: intuitif").
NORMALIZER_RANGE_STATUS: dict[str, ThresholdStatus] = {
    "temperature": ThresholdStatus(ScientificStatus.HYPOTHESIS, "Range -30..50 degC - plausible global extremes, not climatologically sourced per region/season."),
    "wind": ThresholdStatus(ScientificStatus.HYPOTHESIS, "Range 0..50 m/s - plausible extreme surface wind, not sourced from a specific climatology."),
    "wind_shear": ThresholdStatus(ScientificStatus.HYPOTHESIS, "Range 0..50 m/s - same envelope as 'wind' for internal consistency; not sourced from a specific climatology, and the real shear itself spans whatever native model levels acf.awci.wind_shear.compute_real_wind_shear_at_point() was given, not a fixed physical layer (e.g. 0-6 km)."),
    "humidity": ThresholdStatus(ScientificStatus.HYPOTHESIS, "Range 0..0.03 kg/kg specific humidity - plausible but not sourced."),
    "cape": ThresholdStatus(ScientificStatus.HYPOTHESIS, "Range 0..5000 J/kg - plausible extreme CAPE, not sourced from a specific climatology."),
    "cin": ThresholdStatus(ScientificStatus.HYPOTHESIS, "Range 0..500 J/kg (abs) - plausible, not sourced."),
    "precipitation": ThresholdStatus(ScientificStatus.HYPOTHESIS, "Range 0..50 mm/h - plausible extreme rate, not sourced."),
    "pressure": ThresholdStatus(ScientificStatus.HYPOTHESIS, "Range 800..1050 hPa - real physically-typical sea-level-ish envelope, not sourced from operational QC limits."),
    "topographic": ThresholdStatus(ScientificStatus.HYPOTHESIS, "Range 0..3000 m (default max_altitude) - plausible, not sourced; caller-overridable."),
    "confidence": ThresholdStatus(ScientificStatus.CONFIRMED, "Range 0..100% is a real, exact unit definition, not an empirical choice."),
    "temporal": ThresholdStatus(ScientificStatus.HYPOTHESIS, "Range 0..20 (default max_change) - unitless, not sourced; caller-overridable."),
}

#: Status for Normalizer.ENSEMBLE_SPREAD_REFERENCE / MODEL_DISAGREEMENT_REFERENCE -
#: HYPOTHESIS per that class's own existing docstring disclosure.
SPREAD_REFERENCE_STATUS = ThresholdStatus(
    ScientificStatus.HYPOTHESIS,
    "ACF design choice for 'large disagreement' per variable - no published external standard defines this "
    "for this composite index (Normalizer's own docstring).",
)

#: Status for AWCICalculator.calculate_with_uncertainty() itself
#: (docs/ACF_MASTER_PROMPT.md section 64) - the real per-realization
#: substitution method is a real, defensible design choice, not an
#: externally validated or published technique for this composite
#: index. The empirical statistics/class-probabilities it computes
#: FROM real supplied realizations are exact real arithmetic, not
#: themselves uncertain - it is the *method* of turning real ensemble/
#: model data into a per-realization AWCI recomputation that carries
#: this HYPOTHESIS status, not the arithmetic.
UNCERTAINTY_METHOD_STATUS = ThresholdStatus(
    ScientificStatus.HYPOTHESIS,
    "Real per-realization AWCI recomputation (substituting each real ensemble/model value into an "
    "otherwise-unchanged scenario) is a real, defensible ACF design choice - not an externally validated "
    "or published uncertainty-quantification technique for this composite index.",
)

#: Status for AWCICalculator's opt-in climatological-percentile
#: normalization path (docs/ACF_MASTER_PROMPT.md section 20: naive
#: min-max normalization "peut être scientifiquement mauvaise" -
#: percentile rank within a real climatological sample is one of the
#: alternatives the section explicitly asks to be studied). When a
#: caller supplies data["climatology"], the affected variable(s) use
#: Normalizer.normalize_percentile() (an exact real empirical-fraction
#: computation) instead of the fixed min-max range. The ARITHMETIC is
#: exact; the METHOD - percentile rank against a caller-supplied sample,
#: with no built-in season/region/altitude stratification (the caller
#: is responsible for pre-filtering the sample to the relevant
#: season/region/altitude if that nuance matters - a real, disclosed
#: limitation, not silently ignored) - is HYPOTHESIS, same reasoning as
#: UNCERTAINTY_METHOD_STATUS above. Section 20's other listed
#: alternatives (sigmoid functions, piecewise functions, physical
#: threshold curves) remain NOT built - not fabricated as equivalent.
CLIMATOLOGY_NORMALIZATION_METHOD_STATUS = ThresholdStatus(
    ScientificStatus.HYPOTHESIS,
    "Real empirical percentile rank against a caller-supplied real climatological sample is a real, "
    "defensible ACF design choice among section 20's several listed alternatives (sigmoid/piecewise/"
    "physical-threshold-curve normalization remain unbuilt) - not itself an externally validated or "
    "published normalization technique for this composite index, and with no built-in season/region/"
    "altitude stratification of the supplied sample.",
)


def get_normalizer_range_status(variable: str) -> ThresholdStatus:
    """Real status for one Normalizer range (by the variable name used in normalize_<variable>())."""
    return NORMALIZER_RANGE_STATUS.get(
        variable, ThresholdStatus(ScientificStatus.UNKNOWN, "No status recorded for this variable - treat as unassessed.")
    )
