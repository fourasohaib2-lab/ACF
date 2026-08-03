"""
Atmospheric Complexity Framework (ACF)

AI Forecast Intelligence Dashboard & Mode Manager Module (Phase 1, 10)
"""

from typing import Any, Dict


class AIForecastDashboard:
    """Tableau de bord central de l'intelligence artificielle de prévision."""

    @classmethod
    def get_dashboard_config(cls, mode: str = "METEOROLOGIST") -> Dict[str, Any]:
        """Retourne la configuration du tableau de bord selon le mode d'utilisation."""
        mode_upper = mode.upper()
        if mode_upper == "AI_SCIENTIST":
            panels = ["AI Attention Maps", "Model Bias Analysis", "XAI Feature Importance", "Neural Latent Space"]
        elif mode_upper == "EMERGENCY":
            panels = ["Multi-Hazard Risk Probability", "Population & Infrastructure Exposure", "Impact Prediction Bulletin"]
        else:  # METEOROLOGIST
            panels = ["Multi-Model Consensus Matrix", "Radar & Satellite Overlay", "Skew-T Soundings", "Ensemble Plumes"]

        return {
            "mode": mode_upper,
            "active_panels": panels,
            "dashboard_status": "DASHBOARD_ACTIVE",
        }
