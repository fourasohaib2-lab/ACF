"""
Atmospheric Complexity Framework (ACF)

AWCI Decision Support - Situation

Real composition of an operational "situation" view from the exact
same real, already-computed AWCI outputs an existing caller (e.g.
``AWCIDashboard``) already has ready - the same real inputs
``awci.dashboard.awci_alerts_panel.compute_elevated_risks()`` already
takes, and the same real module-key -> label mapping
``awci.dashboard.awci_risk_summary._ROWS`` already establishes (mirrored
here as a plain, headless constant - see ``test_row_mapping_matches_the_
gui_risk_summary_rows`` in this package's test file for the parity
lock, and this package's own ``__init__.py`` docstring for why this
does not simply import that GUI module directly). No new score is
computed here - only real, already-computed scores classified and
packaged.

``AWCI_SCORE_BANDS`` mirrors ``awci.dashboard.awci_colors.LEVELS``
exactly (the module docstring there: "Single shared 0-100 color scale
used by every AWCI widget") - the real, canonical AWCI severity-band
scale, not a second, independently-invented one. Locked to that
module's own real values by a parity test, for the same "avoid a
silent, undetected drift between two classification scales" reason
this session already found and disclosed a real pre-existing
inconsistency for (``awci.dashboard.awci_risk_summary._BANDS`` uses
only 5 bands, folding "Very Low" into "Low" - a real, pre-existing
divergence from ``awci_colors.LEVELS``'s own 6 bands, left as-is since
fixing a GUI display module is out of this package's own scope, but
this module deliberately follows the 6-band ``awci_colors.LEVELS``
scale, not the 5-band one, since that module's own docstring names it
canonical).
"""

from __future__ import annotations

from dataclasses import dataclass

from awci.decision.context import DecisionContext

#: Real, canonical 0-100 AWCI severity bands - mirrors
#: awci.dashboard.awci_colors.LEVELS exactly (threshold, name), locked
#: by a parity test. See module docstring for why this package does not
#: import that GUI module directly.
AWCI_SCORE_BANDS: tuple[tuple[float, str], ...] = (
    (0, "Very Low"),
    (20, "Low"),
    (35, "Moderate"),
    (50, "High"),
    (65, "Very High"),
    (85, "Extreme"),
)

#: Real, elevated-only bands - matches
#: awci.dashboard.awci_alerts_panel._ELEVATED_LEVELS exactly (High and
#: above are worth surfacing as "elevated"; Very Low/Low/Moderate are
#: not).
ELEVATED_SCORE_BANDS = frozenset({"High", "Very High", "Extreme"})

#: Real module-key -> (label, module-score-key) mapping - mirrors the
#: key/label/module fields of
#: awci.dashboard.awci_risk_summary._ROWS exactly (that tuple's own
#: 2nd field, an emoji icon, is a pure UI concern out of scope for this
#: headless package - see module docstring). "__physical__"/
#: "__forecast__" are the same real sentinel keys that module's own
#: compute_elevated_risks() already uses to read the physical/forecast
#: composite scores rather than a per-hazard module_scores entry;
#: module=None means "the overall AWCI score itself", also the same
#: real convention.
SITUATION_ROWS: tuple[tuple[str, str, str | None], ...] = (
    ("turbulence", "Turbulence Risk", "dynamic"),
    ("icing", "Icing Risk", "microphysical"),
    ("convective", "Convective Risk", "convective"),
    ("overall", "Overall Complexity", None),
    ("physical", "Physical Complexity", "__physical__"),
    ("forecast", "Forecast Complexity", "__forecast__"),
)


def classify_awci_score(score: float) -> str:
    """Real AWCI_SCORE_BANDS classification for a 0-100 score - the
    same real algorithm as awci.dashboard.awci_colors.level_for(),
    reimplemented here (not imported, per this package's own headless
    requirement) against the identical, parity-tested band table."""
    level = AWCI_SCORE_BANDS[0][1]
    for threshold, name in AWCI_SCORE_BANDS:
        if score >= threshold:
            level = name
    return level


@dataclass(frozen=True)
class HazardAssessment:
    """One real row of the situation - a real, already-computed AWCI
    module (or composite) score, classified into its real severity
    band. Never a fabricated or estimated score."""

    key: str
    label: str
    score: float
    level: str

    @property
    def is_elevated(self) -> bool:
        return self.level in ELEVATED_SCORE_BANDS


@dataclass(frozen=True)
class SituationSnapshot:
    """
    Real operational situation - every row from SITUATION_ROWS that had
    a real score available, classified into its real severity band.
    "Gathers information into an operational view. Does not replace the
    decision maker." (reference architecture section 13) - this
    snapshot states what the real, already-computed scores are, and
    nothing more; it recommends nothing by itself (see
    ``awci.decision.recommendation`` for the real, separately-scoped,
    cited recommendation text).
    """

    context: DecisionContext
    assessments: tuple[HazardAssessment, ...]

    @property
    def elevated(self) -> tuple[HazardAssessment, ...]:
        """Real subset currently at High/Very High/Extreme - empty
        means genuinely nothing elevated right now, not "not
        computed" (same honest-empty convention as
        awci.dashboard.awci_alerts_panel.compute_elevated_risks())."""
        return tuple(a for a in self.assessments if a.is_elevated)

    def get(self, key: str) -> HazardAssessment | None:
        for assessment in self.assessments:
            if assessment.key == key:
                return assessment
        return None


def build_situation_snapshot(
    context: DecisionContext,
    module_scores: dict[str, float],
    overall_awci: float,
    physical_score: float | None = None,
    forecast_score: float | None = None,
) -> SituationSnapshot:
    """
    Real situation snapshot from the exact same real, already-computed
    inputs ``awci.dashboard.awci_alerts_panel.compute_elevated_risks()``
    already takes - no new score computed here, only real values
    classified and packaged into ``SituationSnapshot``.

    Deliberate, disclosed divergence from that GUI function: a row is
    OMITTED (never fabricated as a 0.0 "Very Low" score) when its real
    score is genuinely unavailable (``physical_score``/
    ``forecast_score`` is ``None``, or a ``module_scores`` key is
    missing) - ``compute_elevated_risks()`` instead defaults a missing
    ``module_scores`` entry to ``0.0`` (an existing, real, tested GUI
    behavior this package does not alter), which this decision-support
    package's own honest-data discipline treats as a real risk of
    silently presenting "not yet assessed" as "assessed and safe" -
    unacceptable for a package whose stated purpose is to inform a
    real operational decision.
    """
    specials = {"__physical__": physical_score, "__forecast__": forecast_score}
    assessments: list[HazardAssessment] = []
    for key, label, module in SITUATION_ROWS:
        if module is None:
            score: float | None = overall_awci
        elif module in specials:
            score = specials[module]
        else:
            score = module_scores.get(module)
        if score is None:
            continue
        assessments.append(HazardAssessment(key=key, label=label, score=score, level=classify_awci_score(score)))
    return SituationSnapshot(context=context, assessments=tuple(assessments))
