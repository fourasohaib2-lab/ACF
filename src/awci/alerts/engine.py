"""
Atmospheric Complexity Framework (ACF)

AWCI Alerts - Engine

Real, headless alert engine - the ``engine.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 19
("Alerts"), composing the already-real
``awci.decision.situation.SituationSnapshot`` (built earlier this
session) into structured ``Alert`` records - the same real "elevated
= High/Very High/Extreme" rule already established by
``awci.dashboard.awci_alerts_panel.compute_elevated_risks()``, but
headless (no PySide6/matplotlib import, unlike that GUI panel), so
this engine is usable outside the dashboard too (a future CLI/API/
notification consumer) - matching this whole session's "decision/rag/
provenance packages stay headless" precedent.

Real, disclosed scope: ``rules.py``/``thresholds.py``/``severity.py``
are deliberately not separate files here - the real severity bands/
elevated-threshold rule this engine uses already exist as
``awci.decision.situation.AWCI_SCORE_BANDS``/``ELEVATED_SCORE_BANDS``;
building a second copy under ``awci.alerts`` would be duplication, not
a real gap closed.
"""

from __future__ import annotations

from dataclasses import dataclass

from awci.decision.recommendation import HAZARDS_WITH_REAL_RECOMMENDATIONS, get_flight_recommendations
from awci.decision.situation import SituationSnapshot


@dataclass(frozen=True)
class Alert:
    """One real, elevated-hazard alert - built entirely from an
    already-real ``HazardAssessment``, never a new severity judgment.
    ``recommendations`` is a real, cited flight-recommendation tuple
    only when the caller's own ``hazard_key_map`` (see
    ``AlertEngine.alerts_for()``) names a real, covered hazard for this
    row - an empty tuple (never fabricated) otherwise."""

    key: str
    label: str
    score: float
    level: str
    recommendations: tuple[str, ...]


class AlertEngine:
    """Real, headless alert engine over an already-built
    ``SituationSnapshot``."""

    def alerts_for(
        self, situation: SituationSnapshot, hazard_key_map: dict[str, str] | None = None
    ) -> tuple[Alert, ...]:
        """
        Real alerts for every real elevated ``HazardAssessment`` in
        ``situation`` (High/Very High/Extreme - see
        ``SituationSnapshot.elevated``'s own docstring). Empty means
        genuinely nothing elevated right now, not "not computed" - the
        same honest-empty convention already established by
        ``awci.dashboard.awci_alerts_panel.compute_elevated_risks()``.

        Parameters
        ----------
        hazard_key_map : dict[str, str] | None
            Optionally maps a real situation-row key (e.g.
            ``"turbulence"``) to a real
            ``AVIATION_HAZARDS_REGISTRY`` key (e.g.
            ``"cat_turbulence"``) to attach real, cited recommendations
            - never inferred automatically (the same real "never
            conflate a coarse module score with one specific named
            hazard" discipline already established in
            ``awci.decision.recommendation``'s own docstring). A row
            with no mapping, or a mapping to a hazard key outside
            ``HAZARDS_WITH_REAL_RECOMMENDATIONS``, honestly gets an
            empty ``recommendations`` tuple, never a fabricated one.
        """
        hazard_key_map = hazard_key_map or {}
        alerts: list[Alert] = []
        for assessment in situation.elevated:
            hazard_key = hazard_key_map.get(assessment.key)
            recommendations: tuple[str, ...] = ()
            if hazard_key is not None and hazard_key in HAZARDS_WITH_REAL_RECOMMENDATIONS:
                real_recommendations = get_flight_recommendations(hazard_key)
                recommendations = tuple(real_recommendations) if real_recommendations else ()
            alerts.append(
                Alert(
                    key=assessment.key,
                    label=assessment.label,
                    score=assessment.score,
                    level=assessment.level,
                    recommendations=recommendations,
                )
            )
        return tuple(alerts)
