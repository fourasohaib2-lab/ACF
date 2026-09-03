"""Unified Earth System Operations Center (ESOC) Main Window (ACF-UI-011)."""

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from acf.awci.spatial_field import compute_real_complexity_field
from acf.gui_screen_utils import fit_window_to_screen
from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.esoc_controller import ESOCController
from acf.gui.esoc.esoc_layout import ESOCLayout
from acf.gui.esoc.esoc_statusbar import ESOCStatusBar
from acf.gui.esoc.esoc_toolbar import ESOCToolbar
from acf.gui.esoc.esoc_workspace import WorkspaceManager, WorkspaceMode
from acf.gui.esoc.hpc_connection_dialog import HPCConnectionDialog
from acf.gui.esoc.log_viewer_dialog import LogViewerDialog
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import PanelManager
from acf.gui.esoc.session_manager import SessionManager
from acf.gui.esoc.settings_dialog import SettingsDialog

if TYPE_CHECKING:
    from acf.dashboard.window import ClassicDashboardWindow
    from acf.gui.dashboard.acf_general_dashboard_window import ACFGeneralDashboardWindow
    from acf.gui.dashboard.awci_window import AWCIDashboardWindow

logger = logging.getLogger("acf.gui.esoc.esoc_window")


class _AWCIFieldWorkerSignals(QObject):
    """QRunnable itself cannot be a QObject (no signals) - same
    companion-object pattern as acf.gui.dashboard.awci_dashboard's
    _RealFieldWorkerSignals, reused here rather than duplicated."""

    finished = Signal(dict)
    failed = Signal(str)


class _AWCIFieldWorker(QRunnable):
    """Runs compute_real_complexity_field() off the GUI thread, for the
    "🌪️ AWCI Field" toolbar action - explicit user request "ajoute la
    4eme dimension au niveau d'affichage des cartes"."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        self.kwargs = kwargs
        self.signals = _AWCIFieldWorkerSignals()

    def run(self) -> None:
        try:
            result = compute_real_complexity_field(**self.kwargs)
        except Exception as exc:
            logger.exception("Real AWCI field computation failed")
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(result)


class ESOCWindow(QMainWindow):
    """Unified Earth System Operations Center (ESOC) Main Window.

    Provides a single unified command cockpit controlling all 45+ ACF scientific subsystems.
    """

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Unified Earth System Operations Center (ESOC) v1.0 — Atmospheric Complexity Framework")
        # NOTE (correction): was a hardcoded self.resize(1600, 1000) - on any
        # screen smaller than that (laptop panel, remote desktop session) the
        # window opened larger than the display, so its edges/toolbar/status
        # bar ended up off-screen. Clamp to the actual screen's available
        # geometry instead, still using the full 1600x1000 on a big-enough one.
        fit_window_to_screen(self, 1600, 1000)

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

        # Toolbar-driven UI state (real, not fabricated: reflects only what the user
        # actually triggered from this window - a chosen theme, an opened log viewer).
        self._current_theme = "dark"
        self._log_viewer: LogViewerDialog | None = None
        self._classic_dashboard_window: ClassicDashboardWindow | None = None
        self._awci_dashboard_window: AWCIDashboardWindow | None = None
        self._acf_general_dashboard_window: ACFGeneralDashboardWindow | None = None

        # 4. Connect Signals & Select Default Profile
        self._setup_connections()
        self._apply_mode(WorkspaceMode.METEOROLOGIST.value)

    def _setup_connections(self) -> None:
        """Connect UI signals to status bar and layout events."""
        self.dispatcher.hazard_alert_triggered.connect(self._on_hazard_alert)
        self.dispatcher.simulation_step_completed.connect(self._on_sim_step)
        self.dispatcher.hpc_connection_result.connect(self._on_hpc_connection_result)

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
        """Process toolbar button clicks.

        NOTE (correction — improvement pass): 14 of the toolbar's 21 buttons
        (open_dataset, live_stream, connect_hpc, disconnect_hpc, submit_hpc_job,
        cancel_hpc_job, sync_hpc_storage, open_terminal, open_logs, benchmark_hpc,
        trigger_ai, export_data, take_screenshot, open_settings) were entirely
        unhandled here - clicking them silently did nothing (ESOCToolbar always
        calls the callback, and CommandDispatcher.dispatch() only warns into the
        log for a command with no registered handler, which nothing ever surfaced
        to the user). trigger_ai in particular mapped to an already fully working,
        previously-fixed handler (ESOCController.handle_run_ai_forecast) that was
        simply never wired to its own button. Every branch below does something
        real (opens an already-built dialog, switches to the panel tab that
        actually owns that function, performs a genuine local action like a
        screenshot or theme change, or attempts a real HPC connection in the
        background) rather than fabricating a result - see each handler's own
        comment for what it actually does versus what it honestly cannot do yet.
        """
        if cmd == "trigger_sim":
            self._dispatch_and_report("run_simulation")
        elif cmd == "trigger_da":
            self._dispatch_and_report("run_assimilation")
        elif cmd == "trigger_twin":
            self._dispatch_and_report("load_digital_twin")
        elif cmd == "trigger_hazards":
            self._dispatch_and_report("assess_hazards")
        elif cmd == "trigger_climate":
            self._dispatch_and_report("run_climate_projection")
        elif cmd == "trigger_ai":
            self._dispatch_and_report("run_ai_forecast")
        elif cmd == "trigger_forecast":
            # NOTE (correction): this button sent "trigger_forecast" but the only
            # matching branch here checked for "trigger_verif" - a command name no
            # toolbar button has ever actually sent (ESOCToolbar's action list has
            # no "trigger_verif" entry) - so this button did nothing. The closest
            # real registered command is "verify_forecast" (ESOCController.
            # handle_verify_forecast, already honest: reports
            # NOT_VERIFIED_NO_FORECAST_OBSERVATION_PAIR_PROVIDED with no fabricated
            # RMSE/ACC).
            self._dispatch_and_report("verify_forecast")
        elif cmd == "live_stream":
            self._dispatch_and_report("refresh_observations")
        elif cmd == "open_dataset":
            self._open_dataset()
        elif cmd == "connect_hpc":
            self._connect_hpc()
        elif cmd == "disconnect_hpc":
            self._disconnect_hpc()
        elif cmd == "submit_hpc_job":
            self._focus_panel_tab("job_explorer")
        elif cmd == "cancel_hpc_job":
            self._focus_panel_tab("job_explorer")
        elif cmd == "sync_hpc_storage":
            self._focus_panel_tab("storage_monitor")
        elif cmd == "open_terminal":
            self._focus_panel_tab("hpc_terminal")
        elif cmd == "benchmark_hpc":
            self._focus_panel_tab("benchmark_panel")
        elif cmd == "open_logs":
            self._open_log_viewer()
        elif cmd == "export_data":
            self._export_data()
        elif cmd == "take_screenshot":
            self._take_screenshot()
        elif cmd == "open_settings":
            self._open_settings()
        elif cmd == "open_classic_dashboard":
            self._open_classic_dashboard()
        elif cmd == "open_awci_dashboard":
            self._open_awci_dashboard()
        elif cmd == "open_acf_general_dashboard":
            self._open_acf_general_dashboard()
        elif cmd == "show_awci_field_on_map":
            self._show_awci_field_on_map()
        elif cmd == "open_help":
            QMessageBox.information(
                self,
                "ESOC Help",
                "Unified Earth System Operations Center (ESOC v1.0)\n\n"
                "Controls all Earth System Physics, Numerical Simulation, AI Intelligence, "
                "Data Assimilation, Hazards, Climate, Verification, and HPC Layers.",
            )

    def _dispatch_and_report(self, command_name: str, **kwargs: Any) -> None:
        """Dispatch a command and surface its real result in the status bar.

        NOTE (correction): dispatching alone (the previous behaviour for
        trigger_sim/trigger_da/trigger_twin/trigger_hazards/trigger_climate) only
        logged to CommandDispatcher.log_message_emitted, which nothing displayed
        anywhere unless the operator happened to have the log viewer open - so
        clicking these buttons looked exactly like doing nothing. This shows the
        handler's own real returned status (e.g. "SUCCESS", or an honest
        "NOT_EXECUTED_NO_DA_ENGINE_CONNECTED") for a few seconds, whatever it is -
        it does not upgrade or embellish the result.
        """
        result = self.dispatcher.dispatch(command_name, **kwargs)
        status = result.get("status") if isinstance(result, dict) else result
        self.statusBar().showMessage(f"{command_name}: {status}", 5000)

    def _focus_panel_tab(self, panel_key: str) -> None:
        """Raise the bottom-dock tab that actually owns a given operational function.

        Genuine navigation, not a fabricated action: submit/cancel job, storage
        sync, the HPC terminal, and benchmarking each already have a real,
        working operational panel - this just takes the operator there instead
        of the toolbar button silently doing nothing.
        """
        panel = self.panel_manager.get_panel(panel_key)
        tabs = self.layout_manager.bottom_tabs
        if panel is not None:
            idx = tabs.indexOf(panel)
            if idx >= 0:
                tabs.setCurrentIndex(idx)
                self.dock_bottom_raise()
                return
        self.dispatcher.log_message_emitted.emit("WARNING", f"No panel registered for {panel_key!r}")

    def dock_bottom_raise(self) -> None:
        """Ensure the bottom operational-panels dock is visible and focused."""
        self.layout_manager.dock_bottom.setVisible(True)
        self.layout_manager.dock_bottom.raise_()

    def _open_dataset(self) -> None:
        """Let the operator pick a dataset file and reflect the real selection in the
        status bar. Honest about scope: no ingestion/parsing pipeline is wired to
        this toolbar action, so the file is not read - only genuinely selected.

        NOTE (correction - real user-reported bug: "je vois les dossiers mais
        aucun fichier ne s'affiche" / folders show but no files do): the filter
        string used to list "All Supported (*.nc *.grib *.grib2 *.zarr *.csv
        *.geojson)" FIRST, which Qt preselects as the active filter - so any
        file whose extension was not in that short list (real AROME/ALADIN/
        ARPEGE HPC output is commonly plain unnumbered GRIB with no ".grib2"
        suffix, Meteo-France's native ".fa" format, ".grb"/".grib1", ".h5"/
        ".hdf5"/".nc4", or genuinely no extension at all) was silently hidden
        by the OS file dialog - directories are always shown regardless of
        filter, which is exactly why folders were visible but their files
        were not. "All Files (*)" is now the default filter (nothing hidden
        unless the operator deliberately narrows it), and the named filter
        covers more of the real formats this project already reads elsewhere
        (see simulation_engine/output/netcdf_writer.py, zarr_writer.py).
        """
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Dataset",
            os.getcwd(),
            "All Files (*);;Meteorological Data "
            "(*.nc *.nc4 *.grib *.grib1 *.grib2 *.grb *.grb1 *.grb2 *.fa *.zarr *.h5 *.hdf5 *.csv *.geojson)",
        )
        if not path:
            return
        self.status_bar.update_metrics(dataset_name=Path(path).name)
        self.dispatcher.log_message_emitted.emit(
            "INFO", f"Dataset file selected: {path} (no ingestion pipeline connected to this action yet)"
        )

    def _connect_hpc(self) -> None:
        """Open the real HPC connection wizard, then genuinely attempt the connection
        (over Paramiko SSH, via acf.hpc_connector.HPCConnectionManager) in a background
        thread so the UI never blocks.

        NOTE: HPCConnectionManager.connect() itself always returns True once its
        11-step workflow completes without raising - by design, it also supports
        a local/offline development mode with no real cluster reachable (see its
        own NOTE and ssh_connector.py's - this is deliberate, not a bug, and is
        covered by tests/test_hpc_connector.py::test_hpc_connection_manager_
        fennec_workflow asserting exactly that True in this same kind of offline
        environment). So connect()'s own return value is NOT used here to decide
        what the status bar claims - that would repeat the "workflow succeeded"
        vs "genuinely reached a real machine" conflation this codebase has
        already fixed once at the SSHConnector layer via is_real_connection. The
        status bar only reports "Connected" when is_real_connection is actually
        True (a live Paramiko transport was confirmed); otherwise it honestly
        shows Not Connected even though the local workflow itself "succeeded".
        """
        dialog = HPCConnectionDialog(self)
        if dialog.exec() != HPCConnectionDialog.DialogCode.Accepted:
            return
        config = dialog.get_connection_config()
        # NOTE (correction): only config["profile_name"] used to be forwarded, and it
        # carried the combo box's human-readable LABEL - which never matched any key
        # under cluster_profiles: in config/hpc.yaml, so the profile always resolved
        # to {} and the connector fell back to its hardcoded defaults. Every other
        # field the operator filled in (hostname, username, port, SSH key, password,
        # directories) was discarded outright. The wizard now returns a separate
        # profile_key for the YAML lookup, and the whole dict is passed as overrides.
        profile = config.get("profile_key") or "fennec"
        label = config.get("profile_name", profile)
        hpc = self.registry.get_module("hpc_connector")
        if hpc is None:
            self.dispatcher.log_message_emitted.emit("ERROR", "HPC connector subsystem not available")
            return
        self.dispatcher.log_message_emitted.emit(
            "INFO",
            f"Attempting HPC connection (profile: {label!r} -> key {profile!r}, "
            f"target {config.get('username')}@{config.get('hostname')}:{config.get('port')})...",
        )

        def _do_connect() -> None:
            try:
                try:
                    workflow_ok = hpc.connect(profile, overrides=config)
                except TypeError:
                    # Connector implementation predating the overrides parameter.
                    self.dispatcher.log_message_emitted.emit(
                        "WARNING",
                        "HPC connector does not accept per-connection overrides - "
                        "the wizard's hostname/username/port fields will be ignored.",
                    )
                    workflow_ok = hpc.connect(profile)
            except Exception as exc:  # noqa: BLE001 - must not crash the worker thread
                self.dispatcher.log_message_emitted.emit("ERROR", f"HPC connect({profile!r}) raised: {exc}")
                self.dispatcher.hpc_connection_result.emit(False, profile)
                return
            real_transport = bool(getattr(hpc.ssh_connector, "is_real_connection", False))
            self.dispatcher.log_message_emitted.emit(
                "INFO",
                f"HPC connect({profile!r}): workflow_completed={workflow_ok}, "
                f"real_ssh_transport={real_transport} "
                f"({'genuinely reached a remote host' if real_transport else 'offline/local dev mode - no real cluster reached'})",
            )
            self.dispatcher.hpc_connection_result.emit(real_transport, profile)

        self.dispatcher.run_async(_do_connect)

    def _disconnect_hpc(self) -> None:
        """Genuinely call HPCConnectionManager.disconnect() rather than only resetting
        the status bar label - the real connector is told to tear down its channel."""
        hpc = self.registry.get_module("hpc_connector")
        if hpc is None:
            self.dispatcher.log_message_emitted.emit("ERROR", "HPC connector subsystem not available")
            return
        try:
            hpc.disconnect()
        except Exception as exc:  # noqa: BLE001
            self.dispatcher.log_message_emitted.emit("ERROR", f"HPC disconnect() raised: {exc}")
            return
        self.status_bar.update_metrics(hpc_connected=False)
        self.dispatcher.log_message_emitted.emit("INFO", "HPC connection closed.")

    def _on_hpc_connection_result(self, ok: bool, profile: str) -> None:
        """Reflect the real outcome of a background connect() attempt in the status bar."""
        self.status_bar.update_metrics(hpc_connected=ok)
        self.dispatcher.log_message_emitted.emit(
            "INFO" if ok else "WARNING", f"HPC connect(profile={profile!r}) -> {ok}"
        )

    def _open_log_viewer(self) -> None:
        """Open (or raise) the live session log viewer."""
        if self._log_viewer is None:
            self._log_viewer = LogViewerDialog(self.dispatcher, self)
        self._log_viewer.show()
        self._log_viewer.raise_()
        self._log_viewer.activateWindow()

    def _open_classic_dashboard(self) -> None:
        """Open (or raise) the classic ACF dashboard (acf.dashboard - MapView plus
        Explorer/Charts/Properties/Timeline/Console/Status docks) as its own
        top-level window.

        NOTE: this predates ESOC and was completely unreachable from the running
        application before this action existed - see ClassicDashboardWindow's own
        docstring for why it is a separate window rather than one more ESOC tab
        (its DashboardLayout calls setCentralWidget()/addDockWidget() directly,
        so it wants to own a whole window, unlike the AWCI dashboard which fit
        naturally as a tab).

        The import below is deliberately local: acf.dashboard.window imports
        acf.dashboard.layout, which imports acf.gui.widgets.map_view - importing
        anything under acf.gui at all triggers acf/gui/__init__.py, which eagerly
        imports THIS module (ESOCWindow) for its own __all__ - a module-level
        import here would be a circular import (confirmed: raises ImportError on
        a partially-initialized module). Deferring it until the button is
        actually clicked breaks the cycle.
        """
        from acf.dashboard.window import ClassicDashboardWindow

        if self._classic_dashboard_window is None:
            self._classic_dashboard_window = ClassicDashboardWindow(self)
        self._classic_dashboard_window.show()
        self._classic_dashboard_window.raise_()
        self._classic_dashboard_window.activateWindow()

    def _open_awci_dashboard(self) -> None:
        """Open (or raise) the AWCI dashboard as its own top-level window.

        The AWCIDashboard widget was already reachable twice, but badly: as the
        28th and last tab of the bottom dock (where it is clipped - it declares a
        1200x900 minimum and lives in a QScrollArea, see AWCIDashboardPanel), and
        as a button inside the Classic View window, two clicks away. This action
        opens acf.gui.dashboard.awci_window.AWCIDashboardWindow (1500x950)
        directly, reusing the exact pattern of _open_classic_dashboard() above.

        The import is deliberately local for the same reason as there:
        acf.gui.dashboard pulls in acf.gui, whose __init__ eagerly imports THIS
        module, so a module-level import would be circular.
        """
        from acf.gui.dashboard.awci_window import AWCIDashboardWindow

        if self._awci_dashboard_window is None:
            self._awci_dashboard_window = AWCIDashboardWindow(self)
        self._awci_dashboard_window.show()
        self._awci_dashboard_window.raise_()
        self._awci_dashboard_window.activateWindow()
        self.dispatcher.log_message_emitted.emit(
            "INFO",
            "AWCI dashboard opened. Meteorological INPUT fields are synthetic "
            "(see acf.gui.dashboard.awci_synthetic_field); the AWCI scores themselves "
            "are real AWCICalculator output over those inputs.",
        )

    def _open_acf_general_dashboard(self) -> None:
        """Open (or raise) the general ACF research dashboard as its own
        top-level window - docs/ACF_MASTER_PROMPT.md sections 27-29,
        docs/reference/acf_dashboard_reference.jpg. Distinct from the
        AWCI-only dashboard above (_open_awci_dashboard); same
        open-or-raise pattern, same reason for a local import (circular
        via acf.gui.dashboard -> acf.gui.__init__ -> this module).
        """
        from acf.gui.dashboard.acf_general_dashboard_window import ACFGeneralDashboardWindow

        if self._acf_general_dashboard_window is None:
            self._acf_general_dashboard_window = ACFGeneralDashboardWindow(self)
        self._acf_general_dashboard_window.show()
        self._acf_general_dashboard_window.raise_()
        self._acf_general_dashboard_window.activateWindow()
        self.dispatcher.log_message_emitted.emit(
            "INFO",
            "ACF general dashboard opened - computing real CoupledEarthSolver "
            "evolution off-thread (acf.awci.temporal_field.compute_real_complexity_evolution).",
        )

    def _show_awci_field_on_map(self) -> None:
        """Compute a real acf.awci.spatial_field.compute_real_complexity_field()
        result (off the GUI thread, same QRunnable+Signal pattern as
        acf.gui.dashboard.awci_dashboard's Real Physics mode) and overlay
        it on THIS window's own central map (acf.gui.map.map_canvas.
        MapCanvas, via ViewManager) - explicit user request "ajoute la
        4eme dimension au niveau d'affichage des cartes". Before this,
        ESOC's central map never showed any real AWCI/CAPE/CIN data at
        all - only the separate AWCI dashboard window did.

        compute_convective_energy=True also surfaces real per-point
        CAPE/CIN (acf.awci.convective_energy) - closing a real,
        previously-found gap: that machinery existed and was tested,
        but no GUI widget anywhere ever visualized it.
        """
        self.dispatcher.log_message_emitted.emit(
            "INFO",
            "Computing real AWCI complexity field (CoupledEarthSolver, ARPEGE grid, "
            "including CAPE/CIN)… this takes a few seconds.",
        )
        self.status_bar.showMessage("🌪️ Computing real AWCI field…")
        worker = _AWCIFieldWorker(
            model="ARPEGE", n_lat=24, n_lon=36, n_levels=6, steps=6, compute_convective_energy=True
        )
        # NOTE (found while verifying this end-to-end, not hypothetical):
        # connecting to a bare lambda here (instead of a genuine bound
        # method, like awci_dashboard.py's own _RealFieldWorker
        # consumers do) meant PySide6's Auto connection type had no
        # receiver QObject to determine safe cross-thread queuing for -
        # the signal, emitted from the worker thread, never actually
        # invoked the lambda at all (confirmed: it silently never ran,
        # not even on the wrong thread). Bound methods on self (a
        # QObject) resolve this correctly, matching the proven pattern.
        worker.signals.finished.connect(self._on_awci_field_ready)
        worker.signals.failed.connect(self._on_awci_field_failed)
        QThreadPool.globalInstance().start(worker)

    def _on_awci_field_ready(self, result: dict[str, Any]) -> None:
        map_canvas = self.layout_manager.view_manager.map_canvas
        map_canvas.set_awci_field(result["lons"], result["lats"], result["awci_field"], label="REAL AWCI")
        self.status_bar.showMessage("🌪️ Real AWCI field displayed on map (ARPEGE, CAPE/CIN included).", 5000)
        self.dispatcher.log_message_emitted.emit(
            "INFO", "Real AWCI complexity field displayed on the central map."
        )

    def _on_awci_field_failed(self, message: str) -> None:
        self.status_bar.showMessage(f"⚠ Real AWCI field computation failed: {message}", 5000)
        self.dispatcher.log_message_emitted.emit("ERROR", f"Real AWCI field computation failed: {message}")

    def _open_settings(self) -> None:
        """Open the settings dialog; apply the chosen theme immediately if changed."""
        dialog = SettingsDialog(self._current_theme, self)
        dialog.exec()
        self._current_theme = dialog.combo_theme.currentText()

    def _take_screenshot(self) -> None:
        """Genuinely capture the current window and save it - the same real grab()
        used to validate this window during development, now reachable from the UI."""
        path, _ = QFileDialog.getSaveFileName(self, "Save Screenshot", "acf_esoc_screenshot.png", "PNG Files (*.png)")
        if not path:
            return
        pixmap = self.grab()
        saved = pixmap.save(path)
        level = "INFO" if saved else "ERROR"
        self.dispatcher.log_message_emitted.emit(
            level, f"Screenshot {'saved to ' + path if saved else 'failed to save to ' + path}"
        )

    def _export_data(self) -> None:
        """Surface CommandDispatcher.export_product()'s own honest explanation of why
        it cannot export yet, instead of the button doing nothing at all."""
        try:
            self.dispatcher.dispatch("export_product", format="png", path="acf_export.png")
        except NotImplementedError as exc:
            QMessageBox.warning(self, "Export Data", str(exc))

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
