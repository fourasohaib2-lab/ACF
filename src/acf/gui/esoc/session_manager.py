"""Session manager for automatic workspace state, panel layouts, and settings persistence (ACF-UI-013)."""

from typing import Dict, Any, Optional
import os
import json


class SessionManager:
    """Saves and restores user ESOC workspace sessions, panels, and mode configurations (Phase 13)."""

    def __init__(self, session_filepath: str = "esoc_session_config.json") -> None:
        self.session_filepath = session_filepath
        self.current_session: Dict[str, Any] = self._default_session_state()

    def _default_session_state(self) -> Dict[str, Any]:
        """Generate default configuration state dictionary."""
        return {
            "workspace_mode": "Meteorologist",
            "active_layers": ["Satellite RGB", "Radar Mosaic", "2m Temp", "Wind Vectors", "MSLP"],
            "map_view_mode": "2D Mercator Map",
            "map_center_lat": 20.0,
            "map_center_lon": 0.0,
            "map_zoom_level": 3,
            "theme": "Dark_Meteorological",
            "auto_refresh_sec": 5,
            "hpc_gpu_enabled": True,
            "recent_projects": ["Global_NWP_2026", "Climate_SSP2_2050", "Hurricane_Track_Analysis"],
            "simulation_settings": {
                "timestep_sec": 60.0,
                "horizon_hours": 360,
                "resolution": "Global 25km",
                "physics_scheme": "Primitive Equations Core",
            },
            "panel_visibility": {
                "earth_monitoring": True,
                "earth_physics": True,
                "simulation": True,
                "digital_twin": True,
                "ai_forecast": True,
                "hazards": True,
                "data_assimilation": True,
                "climate": True,
                "ocean": True,
                "hydrology": True,
                "cryosphere": True,
                "air_quality": True,
                "carbon": True,
                "space_weather": True,
                "geology": True,
                "verification": True,
                "system_console": True,
                "hpc": True,
                "timeline": True,
                "alerts": True,
            },
        }

    def save_session(self, session_data: Optional[Dict[str, Any]] = None) -> bool:
        """Serialize session state dictionary to disk JSON file."""
        if session_data is not None:
            self.current_session.update(session_data)

        try:
            with open(self.session_filepath, "w") as f:
                json.dump(self.current_session, f, indent=2)
            return True
        except Exception:
            return False

    def load_session(self) -> Dict[str, Any]:
        """Read session configuration from disk JSON file if available."""
        if os.path.exists(self.session_filepath):
            try:
                with open(self.session_filepath, "r") as f:
                    data = json.load(f)
                    self.current_session.update(data)
            except Exception:
                pass
        return self.current_session
