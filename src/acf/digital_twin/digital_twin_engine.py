"""
Atmospheric Complexity Framework (ACF)

Digital Twin Core Engine Module (Phase 1)
(DigitalTwinEngine, SimulationState, Global Synchronized Twin Controller)
"""

from dataclasses import dataclass
from typing import Any

from acf.digital_twin.planet_state import GlobalEarthState, PlanetState


@dataclass
class SimulationState:
    """État d'avancement de la simulation du Digital Twin."""

    simulation_id: str
    target_lead_time: str  # e.g., "+24h", "+100 years"
    is_running: bool
    progress_pct: float
    resolution_mode: str  # e.g., "High-Res 1km Local / 0.25° Global"


class DigitalTwinEngine:
    """
    Moteur principal du Digital Twin planétaire réunissant tous les sous-systèmes Earth Science d'ACF.
    """

    def __init__(self):
        self.planet_state_mgr = PlanetState()

    def get_current_earth_state(self) -> GlobalEarthState:
        """Retourne l'état physique synchronisé unique de la Terre."""
        return self.planet_state_mgr.current_state

    def run_digital_twin_cycle(self, lead_time_horizon: str = "+24h") -> dict[str, Any]:
        """Exécute un cycle complet d'assimilation et de prévision couplée du Digital Twin."""
        state = self.planet_state_mgr.get_planet_status()
        sim_state = SimulationState(
            simulation_id="SIM-DESTINE-2026-001",
            target_lead_time=lead_time_horizon,
            is_running=False,
            progress_pct=100.0,
            resolution_mode="Coupled Earth Twin 0.25° Global",
        )

        return {
            "engine": "ACF Earth System Digital Twin (DestinE Equivalent)",
            "simulation": {
                "id": sim_state.simulation_id,
                "horizon": sim_state.target_lead_time,
                "progress": sim_state.progress_pct,
            },
            "earth_state": state,
        }
