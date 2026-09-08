"""
Atmospheric Complexity Framework (ACF)

Crisis Timeline Engine Module (Phase 7)
"""

from typing import Any


class CrisisTimelineEngine:
    """Générateur de la chronologie dynamique d'une crise environnementale."""

    @classmethod
    def get_crisis_timeline(cls) -> dict[str, Any]:
        """
        NOTE (correction): this used to unconditionally return a
        fabricated 5-step storm timeline (landfall in 24h, peak in
        48h...) with status "TIMELINE_ACTIVE", as if describing a real
        ongoing crisis - with no crisis/forecast data connected (0
        parameters). Not fabricated here.
        """
        return {"timeline_steps": [], "status": "NOT_ACTIVE_NO_CRISIS_TRACKED", "is_real_data": False}
