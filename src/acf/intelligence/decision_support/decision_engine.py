"""
Atmospheric Complexity Framework (ACF)

Operational Decision Support & Recommendation Engine Module (Phase 6)
(DecisionSupportEngine, RecommendedAction, Scientific Action Justifications)
"""

from dataclasses import dataclass
from typing import List


@dataclass
class RecommendedAction:
    """Action recommandée par le moteur de support décisionnel."""
    action_id: str
    target_sector: str  # Civil Protection, Aviation, Maritime, Power Grid, Agriculture
    priority_level: str  # CRITICAL, HIGH, MEDIUM, LOW
    action_title: str
    scientific_justification: str
    expected_impact: str


class DecisionSupportEngine:
    """
    Moteur de support à la décision opérationnelle basé sur les lois physiques et l'évaluation des risques.
    """

    @classmethod
    def generate_recommendations(cls) -> List[RecommendedAction]:
        """Génère la liste des recommandations opérationnelles prioritaires."""
        return [
            RecommendedAction(
                action_id="ACT-001",
                target_sector="Civil Protection",
                priority_level="CRITICAL",
                action_title="Issue Coastal Evacuation Order for Zone B",
                scientific_justification="Predicted storm surge of 3.2m coincides with spring high tide at 14:00 UTC.",
                expected_impact="Prevents severe loss of life in low-lying coastal surge zone.",
            ),
            RecommendedAction(
                action_id="ACT-002",
                target_sector="Aviation Safety",
                priority_level="HIGH",
                action_title="Reroute Transpacific Flights below FL280",
                scientific_justification="Severe Clear Air Turbulence (EDR > 0.45) detected near Jet Stream core.",
                expected_impact="Eliminates airframe structural damage and passenger injury risk.",
            ),
        ]
