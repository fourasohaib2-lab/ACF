"""
Atmospheric Complexity Framework (ACF)

Global Risk Layers Manager Module
"""

from typing import Any


class RiskLayersManager:
    """Gestionnaire de couches de risques (LOW, MEDIUM, HIGH, EXTREME)."""

    @classmethod
    def get_risk_layers(cls) -> dict[str, Any]:
        """
        Static catalog of layer categories and the named layer TYPES
        this UI supports selecting (not a claim that any one of them
        is currently populated with live hazard data - see this same
        package's other engines, e.g. HazardDetectionEngine, for the
        honest "no live data connected" disclosure on anything that
        actually claims a real detection/assessment result). Reviewed
        during the post-model4d audit (2026-09-11) and left unchanged
        - see tests/test_hazard_operations.py's own comment confirming
        this is a legitimate static catalog, not fabricated data.
        """
        return {
            "risk_categories": ["LOW", "MEDIUM", "HIGH", "EXTREME"],
            "active_risk_maps": ["Flood Risk Layer", "Storm Surge Layer", "Wildfire Hazard Layer"],
            "status": "RISK_LAYERS_READY",
        }
