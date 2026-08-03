"""
Atmospheric Complexity Framework (ACF)

Planetary Digital Twin Dashboard & AWCI 3D Globe Workspace Integration Module (Phase 9)
"""

from typing import Any, Dict


class PlanetaryDashboard:
    """
    Configuration et métadonnées du tableau de bord 'PLANETARY DIGITAL TWIN' dans AWCI.
    """

    @classmethod
    def get_dashboard_metadata(cls) -> Dict[str, Any]:
        """Retourne la configuration complète du workspace Planetary Digital Twin."""
        return {
            "workspace_name": "PLANETARY DIGITAL TWIN",
            "active_mode": "Real-Time Synchronized Earth System Twin (DestinE Equivalent)",
            "available_views": [
                "3D Earth Globe View",
                "Atmospheric Layer View",
                "Ocean & Waves View",
                "Hydrology & River Basin View",
                "Climate Indices View",
                "Solid Earth Geology View",
                "Space Weather & Ionosphere View",
                "Physics-Informed AI View",
                "Multi-Hazard Cascade View",
            ],
            "left_panel_controls": ["Layer Manager", "Earth Components", "NWP / AI Models", "Observations Feeds"],
            "center_panel": ["Interactive 3D Photorealistic Globe", "Timeline Player", "4D Particle Streamlines"],
            "right_panel": ["Physics Engine Inspector", "AI Confidence Gauge", "Equations Viewer", "Knowledge Graph"],
            "bottom_panel": ["Simulation Controller Time Step", "FPS Counter", "Map Projections Switcher"],
        }
