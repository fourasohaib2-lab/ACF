"""
Atmospheric Complexity Framework (ACF)

AWCI Real-Time Mission Control Monitoring Dashboard Module (Phase 10)
"""

from typing import Any


class AWCIMonitoringDashboard:
    """
    Configuration et métadonnées du tableau de bord 'GLOBAL REAL-TIME EARTH MONITORING MISSION CONTROL' dans AWCI.
    """

    @classmethod
    def get_dashboard_metadata(cls) -> dict[str, Any]:
        """Retourne la configuration complète du workspace Real-Time Monitoring dans AWCI."""
        return {
            "workspace_name": "GLOBAL REAL-TIME EARTH MONITORING MISSION CONTROL",
            "active_mode": "Continuous Planetary Operations Center",
            "sections": [
                "Global Earth System Live Status & Health Gauge",
                "3D Real-Time Photorealistic Earth Globe & Satellite Overlay",
                "Live Weather Radar & Dual-Pol Reflectivity Composite",
                "Current Active Hazards & Cascading Threat Ribbon",
                "Multi-Model AI Confidence & Consensus Telemetry",
                "Hardware Infrastructure Telemetry (CPU, RAM, GPU, Cluster, Latency)",
                "Digital Twin Synchronization & Event Log Console",
            ],
            "live_map_layers": [
                "Temperature",
                "Pressure",
                "Wind",
                "Humidity",
                "Rainfall",
                "Radar",
                "Satellite",
                "Clouds",
                "Lightning",
                "Snow",
                "Sea Ice",
                "Ocean Currents",
                "Wave Height",
                "SST",
                "Wildfires",
                "Smoke",
                "Dust",
                "Air Quality",
                "Cyclones",
                "Floods",
                "Heatwaves",
                "Drought",
                "Volcanoes",
                "Earthquakes",
                "Solar Storms",
            ],
            "alert_levels": ["GREEN", "BLUE", "YELLOW", "ORANGE", "RED", "PURPLE", "BLACK"],
            "center_panel": ["3D Live Earth Globe", "Active Hazards Ribbon"],
        }
