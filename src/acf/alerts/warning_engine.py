"""
Atmospheric Complexity Framework (ACF)

Operational Warning & Meteorological Alert Engine Module (MISSION ACF-030 Phase 7)
(Thunderstorm, Heavy Rain, Flash Flood, Snow, Blizzard, Fog, Wind, Tornado, Hail, Volcanic Ash Warnings)
"""

from dataclasses import dataclass
from typing import List
from uuid import uuid4


@dataclass
class OperationalWarning:
    """Structure officielle d'une vigilance / alerte météorologique opérationnelle."""
    warning_id: str
    phenomenon: str
    severity: str  # "Yellow" (Vigilance), "Orange" (Alerte), "Red" (Alerte Maximale / Urgence)
    probability_pct: float
    confidence_score: float
    affected_regions: List[str]
    valid_from: str
    valid_until: str
    expected_impacts: List[str]
    recommended_actions: List[str]
    scientific_explanation: str
    ai_explanation: str


class WarningEngine:
    """Moteur de génération et de diffusion des alertes météorologiques opérationnelles WMO/EUMETNET CAP."""

    def __init__(self):
        self.active_warnings: List[OperationalWarning] = []

    def issue_warning(
        self,
        phenomenon: str,
        severity: str,
        probability_pct: float,
        affected_regions: List[str],
        valid_hours: float = 24.0,
        scientific_explanation: str = "",
        ai_explanation: str = "",
    ) -> OperationalWarning:
        """Génère et enregistre une alerte opérationnelle d'urgence."""
        w_id = f"WARN-{uuid4().hex[:8].upper()}"

        impacts = [
            f"Risque important lié à {phenomenon} dans les zones désignées.",
            "Perturbations possibles des transports routiers, aériens et maritimes.",
        ]
        actions = [
            "Tenez-vous informé de l'évolution des conditions météorologiques.",
            "Respectez les consignes de sécurité émises par les autorités locales.",
        ]

        warning = OperationalWarning(
            warning_id=w_id,
            phenomenon=phenomenon,
            severity=severity,
            probability_pct=probability_pct,
            confidence_score=0.90,
            affected_regions=affected_regions,
            valid_from="2026-08-02T08:00:00Z",
            valid_until="2026-08-03T08:00:00Z",
            expected_impacts=impacts,
            recommended_actions=actions,
            scientific_explanation=scientific_explanation or f"Alerte déclenchée en raison des conditions favorables à {phenomenon}.",
            ai_explanation=ai_explanation or f"Prédiction d'IA confirmant un risque élevé de {phenomenon}.",
        )
        self.active_warnings.append(warning)
        return warning

    def get_active_warnings(self) -> List[OperationalWarning]:
        """Retourne la liste des alertes en cours."""
        return self.active_warnings
