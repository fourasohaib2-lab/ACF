"""
Atmospheric Complexity Framework (ACF)

Earth Digital Twin Master Core Module (Phase 1)
"""

from typing import Any, Dict
from acf.digital_twin.earth_state import EarthState
from acf.digital_twin.coupling_engine import CouplingEngine
from acf.digital_twin.scenario_engine import DigitalTwinScenarioEngine


class EarthTwinCore:
    """Cœur d'orchestration globale du Jumeau Numérique du système Terre ACF v1.0."""

    def __init__(self):
        self.state = EarthState()

    def run_full_earth_twin_cycle(self) -> Dict[str, Any]:
        """Exécute un cycle complet d'assimilation, couplage, simulation et audit planétaire."""
        couplings = CouplingEngine.compute_couplings()
        scenarios = DigitalTwinScenarioEngine.run_scenario("SSP2-4.5")

        return {
            "earth_state": self.state.get_state_vector_summary(),
            "couplings": couplings,
            "scenario_projections": scenarios,
            "digital_twin_status": "EARTH_DIGITAL_TWIN_OPERATIONAL",
        }
