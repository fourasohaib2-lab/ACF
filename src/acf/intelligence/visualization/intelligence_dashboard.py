"""
Atmospheric Complexity Framework (ACF)

Earth Intelligence Dashboard & AWCI Mission Control Module (Phase 12)
"""

from typing import Any, Dict


class EarthIntelligenceDashboard:
    """
    Configuration et métadonnées du tableau de bord 'EARTH INTELLIGENCE MISSION CONTROL' dans AWCI.
    """

    @classmethod
    def get_dashboard_metadata(cls) -> Dict[str, Any]:
        """Retourne la configuration complète du workspace Earth Intelligence Mission Control."""
        return {
            "workspace_name": "EARTH INTELLIGENCE MISSION CONTROL",
            "active_mode": "Autonomous Scientific AI & Planetary Decision Support Platform",
            "active_panels": [
                "Mission Control Center",
                "Scientific AI Reasoning Tree",
                "Digital Twin Planetary State",
                "Knowledge Graph Inspector",
                "Domain Agents Panel (Meteorology, Ocean, Space Weather)",
                "Action Recommendations & Decision Support",
                "Model Consensus & AI Confidence Gauge",
                "Timeline & Emergency Optimization Solver",
            ],
            "center_panel": ["3D Interactive Earth Globe", "Multi-Hazard Cascade Overlay"],
            "bottom_panel": ["Autonomous Workflow Planner", "Real-Time Log Feeds"],
        }
