"""Unified Earth System Operations Center (ESOC) Main Window (ACF-UI-011)."""

from typing import Any

from PySide6.QtWidgets import QMainWindow, QMessageBox

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.esoc_controller import ESOCController
from acf.gui.esoc.esoc_layout import ESOCLayout
from acf.gui.esoc.esoc_statusbar import ESOCStatusBar
from acf.gui.esoc.esoc_toolbar import ESOCToolbar
from acf.gui.esoc.esoc_workspace import WorkspaceManager, WorkspaceMode
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import PanelManager
from acf.gui.esoc.session_manager import SessionManager


class ESOCWindow(QMainWindow):
    """Unified Earth System Operations Center (ESOC) Main Window.

    Provides a single unified command cockpit controlling all 45+ ACF scientific subsystems.
    """

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Unified Earth System Operations Center (ESOC) v1.0 — Atmospheric Complexity Framework")
        self.resize(1600, 1000)

        # 1. Subsystem Registry & Dispatchers
        self.registry = ModuleRegistry()
        self.dispatcher = CommandDispatcher()
        self.session_manager = SessionManager()
        self.workspace_manager = WorkspaceManager(WorkspaceMode.METEOROLOGIST)

        # 2. Controllers & Managers
        self.panel_manager = PanelManager(self.registry, self.dispatcher)
        self.controller = ESOCController(self.registry, self.dispatcher, self.workspace_manager, self.session_manager)

        # 3. Layout & UI Components
        self.layout_manager = ESOCLayout(self, self.panel_manager)
        self.toolbar = ESOCToolbar(
            on_action_callback=self._handle_toolbar_action,
            on_mode_callback=self._handle_mode_changed,
        )
        self.addToolBar(self.toolbar)

        self.status_bar = ESOCStatusBar()
        self.setStatusBar(self.status_bar)

        # 4. Connect Signals & Select Default Profile
        self._setup_connections()
        self._apply_mode(WorkspaceMode.METEOROLOGIST.value)

    def _setup_connections(self) -> None:
        """Connect UI signals to status bar and layout events."""
        self.dispatcher.hazard_alert_triggered.connect(self._on_hazard_alert)
        self.dispatcher.simulation_step_completed.connect(self._on_sim_step)

    def _apply_mode(self, mode_name: str) -> None:
        """Apply operational workspace mode layout profile."""
        for m in WorkspaceMode:
            if m.value.lower() == mode_name.lower():
                profile = self.workspace_manager.set_mode(m)
                self.layout_manager.apply_workspace_profile(profile)
                self.status_bar.update_metrics(workspace_mode=m.value)
                self.dispatcher.workspace_mode_changed.emit(m.value)
                break

    def _handle_toolbar_action(self, cmd: str) -> None:
        """Process toolbar button clicks."""
        if cmd == "trigger_sim":
            self.dispatcher.dispatch("run_simulation")
        elif cmd == "trigger_da":
            self.dispatcher.dispatch("run_assimilation")
        elif cmd == "trigger_twin":
            self.dispatcher.dispatch("load_digital_twin")
        elif cmd == "trigger_hazards":
            self.dispatcher.dispatch("assess_hazards")
        elif cmd == "trigger_climate":
            self.dispatcher.dispatch("run_climate_projection")
        elif cmd == "trigger_verif":
            self.dispatcher.dispatch("verify_forecast")
        elif cmd == "open_help":
            QMessageBox.information(
                self,
                "ESOC Help",
                "Unified Earth System Operations Center (ESOC v1.0)\n\n"
                "Controls all Earth System Physics, Numerical Simulation, AI Intelligence, "
                "Data Assimilation, Hazards, Climate, Verification, and HPC Layers.",
            )

    def _handle_mode_changed(self, mode_str: str) -> None:
        """Switch workspace operational mode."""
        self._apply_mode(mode_str)

    def _on_hazard_alert(self, level: str, info: dict[str, Any]) -> None:
        """Handle incoming hazard alert signal."""
        self.dispatcher.log_message_emitted.emit(
            "WARNING", f"HAZARD ALERT [{level}]: {info.get('threat', 'Unknown Threat')}"
        )

    def _on_sim_step(self, info: dict[str, Any]) -> None:
        """Handle simulation step completed signal."""
        step = info.get("step", 0)
        self.status_bar.update_metrics(sim_time=f"t+{step:03d}h")

    @classmethod
    def get_esoc_metadata(cls) -> dict[str, Any]:
        """
        Return operational platform metadata dictionary.

        NOTE (correction): platform_name/version/operational_modes/
        dock_panels are static platform-descriptor constants (kept
        as-is), but "connected_subsystems: 45" and
        "status: OPERATIONAL_READY" used to claim a live, verified
        operational state with 0 parameters and no real subsystem-
        connectivity check performed (the exact same fabricated "45"
        count also appeared in release.health_check.ProductionHealthCheck,
        fixed earlier this session - neither was ever real). Not
        fabricated.
        """
        return {
            "platform_name": "Unified Earth System Operations Center (ESOC)",
            "version": "1.0",
            "connected_subsystems": None,
            "operational_modes": 10,
            "dock_panels": 11,
            "status": "NOT_VERIFIED_NO_SUBSYSTEM_CONNECTIVITY_CHECK_PERFORMED",
            "is_real_data": False,
        }
