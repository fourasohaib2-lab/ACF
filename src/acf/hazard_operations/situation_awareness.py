"""
Atmospheric Complexity Framework (ACF)

Situational Awareness & COP Module
"""

from typing import Any


class SituationalAwareness:
    """Module d'aperçu de situation globale (Common Operational Picture - COP)."""

    @classmethod
    def get_cop_summary(cls) -> dict[str, Any]:
        """
        NOTE (correction): this used to unconditionally claim
        "ORANGE_ELEVATED, 2 active cyclones, 5 severe storm warnings"
        - a fabricated global situational picture presented as a real
        Common Operational Picture, with no live data source connected
        (0 parameters). Not fabricated here.
        """
        return {
            "global_hazard_level": "UNKNOWN_NO_LIVE_DATA_CONNECTED",
            "active_tropical_cyclones_count": None,
            "active_severe_storm_warnings_count": None,
            "status": "NOT_READY_NO_DATA_SOURCE",
            "is_real_data": False,
        }
