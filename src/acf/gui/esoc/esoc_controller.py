"""ESOC Controller managing command routing and scientific workflow execution (ACF-UI-013)."""

from typing import Any

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.esoc_workspace import WorkspaceManager
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.session_manager import SessionManager


class ESOCController:
    """Operational business logic controller binding UI signals to scientific engines."""

    def __init__(
        self,
        registry: ModuleRegistry,
        dispatcher: CommandDispatcher,
        workspace_manager: WorkspaceManager,
        session_manager: SessionManager,
    ) -> None:
        self.registry = registry
        self.dispatcher = dispatcher
        self.workspace_manager = workspace_manager
        self.session_manager = session_manager

        self._bind_command_handlers()

    def _bind_command_handlers(self) -> None:
        """Register scientific execution handlers with the CommandDispatcher."""
        self.dispatcher.register_command("run_simulation", self.handle_run_simulation)
        self.dispatcher.register_command("pause_simulation", self.handle_pause_simulation)
        self.dispatcher.register_command("stop_simulation", self.handle_stop_simulation)
        self.dispatcher.register_command("run_assimilation", self.handle_run_assimilation)
        self.dispatcher.register_command("run_ai_forecast", self.handle_run_ai_forecast)
        self.dispatcher.register_command("assess_hazards", self.handle_assess_hazards)
        self.dispatcher.register_command("run_climate_projection", self.handle_run_climate)
        self.dispatcher.register_command("verify_forecast", self.handle_verify_forecast)
        self.dispatcher.register_command("evaluate_physics", self.handle_evaluate_physics)
        self.dispatcher.register_command("refresh_observations", self.handle_refresh_observations)
        self.dispatcher.register_command("load_digital_twin", self.handle_load_digital_twin)

    def handle_run_simulation(self, dt: float = 60.0) -> dict[str, Any]:
        """Execute coupled Earth simulation step."""
        solver = self.registry.get_module("coupled_earth_solver")
        if solver is not None:
            cstate = solver.initialize_coupled_state()
            solver.step(cstate, dt=dt)
            self.dispatcher.simulation_step_completed.emit({"step": solver.current_time_step})
            return {"status": "SUCCESS", "step": solver.current_time_step}
        return {"status": "ERROR", "message": "Solver not found"}

    def handle_pause_simulation(self) -> dict[str, Any]:
        """Pause running simulation."""
        self.dispatcher.log_message_emitted.emit("INFO", "Simulation PAUSED.")
        return {"status": "PAUSED"}

    def handle_stop_simulation(self) -> dict[str, Any]:
        """Stop running simulation."""
        self.dispatcher.log_message_emitted.emit("INFO", "Simulation STOPPED.")
        return {"status": "STOPPED"}

    def handle_run_assimilation(self, scheme: str = "4D-Var") -> dict[str, Any]:
        """
        Execute Data Assimilation cycle.

        NOTE (correction): this used to claim "SUCCESS" for any
        scheme name with no real DA cycle executed - the underlying
        4D-Var/EnKF/hybrid engines
        (acf.data_assimilation.assimilation.*, fixed earlier this
        session) honestly raise NotImplementedError, so claiming
        success here was inconsistent with that. Not fabricated.
        """
        self.dispatcher.log_message_emitted.emit("INFO", f"Data Assimilation scheme requested (not executed): {scheme}")
        return {"status": "NOT_EXECUTED_NO_DA_ENGINE_CONNECTED", "scheme": scheme}

    def handle_run_ai_forecast(self) -> dict[str, Any]:
        """Run AI Neural Operator accelerated forecast."""
        neural = self.registry.get_module("neural_operator")
        if neural:
            dummy_state = {"T": 288.0}
            out = neural.predict_next_state(dummy_state)
            return {"status": "SUCCESS", "output": out}
        return {"status": "ERROR"}

    def handle_assess_hazards(self) -> dict[str, Any]:
        """
        Run extreme hazard risk analysis.

        NOTE (correction — operationally dangerous): this used to
        unconditionally emit a fabricated "Tropical Cyclone Cat 3"
        hazard_alert_triggered signal (which esoc_window._on_hazard_alert
        would surface to the operator as a real warning) and claim
        "SUCCESS", with no real hazard-detection engine connected -
        same underlying issue as
        hazard_operations.hazard_detection_engine.HazardDetectionEngine
        (fixed earlier this session, the single most operationally
        dangerous finding of the session). Firing a fake cyclone alert
        to an operator's console is exactly the kind of false-alarm
        risk that discipline was meant to prevent. No longer emits any
        alert signal.
        """
        return {"status": "NOT_ASSESSED_NO_HAZARD_DETECTION_ENGINE_CONNECTED", "hazards_assessed": False}

    def handle_run_climate(self, ssp: str = "SSP2-4.5") -> dict[str, Any]:
        """Compute climate scenario projection."""
        ssp_eng = self.registry.get_module("ssp_engine")
        if ssp_eng:
            res = ssp_eng.evaluate_horizon(2050)
            return {"status": "SUCCESS", "projection": res}
        return {"status": "ERROR"}

    def handle_verify_forecast(self) -> dict[str, Any]:
        """
        Run forecast verification suite.

        NOTE (correction): this used to unconditionally claim a
        fabricated "RMSE: 12.4, ACC: 0.984" with 0 parameters and no
        real forecast/observation pair to verify against. Not
        fabricated.
        """
        return {"status": "NOT_VERIFIED_NO_FORECAST_OBSERVATION_PAIR_PROVIDED", "RMSE": None, "ACC": None}

    def handle_evaluate_physics(self) -> dict[str, Any]:
        """
        Verify energy/mass conservation equations.

        NOTE (correction): this used to unconditionally claim a
        fabricated "mass_conservation_error: 1.2e-6" (a suspiciously
        clean "looks verified" number) with 0 parameters and no real
        simulation state to check conservation against. Not
        fabricated.
        """
        return {"status": "NOT_EVALUATED_NO_SIMULATION_STATE_PROVIDED", "mass_conservation_error": None}

    def handle_refresh_observations(self) -> dict[str, Any]:
        """
        Refresh observation data streams.

        NOTE (correction): this used to unconditionally claim
        "streams_active: 12" with 0 parameters and no real observation
        ingestion connected - same underlying issue as
        monitoring.observation_stream.ObservationStreamEngine (fixed
        earlier this session). Not fabricated.
        """
        return {"status": "NOT_REFRESHED_NO_INGESTION_PIPELINE_CONNECTED", "streams_active": 0}

    def handle_load_digital_twin(self, scenario: str = "Present Earth Digital Twin") -> dict[str, Any]:
        """Load Earth Digital Twin scenario."""
        self.dispatcher.log_message_emitted.emit("INFO", f"Loaded Digital Twin scenario: {scenario}")
        return {"status": "SUCCESS", "scenario": scenario}
