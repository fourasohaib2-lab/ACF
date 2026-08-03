"""
Atmospheric Complexity Framework (ACF)

Emergency Operations Dashboard & Profile Manager Module (Phase 8)
"""

from typing import Any, Dict


class HazardDashboard:
    """Tableau de bord de commandement des opérations d'urgence et de sécurité civile."""

    @classmethod
    def get_dashboard_profile(cls, profile_name: str = "CIVIL_PROTECTION") -> Dict[str, Any]:
        """Retourne la configuration du tableau de bord selon le profil de commandement."""
        p_upper = profile_name.upper()
        if p_upper == "GOVERNMENT_DECISION":
            modules = ["Global Risk Index", "Economic Exposure Impact", "Critical Infrastructure Map", "Strategic Action Directives"]
        elif p_upper == "METEOROLOGICAL_CENTER":
            modules = ["Radar Reflectivity Composite", "Satellite IR & RGB", "Multi-Model NWP Warnings", "Convective Soundings"]
        else:  # CIVIL_PROTECTION
            modules = ["Active Emergency Alerts", "Real-Time Population Exposure", "Evacuation Routes & Shelters", "First Responder Logistics"]

        return {
            "profile": p_upper,
            "active_modules": modules,
            "dashboard_status": "PROFILE_ACTIVE",
        }
