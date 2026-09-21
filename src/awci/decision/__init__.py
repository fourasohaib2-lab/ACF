"""
Atmospheric Complexity Framework (ACF)

AWCI Decision Support (``src/awci/decision/``)

Real implementation of the package specified in
``docs/architecture/awci_reference_architecture.md`` section 13:
"Gathers information into an operational view. Does not replace the
decision maker." - a genuinely absent piece until now (see
``docs/architecture/acf_awci_architecture_gap_analysis.md`` section 3,
point 3, and the corresponding row in that document's own gap table).

Phase 1 scope (explicit, user-confirmed, "noyau réel uniquement"): only
what composes real, already-computed AWCI outputs into an operational
view, or reuses real, ICAO/FAA-cited operational recommendations
already in this codebase - never a fabricated risk-matrix scheme,
confidence model, alternatives search, or scenario projection. The
reference architecture's own remaining modules (``risk_matrix.py``,
``confidence.py``, ``alternatives.py``, ``scenario.py``) are
deliberately NOT built here - each would need a real, cited
methodology (e.g. the real ICAO Doc 9859 SMS 5x5 risk matrix) before
being added, not an ACF-invented scheme.

Deliberately headless: no PySide6/matplotlib/cartopy import anywhere in
this package, unlike ``awci.dashboard``'s own GUI-side risk display
(``awci_risk_summary.py``, ``awci_alerts_panel.py``) - a real usability
requirement for this package to be usable from a future CLI/API layer
as well as the GUI, per the reference architecture's own placement of
``decision/`` as a peer to ``dashboard/``, not a GUI submodule.
"""

from __future__ import annotations

from awci.decision.context import DecisionContext
from awci.decision.engine import DecisionSupportView, assess
from awci.decision.recommendation import get_flight_recommendations
from awci.decision.situation import (
    AWCI_SCORE_BANDS,
    HazardAssessment,
    SituationSnapshot,
    classify_awci_score,
)

__all__ = [
    "AWCI_SCORE_BANDS",
    "DecisionContext",
    "DecisionSupportView",
    "HazardAssessment",
    "SituationSnapshot",
    "assess",
    "classify_awci_score",
    "get_flight_recommendations",
]
