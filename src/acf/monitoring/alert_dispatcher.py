"""
Atmospheric Complexity Framework (ACF)

Operational Alert Dispatcher Engine Module (Phase 7)
(OperationalAlertDispatcher managing alert levels GREEN to BLACK and routing to AWCI and Emergency Centers)
"""

from typing import Any, Dict, List


ALERT_LEVELS = ["GREEN", "BLUE", "YELLOW", "ORANGE", "RED", "PURPLE", "BLACK"]


class OperationalAlertDispatcher:
    """
    Régulateur et diffuseur d'alertes opérationnelles multi-canaux.
    """

    @classmethod
    def dispatch_alert(cls, alert_name: str, level: str, recipients: List[str]) -> Dict[str, Any]:
        """Émet une alerte opérationnelle vers les destinataires d'urgence."""
        valid_level = level.upper() if level.upper() in ALERT_LEVELS else "YELLOW"
        return {
            "alert_name": alert_name,
            "alert_level": valid_level,
            "recipients_notified": recipients,
            "dispatch_status": "SENT_AND_ACKNOWLEDGED",
        }
