"""ESOC Top Master Operational Toolbar with HPC Cluster Controls (ACF-HPC-001)."""

from collections.abc import Callable

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QToolBar, QWidget

from acf.gui.esoc.esoc_workspace import WorkspaceMode


class ESOCToolbar(QToolBar):
    """Top operational toolbar for action buttons, HPC connections, and workspace mode selection."""

    def __init__(
        self,
        on_action_callback: Callable[[str], None] | None = None,
        on_mode_callback: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__("ESOC Master Operational Toolbar")
        self.on_action_callback = on_action_callback
        self.on_mode_callback = on_mode_callback

        self.setMovable(False)

        actions = [
            ("📂 Open Dataset", "open_dataset"),
            ("📡 Live Stream", "live_stream"),
            ("🔌 Connect HPC", "connect_hpc"),
            ("❌ Disconnect", "disconnect_hpc"),
            ("🚀 Submit Job", "submit_hpc_job"),
            ("⏹ Cancel Job", "cancel_hpc_job"),
            ("🔄 Sync HPC", "sync_hpc_storage"),
            ("💻 Terminal", "open_terminal"),
            ("📜 Logs", "open_logs"),
            ("📊 Benchmark", "benchmark_hpc"),
            ("🔮 Forecast", "trigger_forecast"),
            ("🚀 Simulation", "trigger_sim"),
            ("🔄 Assimilation", "trigger_da"),
            ("🌐 Digital Twin", "trigger_twin"),
            ("🌡️ Climate", "trigger_climate"),
            ("⚠️ Hazards", "trigger_hazards"),
            ("🧠 AI", "trigger_ai"),
            ("💾 Export", "export_data"),
            ("📷 Screenshot", "take_screenshot"),
            ("⚙️ Settings", "open_settings"),
            ("🗂️ Classic View", "open_classic_dashboard"),
            # By explicit design decision (2026-09-12), the AWCI dashboard is
            # never embedded inside the ACF/ESOC dashboard itself - it used to
            # also live, redundantly, as the 28th (last) tab of the bottom
            # dock (removed) and as a button inside the Classic View window.
            # This button is the one real way to reach it: it opens
            # AWCIDashboardWindow as its own top-level window.
            ("✈️ AWCI", "open_awci_dashboard"),
            # Explicit user request ("une vraie application séparée...
            # pas juste une 2e fenêtre Qt dans le même processus") -
            # unlike the button above, this launches acf.awci_app as its
            # own OS process (see esoc_window.py's own
            # _launch_awci_app()) - genuinely independent lifecycle from
            # ESOC, its own single-instance guard, keeps running if
            # ESOC is closed.
            ("🚀 AWCI (App)", "launch_awci_app"),
            # The real, AWCI-free "ACF Scientific Workstation"
            # (docs/reference/acf_dashboard_reference.jpg) - distinct
            # from the AWCI-only dashboard above. Opens
            # ACFWorkstationWindow. NOTE (correction, 2026-09-04): this
            # used to open ACFGeneralDashboardWindow - a real audit
            # found that dashboard genuinely AWCI-coupled despite its
            # "general ACF" name (see acf_general_dashboard.py's own
            # NOTE) - repointed to the real AWCI-free replacement.
            ("🔬 ACF Scientific Workstation", "open_acf_workstation"),
            # Real acf.awci.spatial_field.compute_real_complexity_field()
            # overlay on THIS window's central map (explicit user
            # request "ajoute la 4eme dimension au niveau d'affichage
            # des cartes") - previously only the separate AWCI dashboard
            # window ever showed real AWCI data.
            ("🌪️ AWCI Field", "show_awci_field_on_map"),
            ("❓ Help", "open_help"),
        ]

        for label, cmd in actions:
            act = QAction(label, self)
            act.triggered.connect(lambda checked=False, c=cmd: self._trigger_action(c))
            self.addAction(act)

        self.addSeparator()

        mode_container = QWidget()
        m_layout = QHBoxLayout(mode_container)
        m_layout.setContentsMargins(4, 0, 4, 0)

        lbl_mode = QLabel("Workspace Mode: ")
        lbl_mode.setStyleSheet("font-weight: bold; color: #81D4FA;")
        m_layout.addWidget(lbl_mode)

        self.combo_mode = QComboBox()
        for mode in WorkspaceMode:
            self.combo_mode.addItem(mode.value)

        self.combo_mode.currentTextChanged.connect(self._on_mode_changed)
        m_layout.addWidget(self.combo_mode)

        self.addWidget(mode_container)

    def _trigger_action(self, cmd: str) -> None:
        if self.on_action_callback:
            self.on_action_callback(cmd)

    def _on_mode_changed(self, mode_str: str) -> None:
        if self.on_mode_callback:
            self.on_mode_callback(mode_str)
