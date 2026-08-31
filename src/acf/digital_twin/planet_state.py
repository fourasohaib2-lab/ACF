"""
Atmospheric Complexity Framework (ACF)

Planetary State & Global Earth System Container Module (Phase 1)
(GlobalEarthState, PlanetState, System Components Metadata)
"""

from dataclasses import dataclass, field
from typing import Any

from acf.digital_twin.state_vector import GlobalEarthStateVector


@dataclass
class GlobalEarthState:
    """État global instantané de la planète Terre."""

    timestamp_utc: str
    state_vector: GlobalEarthStateVector = field(default_factory=GlobalEarthStateVector)
    active_warnings_count: int = 3
    health_status: str = "SYNCHRONIZED / OPERATIONAL DIGITAL TWIN"


class PlanetState:
    """Gestionnaire d'état dynamique planétaire."""

    def __init__(self):
        self.current_state = GlobalEarthState(timestamp_utc="2026-08-02T08:00:00Z")

    def get_planet_status(self) -> dict[str, Any]:
        return {
            "timestamp_utc": self.current_state.timestamp_utc,
            "health_status": self.current_state.health_status,
            "active_warnings_count": self.current_state.active_warnings_count,
            "vector": self.current_state.state_vector.to_dict(),
        }
