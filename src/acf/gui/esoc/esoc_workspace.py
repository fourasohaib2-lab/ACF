"""Workspace mode management and configuration for ESOC (ACF-UI-011)."""

from enum import Enum
from typing import Dict, Any, List


class WorkspaceMode(Enum):
    """Operational Workspace Modes tailored for user roles."""

    METEOROLOGIST = "Meteorologist"
    RESEARCH = "Research"
    CLIMATE = "Climate"
    HYDROLOGY = "Hydrology"
    OCEANOGRAPHY = "Oceanography"
    EMERGENCY = "Emergency"
    GOVERNMENT = "Government"
    AI_SCIENTIST = "AI Scientist"
    EDUCATION = "Education"
    ADMINISTRATOR = "Administrator"


class WorkspaceManager:
    """Manages active workspace mode, view configurations, and panel presets."""

    def __init__(self, initial_mode: WorkspaceMode = WorkspaceMode.METEOROLOGIST) -> None:
        self.current_mode = initial_mode

    def set_mode(self, mode: WorkspaceMode) -> Dict[str, Any]:
        """Switch workspace operational mode and return view layout profile.

        Args:
            mode (WorkspaceMode): Target operational mode.

        Returns:
            Dict[str, Any]: Mode configuration profile dictionary.
        """
        self.current_mode = mode
        return self.get_current_profile()

    def get_current_profile(self) -> Dict[str, Any]:
        """Return panel visibility, active tools, and focus map layers for current mode."""
        profiles = {
            WorkspaceMode.METEOROLOGIST: {
                "primary_panel": "earth_monitoring",
                "visible_panels": [
                    "earth_monitoring",
                    "simulation",
                    "hazards",
                    "ai_forecast",
                    "data_assimilation",
                ],
                "active_map_layers": [
                    "Satellite",
                    "Radar",
                    "Surface_SYNOP",
                    "Wind_Vectors",
                    "Pressure_Isobars",
                ],
                "description": "Operational NWP and real-time weather forecasting workbench.",
            },
            WorkspaceMode.RESEARCH: {
                "primary_panel": "earth_physics",
                "visible_panels": [
                    "earth_physics",
                    "simulation",
                    "verification",
                    "hpc",
                    "system",
                ],
                "active_map_layers": [
                    "Vorticity",
                    "Streamlines",
                    "Radiation_Budget",
                    "Spectral_Waves",
                ],
                "description": "Earth physics equations, spectral solver, and microphysics research.",
            },
            WorkspaceMode.CLIMATE: {
                "primary_panel": "climate",
                "visible_panels": [
                    "climate",
                    "digital_twin",
                    "earth_physics",
                    "verification",
                ],
                "active_map_layers": [
                    "Temperature_Anomalies",
                    "Sea_Level_Rise",
                    "Sea_Ice_Extent",
                    "Carbon_Flux",
                ],
                "description": "CMIP6/SSP multi-century climate projections and scenario laboratory.",
            },
            WorkspaceMode.HYDROLOGY: {
                "primary_panel": "hazards",
                "visible_panels": [
                    "hazards",
                    "earth_monitoring",
                    "simulation",
                    "earth_physics",
                ],
                "active_map_layers": [
                    "Precipitation_QPE",
                    "Soil_Moisture",
                    "River_Basins",
                    "Inundation_Depth",
                ],
                "description": "Hydrological runoff, river routing, and flash flood forecasting.",
            },
            WorkspaceMode.OCEANOGRAPHY: {
                "primary_panel": "earth_physics",
                "visible_panels": [
                    "earth_physics",
                    "earth_monitoring",
                    "simulation",
                    "digital_twin",
                ],
                "active_map_layers": [
                    "SST",
                    "Ocean_Currents",
                    "Salinity",
                    "ARGO_Floats",
                    "Significant_Wave_Height",
                ],
                "description": "3D hydrodynamic ocean circulation, AMOC, and spectral wave modeling.",
            },
            WorkspaceMode.EMERGENCY: {
                "primary_panel": "hazards",
                "visible_panels": [
                    "hazards",
                    "ai_forecast",
                    "earth_monitoring",
                    "system",
                ],
                "active_map_layers": [
                    "Alert_Zones",
                    "Cyclone_Track",
                    "Wildfire_Perimeters",
                    "Population_Density",
                    "Evacuation_Routes",
                ],
                "description": "Hazard operations, population exposure, and civil emergency response.",
            },
            WorkspaceMode.GOVERNMENT: {
                "primary_panel": "digital_twin",
                "visible_panels": [
                    "digital_twin",
                    "hazards",
                    "climate",
                    "ai_forecast",
                ],
                "active_map_layers": [
                    "Planetary_Boundaries",
                    "Risk_Indices",
                    "Air_Quality_Index",
                    "Economic_Exposure",
                ],
                "description": "Executive policy indicators, planetary resilience, and risk briefings.",
            },
            WorkspaceMode.AI_SCIENTIST: {
                "primary_panel": "ai_forecast",
                "visible_panels": [
                    "ai_forecast",
                    "simulation",
                    "verification",
                    "hpc",
                ],
                "active_map_layers": [
                    "FNO_Predictions",
                    "Neural_Attention_Maps",
                    "PINN_Corrections",
                    "Model_Spread",
                ],
                "description": "Fourier Neural Operators, GNN surrogates, and AI forecast intelligence.",
            },
            WorkspaceMode.EDUCATION: {
                "primary_panel": "earth_physics",
                "visible_panels": [
                    "earth_physics",
                    "climate",
                    "earth_monitoring",
                ],
                "active_map_layers": [
                    "Global_Temperature",
                    "Wind_General_Circulation",
                    "Sunlight_Radiation",
                ],
                "description": "Interactive Earth physics demonstrations and educational visualizations.",
            },
            WorkspaceMode.ADMINISTRATOR: {
                "primary_panel": "hpc",
                "visible_panels": ["hpc", "system", "data_assimilation", "verification"],
                "active_map_layers": [
                    "MPI_Rank_Domains",
                    "Observation_Data_Density",
                    "System_Cluster_Health",
                ],
                "description": "HPC cluster management, MPI topology, GPU memory, and logs.",
            },
        }

        profile = profiles.get(self.current_mode, profiles[WorkspaceMode.METEOROLOGIST])
        profile["mode_name"] = self.current_mode.value
        return profile

    def list_modes(self) -> List[str]:
        """List human-readable names of all available workspace modes."""
        return [m.value for m in WorkspaceMode]
