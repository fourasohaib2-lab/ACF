"""
Atmospheric Complexity Framework (ACF)

AWCI Autonomous AI Expert Dashboard Module
"""

from typing import Any


class AWCI_AIDashboard:
    """
    Configuration et métadonnées du tableau de bord 'AUTONOMOUS AI EXPERT CONTROL CENTER' dans AWCI.

    NOTE (Physics Guard, 2026-09-06 Tier E sweep): a static workspace/
    panel-name descriptor, same pattern as this session's
    acf.master.awci_master_dashboard.MasterDashboard (see that
    module's own NOTE) - no status/certification field to fabricate,
    but verified by grep, not constructed anywhere in src/ outside
    this package's own tests/test_ai_expert.py. The panel names
    themselves describe a UI that isn't rendered by any real widget.
    """

    @classmethod
    def get_dashboard_metadata(cls) -> dict[str, Any]:
        """Retourne la configuration complète du workspace Autonomous AI Expert dans AWCI."""
        return {
            "workspace_name": "AUTONOMOUS AI METEOROLOGIST & EARTH SYSTEM EXPERT WORKSPACE",
            "active_mode": "Autonomous Reasoning & Multi-Agent Intelligence",
            "panels": [
                "AI Confidence Gauge & Multi-Model Consensus Matrix",
                "Causal Physical Reasoning Graph",
                "Multi-Hazard Threat Monitor & Cascade Chain",
                "Sectorial Recommended Actions Board",
                "Executive Briefing & Natural Language Dialog Interface",
            ],
            "center_panel": ["Reasoning Graph Network", "Interactive Scientific Dialog"],
        }
