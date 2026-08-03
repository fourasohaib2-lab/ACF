"""
Atmospheric Complexity Framework (ACF)

Global Early Warning System (EWS) Module (Phase 5)
"""

from typing import Any, Dict


class EarlyWarningSystem:
    """Système d'alerte précoce mondial (EWS - Early Warning System)."""

    WARNING_LEVELS = ["GREEN", "YELLOW", "ORANGE", "RED"]

    @classmethod
    def get_warning_level(cls, risk_score: float = 0.85) -> Dict[str, Any]:
        """Détermine le niveau d'alerte universel (GREEN, YELLOW, ORANGE, RED)."""
        if risk_score >= 0.8:
            level = "RED (Emergency)"
        elif risk_score >= 0.6:
            level = "ORANGE (Danger)"
        elif risk_score >= 0.3:
            level = "YELLOW (Monitoring)"
        else:
            level = "GREEN (Normal)"

        return {
            "risk_score": risk_score,
            "warning_level": level,
            "action_required": "IMMEDIATE_CIVIL_PROTECTION_DEPLOYMENT" if risk_score >= 0.8 else "MONITORING",
        }
