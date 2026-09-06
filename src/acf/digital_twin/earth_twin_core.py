"""
Atmospheric Complexity Framework (ACF)

Earth Digital Twin Master Core Module (Phase 1)
"""

from typing import Any

from acf.digital_twin.coupling_engine import CouplingEngine
from acf.digital_twin.earth_state import EarthState
from acf.digital_twin.scenario_engine import DigitalTwinScenarioEngine


class EarthTwinCore:
    """Cœur d'orchestration globale du Jumeau Numérique du système Terre ACF v1.0."""

    def __init__(self):
        self.state = EarthState()

    def run_full_earth_twin_cycle(self) -> dict[str, Any]:
        """Exécute un cycle complet d'assimilation, couplage, simulation et audit planétaire.

        NOTE (correction — unconditional status, found during the
        post-model4d audit, 2026-09-06): this used to always return
        "digital_twin_status": "EARTH_DIGITAL_TWIN_OPERATIONAL" no
        matter what CouplingEngine.compute_couplings() and
        DigitalTwinScenarioEngine.run_scenario() actually returned -
        and both of those already honestly report
        is_real_data=False (coupling_status=
        "NOT_COMPUTED_NO_EARTH_SYSTEM_STATE_CONNECTED", scenario
        status="NOT_SIMULATED_NO_CLIMATE_MODEL_CONNECTED"), since
        neither is wired to any real Earth-system state or climate
        model here. Claiming the twin cycle is "OPERATIONAL" while
        its own two constituent sub-results openly say they were not
        computed is exactly the aggregator-overclaim pattern already
        fixed elsewhere in this audit. The status now genuinely
        reflects whether every sub-component reported real data.
        """
        couplings = CouplingEngine.compute_couplings()
        scenarios = DigitalTwinScenarioEngine.run_scenario("SSP2-4.5")

        is_real_data = bool(couplings.get("is_real_data")) and bool(scenarios.get("is_real_data"))
        digital_twin_status = (
            "EARTH_DIGITAL_TWIN_OPERATIONAL"
            if is_real_data
            else "NOT_OPERATIONAL_COUPLING_AND_SCENARIO_ENGINES_NOT_CONNECTED"
        )

        return {
            "earth_state": self.state.get_state_vector_summary(),
            "couplings": couplings,
            "scenario_projections": scenarios,
            "digital_twin_status": digital_twin_status,
            "is_real_data": is_real_data,
        }
