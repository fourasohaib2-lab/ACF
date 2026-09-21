"""
Atmospheric Complexity Framework (ACF)

AWCI Decision Support - Recommendation

Deliberately narrow, "noyau réel uniquement" (real-core-only) scope,
user-confirmed: this module exposes ONLY the real, ICAO/FAA-cited
``flight_recommendations`` already present in
``awci.knowledge.hazards.aviation_hazards.AVIATION_HAZARDS_REGISTRY``
(``cat_turbulence``, ``airframe_icing``, ``microburst_windshear`` - the
only 3 of the registry's entries that carry real, cited operational
recommendation text). It never fabricates a recommendation for a
hazard the registry does not cover, and it never attempts to derive a
recommendation from an AWCI composite module score (``dynamic``/
``microphysical``/``convective``/overall AWCI) - those are broad,
blended composite indices, not a clean 1:1 stand-in for one specific,
named ICAO hazard, and conflating "the convective module score is
elevated" with "a microburst is present" would be a real, dangerous
misattribution in a safety-critical domain. A caller who knows, from a
real per-point hazard diagnostic (e.g.
``awci.hazards.cat_turbulence.compute_real_cat_index_at_level()``),
that one of these 3 specific hazards is genuinely active is the one
real, correct way to reach a recommendation here - never an inferred
guess from a coarser score.
"""

from __future__ import annotations

from awci.knowledge.hazards.aviation_hazards import AviationHazardEngine

#: The real 3 AVIATION_HAZARDS_REGISTRY keys that carry real, cited
#: flight_recommendations text today - see module docstring. Exposed so
#: a caller can check membership before assuming a recommendation
#: exists, without needing to know the registry's own internal
#: structure.
HAZARDS_WITH_REAL_RECOMMENDATIONS: frozenset[str] = frozenset(
    {"cat_turbulence", "airframe_icing", "microburst_windshear"}
)


def get_flight_recommendations(hazard_key: str) -> list[str] | None:
    """
    Real, cited flight recommendations for one of the 3 real hazards in
    ``HAZARDS_WITH_REAL_RECOMMENDATIONS`` - a thin, real lookup into
    ``AVIATION_HAZARDS_REGISTRY``, never a fabricated or inferred
    recommendation. Returns ``None`` (never an empty-but-implied-
    "nothing to do" list, and never a fabricated generic recommendation)
    for any other, unknown, or not-yet-covered hazard key - an honest
    "no real, cited recommendation exists for this hazard yet", the
    correct state to report rather than inventing one (see
    ``docs/architecture/acf_awci_architecture_gap_analysis.md`` section
    3 point 3 for the same "genuinely absent, honestly reported"
    discipline this whole package follows).
    """
    hazard = AviationHazardEngine.get_hazard(hazard_key)
    if hazard is None:
        return None
    return list(hazard.flight_recommendations)
