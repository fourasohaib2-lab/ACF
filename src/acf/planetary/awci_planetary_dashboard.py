"""
Atmospheric Complexity Framework (ACF)

Planetary Defense & Interplanetary Observation Dashboard Module (Phase 12)
"""

from typing import Any


class PlanetaryDefenseDashboard:
    """
    Configuration et métadonnées du tableau de bord 'PLANETARY DEFENSE & INTERPLANETARY CENTER' dans AWCI.
    """

    @classmethod
    def get_dashboard_metadata(cls) -> dict[str, Any]:
        """Retourne la configuration complète du workspace Planetary Defense dans AWCI."""
        return {
            "workspace_name": "PLANETARY DEFENSE & INTERPLANETARY CENTER",
            "active_mode": "Autonomous Cosmic Defense & Planetary Science",
            "center_panel": [
                "3D Solar System Trajectory Viewer (Kepler Orbits)",
                "Near-Earth Object (NEO/PHA) Orbit Simulator",
                "Cosmic Impact Shockwave & Tsunami Simulator",
            ],
            "left_panel": [
                "NEO Catalog & Risk Matrix (Torino / Palermo Scale)",
                "Space Observatories Feed (JWST / NEO Surveyor / Rubin)",
                "Planetary Atmosphere & Climate Comparison Table",
            ],
            "right_panel": [
                "Astrobiology & Exoplanet Habitability Gauge",
                "Planetary Reasoning AI Chain",
                "Executive Defense Briefing Generator",
            ],
        }
