"""
Atmospheric Complexity Framework (ACF)

AWCI Real-Time Mission Control Monitoring Dashboard Module (Phase 10)
"""

from typing import Any


class AWCIMonitoringDashboard:
    """
    Configuration et métadonnées du tableau de bord 'GLOBAL REAL-TIME EARTH MONITORING MISSION CONTROL' dans AWCI.

    NOTE (Physics Guard, 2026-09-06 Tier E sweep): a static workspace/
    section/layer-name descriptor, the third instance of the same
    pattern found this sweep (see acf.master.awci_master_dashboard.
    MasterDashboard and acf.ai_expert.awci_ai_dashboard.
    AWCI_AIDashboard's own NOTEs) - no status/certification field to
    fabricate, but verified by grep, not constructed anywhere in src/
    outside this package's own tests/test_monitoring_platform.py. The
    25-layer "live_map_layers" list describes a UI that isn't rendered
    by any real widget - distinct from acf.monitoring's actually-real,
    already-audited telemetry/anomaly/health/event-stream engines.
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
