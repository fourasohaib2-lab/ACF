"""
Atmospheric Complexity Framework (ACF)

Global Scientific Capability Registry Module (Phase 3)
(ScientificCapabilityRegistry categorizing Forecast, Simulation, Observation, AI, Digital Twin, Geoengineering)
"""

from typing import Dict, List


CAPABILITIES: Dict[str, List[str]] = {
    "Forecast": ["NWP Ensemble (IFS, AROME, ICON)", "Neural AI Forecast (GraphCast, FourCastNet, Pangu)"],
    "Simulation": ["2D/3D/4D Physics Engines", "Coastal Tsunami Propagation", "Mogi Volcanic Surface Uplift"],
    "Observation": ["WIGOS SYNOP/TEMP Data Ingestion", "Satellite RGB / Radiances", "Dual-Pol Radar Reflectivity"],
    "Assimilation": ["4D-Var Data Assimilation", "EnKF (Ensemble Kalman Filter)"],
    "Visualization": ["2D/3D/4D Photorealistic Renderers", "Mermaid Diagram Engine", "Planetary Globe Overlay"],
    "AI": ["Physics-Informed Neural Networks", "Graph Neural Networks", "Automated Reasoning Chain"],
    "DecisionSupport": ["Operational Evacuation Max-Flow Solver", "Flight Level Safety Rerouting"],
    "DigitalTwin": ["Global Earth State Vector Synchronizer", "Multi-Hazard Cascade Risk Engine"],
    "SpaceWeather": ["OVATION Prime Auroral Oval", "WSA-ENLIL Solar Wind & CME Propagation"],
    "PlanetaryDefense": ["Near-Earth Object (NEO/PHA) Orbit Solver", "Cosmic Impact Shockwave Simulator"],
    "Climate": ["CMIP6 / SSP Scenarios Projection", "ENSO / NAO Teleconnection Diagnostics"],
    "Geoengineering": ["9 Planetary Boundaries Monitor", "Stratospheric Aerosol Injection (SAI) Simulator"],
    "KnowledgeGraph": ["Master Knowledge Graph Inferencer", "Peer-Reviewed Literature Traceability"],
}


class ScientificCapabilityRegistry:
    """Registre interrogeable des capacités scientifiques d'ACF."""

    @classmethod
    def list_categories(cls) -> List[str]:
        return list(CAPABILITIES.keys())

    @classmethod
    def get_capabilities(cls, category: str) -> List[str]:
        for cat, caps in CAPABILITIES.items():
            if cat.lower() == category.lower():
                return caps
        return []
