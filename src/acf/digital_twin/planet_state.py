"""
Atmospheric Complexity Framework (ACF)

Planetary State & Global Earth System Container Module (Phase 1)
(GlobalEarthState, PlanetState, System Components Metadata)
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from acf.digital_twin.state_vector import GlobalEarthStateVector


@dataclass
class GlobalEarthState:
    """
    État global instantané de la planète Terre.

    NOTE (correction): active_warnings_count/health_status used to
    default to a fixed "3"/"SYNCHRONIZED / OPERATIONAL DIGITAL TWIN"
    for any instance, claiming 3 warnings are always active and the
    twin is always synchronized with no real warning tracker or
    synchronization process ever connected - the same fabrication
    pattern independently found and fixed in
    science/query_engine.py's own "health_status" claim. Not
    fabricated.
    """

    timestamp_utc: str
    state_vector: GlobalEarthStateVector = field(default_factory=GlobalEarthStateVector)
    active_warnings_count: int | None = None
    health_status: str | None = "NOT_SYNCHRONIZED_NO_REAL_DATA_EXCHANGE_CONNECTED"


class PlanetState:
    """Gestionnaire d'état dynamique planétaire."""

    def __init__(self):
        # NOTE (correction): timestamp_utc used to be a fixed literal
        # string, so "current" state was permanently frozen at
        # 2026-08-02T08:00:00Z regardless of when this was actually
        # instantiated. Now genuinely computed from the real clock.
        self.current_state = GlobalEarthState(timestamp_utc=datetime.now(timezone.utc).isoformat())

    def get_planet_status(self) -> dict[str, Any]:
        return {
            "timestamp_utc": self.current_state.timestamp_utc,
            "health_status": self.current_state.health_status,
            "active_warnings_count": self.current_state.active_warnings_count,
            "vector": self.current_state.state_vector.to_dict(),
        }
