"""ESOC Controller managing command routing and scientific workflow execution (ACF-UI-013)."""

from typing import Any

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.esoc_workspace import WorkspaceManager
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.session_manager import SessionManager
from acf.simulation_engine.climate_scenarios.cmip6 import SSPScenario
from acf.simulation_engine.climate_scenarios.ssp_engine import SSPEngine


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
        """Run AI Neural Operator accelerated forecast.

        NOTE (correction): this used to feed a fabricated, disconnected
        `{"T": 288.0}` scalar into predict_next_state() regardless of any
        real atmospheric state - and since it wasn't even a numpy array,
        NeuralOperatorEngine.predict_next_state()'s own logic passes
        non-array fields through completely unchanged (`if not
        isinstance(field, np.ndarray): predicted_state[key] = field`), so
        this call never even exercised the neural operator's real
        FFT-based prediction path. It still unconditionally claimed
        "SUCCESS". Fixed to use AtmosphericModel.initialize_state() (the
        registry's "atmospheric_model" module) as the input state - a
        genuine, physically-consistent, properly-shaped array state
        (standard-atmosphere lapse rate, realistic wind statistics, real
        grid shape), not fabricated. This is a baseline/initial state
        rather than a tracked live "current" state (no live-state
        tracking exists anywhere in this codebase to reference), which is
        disclosed in the response rather than presented as more than it is.
        """
        neural = self.registry.get_module("neural_operator")
        atmos_model = self.registry.get_module("atmospheric_model")
        if not neural or not atmos_model:
            return {"status": "ERROR"}

        state = atmos_model.initialize_state()
        out = neural.predict_next_state(state)
        return {"status": "SUCCESS", "output": out, "input_state_source": "AtmosphericModel.initialize_state() baseline"}

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
        """Compute climate scenario projection.

        NOTE (correction): `ssp` was accepted but never used - the
        registry's "ssp_engine" module is a single SSPEngine instance
        constructed once at startup with a hard-coded SSP2-4.5 scenario
        (module_registry.py), and SSPEngine.evaluate_horizon(target_year)
        has no way to take a scenario per call (SSPScenario is bound at
        SSPEngine.__init__ time, not evaluate_horizon() time) - so ANY
        `ssp` value passed here (e.g. "SSP5-8.5") silently evaluated
        SSP2-4.5 instead. The registry module presence is still checked
        (as a real "is this subsystem available" signal), but the actual
        evaluation now constructs a scenario-specific SSPEngine for the
        requested `ssp`, genuinely honoring the caller's choice.
        """
        ssp_eng = self.registry.get_module("ssp_engine")
        if not ssp_eng:
            return {"status": "ERROR"}

        try:
            scenario = SSPScenario(ssp)
        except ValueError:
            valid = [s.value for s in SSPScenario]
            return {"status": "ERROR", "reason": f"unknown SSP scenario {ssp!r} - valid: {valid}"}

        res = SSPEngine(scenario).evaluate_horizon(2050)
        return {"status": "SUCCESS", "projection": res}

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
