"""
Atmospheric Complexity Framework (ACF)

AWCI Decision Support - Engine

Real, thin orchestrator composing ``awci.decision.situation`` and
``awci.decision.recommendation`` into one ``DecisionSupportView`` - the
``engine.py`` entry point named in
``docs/architecture/awci_reference_architecture.md`` section 13:
"Gathers information into an operational view. Does not replace the
decision maker." No new computation happens here; see this package's
own ``__init__.py`` docstring for the explicit "noyau réel uniquement"
scope this Phase 1 build stays within.
"""

from __future__ import annotations

from dataclasses import dataclass

from awci.decision.context import DecisionContext
from awci.decision.recommendation import HAZARDS_WITH_REAL_RECOMMENDATIONS, get_flight_recommendations
from awci.decision.situation import SituationSnapshot, build_situation_snapshot


@dataclass(frozen=True)
class DecisionSupportView:
    """
    Real, composed operational view - a real ``SituationSnapshot`` plus
    real, cited recommendations for whichever of the caller-supplied
    ``active_hazard_keys`` are genuinely covered by
    ``awci.decision.recommendation`` (see that module's own docstring
    for why this is never inferred from a coarse module score).
    """

    situation: SituationSnapshot
    recommendations: dict[str, list[str]]


def assess(
    context: DecisionContext,
    module_scores: dict[str, float],
    overall_awci: float,
    physical_score: float | None = None,
    forecast_score: float | None = None,
    active_hazard_keys: tuple[str, ...] = (),
) -> DecisionSupportView:
    """
    Real, composed decision-support view for one point/time/level.

    Parameters
    ----------
    context : DecisionContext
        Real point/level/time this view is about.
    module_scores, overall_awci, physical_score, forecast_score :
        The exact same real, already-computed AWCI outputs
        ``awci.decision.situation.build_situation_snapshot()`` already
        takes - see that function's own docstring.
    active_hazard_keys : tuple[str, ...]
        Real, caller-known-active specific hazards (e.g.
        ``("cat_turbulence",)``) to look up real, cited recommendations
        for - never inferred here from ``module_scores`` (see
        ``awci.decision.recommendation``'s own docstring for why).
        Keys outside ``HAZARDS_WITH_REAL_RECOMMENDATIONS`` are silently
        skipped (not an error - a caller may reasonably pass a hazard
        key this package does not yet cover), consistent with
        ``get_flight_recommendations()``'s own honest ``None`` return
        for those.

    Returns
    -------
    DecisionSupportView
    """
    situation = build_situation_snapshot(
        context=context,
        module_scores=module_scores,
        overall_awci=overall_awci,
        physical_score=physical_score,
        forecast_score=forecast_score,
    )
    recommendations: dict[str, list[str]] = {}
    for hazard_key in active_hazard_keys:
        if hazard_key not in HAZARDS_WITH_REAL_RECOMMENDATIONS:
            continue
        hazard_recommendations = get_flight_recommendations(hazard_key)
        if hazard_recommendations is not None:
            recommendations[hazard_key] = hazard_recommendations
    return DecisionSupportView(situation=situation, recommendations=recommendations)
