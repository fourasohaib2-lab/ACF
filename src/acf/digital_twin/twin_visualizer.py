"""
Atmospheric Complexity Framework (ACF)

Digital Twin UI Visualizer Module (Phase 9)
(DigitalTwinVisualizer for Present Earth NOW, Future Earth 2030/2050/2100, Alternative Earth modes)
"""

from typing import Any


class DigitalTwinVisualizer:
    """Visualiseur d'interface du Jumeau Numérique (Présent NOW, Futur 2050/2100, Terres Alternatives)."""

    @classmethod
    def get_visualization_modes(cls) -> dict[str, Any]:
        return {
            "modes": [
                {"name": "Present Earth (NOW)", "horizon": "2026", "active_data": "Live Assimilation Stream"},
                {"name": "Future Earth (2050)", "horizon": "2050", "active_data": "CMIP6 Projection Mesh"},
                {"name": "Future Earth (2100)", "horizon": "2100", "active_data": "CMIP6 End-of-Century Mesh"},
                {
                    "name": "Alternative Earth (Net-Zero)",
                    "horizon": "2050",
                    "active_data": "SSP1-1.9 Decarbonization Scenario",
                },
                {
                    "name": "Alternative Earth (Geoengineering)",
                    "horizon": "2050",
                    "active_data": "SAI Aerosol Injection Scenario",
                },
            ],
            "status": "VISUALIZER_READY",
        }
