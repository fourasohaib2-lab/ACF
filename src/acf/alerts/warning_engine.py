"""
Atmospheric Complexity Framework (ACF)

Operational Warning & Meteorological Alert Engine Module (MISSION ACF-030 Phase 7)
(Thunderstorm, Heavy Rain, Flash Flood, Snow, Blizzard, Fog, Wind, Tornado, Hail, Volcanic Ash Warnings)
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4


@dataclass
class OperationalWarning:
    """Structure officielle d'une vigilance / alerte météorologique opérationnelle."""

    warning_id: str
    phenomenon: str
    severity: str  # "Yellow" (Vigilance), "Orange" (Alerte), "Red" (Alerte Maximale / Urgence)
    probability_pct: float
    confidence_score: float | None
    affected_regions: list[str]
    valid_from: str
    valid_until: str
    expected_impacts: list[str]
    recommended_actions: list[str]
    scientific_explanation: str
    ai_explanation: str


class WarningEngine:
    """Moteur de génération et de diffusion des alertes météorologiques opérationnelles WMO/EUMETNET CAP."""

    def __init__(self):
        self.active_warnings: list[OperationalWarning] = []

    def issue_warning(
        self,
        phenomenon: str,
        severity: str,
        probability_pct: float,
        affected_regions: list[str],
        valid_hours: float = 24.0,
        scientific_explanation: str = "",
        ai_explanation: str = "",
        confidence_score: float | None = None,
    ) -> OperationalWarning:
        """
        Génère et enregistre une alerte opérationnelle d'urgence.

        NOTE (correction): valid_from/valid_until used to be hardcoded
        to a fixed "2026-08-02T08:00:00Z" / "2026-08-03T08:00:00Z" for
        every warning regardless of when issue_warning() was actually
        called - valid_hours was genuinely accepted as a parameter but
        never used anywhere in the method body, so a caller requesting
        a 6-hour warning still got the same fixed ~24h window from a
        fixed calendar date. Operationally dangerous: once that fixed
        date passed, every newly issued "urgent" warning would show an
        already-expired validity period. confidence_score was also a
        fixed "0.90" for every warning regardless of phenomenon/
        severity/probability, with no real forecast-confidence model
        connected. Fix: valid_from/valid_until now genuinely derive
        from the real issuance time and the caller's valid_hours;
        confidence_score is only set when a caller genuinely supplies
        one (e.g. from real ensemble spread), else honestly None.
        """
        w_id = f"WARN-{uuid4().hex[:8].upper()}"

        issued_at = datetime.now(timezone.utc)
        valid_until_dt = issued_at + timedelta(hours=valid_hours)

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
            confidence_score=confidence_score,
            affected_regions=affected_regions,
            valid_from=issued_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            valid_until=valid_until_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            expected_impacts=impacts,
            recommended_actions=actions,
            scientific_explanation=scientific_explanation
            or f"Alerte déclenchée en raison des conditions favorables à {phenomenon}.",
            ai_explanation=ai_explanation or f"Prédiction d'IA confirmant un risque élevé de {phenomenon}.",
        )
        self.active_warnings.append(warning)
        return warning

    def get_active_warnings(self) -> list[OperationalWarning]:
        """Retourne la liste des alertes en cours."""
        return self.active_warnings
