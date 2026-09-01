"""ESOC HPC Connection Wizard & Profile Dialog (ACF-HPC-002)."""

from typing import Any

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


class HPCConnectionDialog(QDialog):
    """Wizard dialog for configuring SSH parameters, scheduler settings, and HPC connection profiles."""

    def __init__(self, parent: Any | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("🔌 Universal HPC Connection Wizard & Profiles")
        self.resize(550, 450)

        main_layout = QVBoxLayout(self)

        title = QLabel("🔌 CONFIGURE HPC REMOTE CLUSTER CONNECTION")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #4FC3F7; margin-bottom: 10px;")
        main_layout.addWidget(title)

        form = QFormLayout()

        # Host Profile Selector
        self.combo_profile = QComboBox()
        self.combo_profile.addItems(
            [
                "Local Workstation",
                "University HPC (hpc.university.edu)",
                "National Supercomputer (supercomputer.national.gov)",
                "EuroHPC Supercomputer (lumi.eurohpc.eu)",
                "AWS ParallelCluster",
                "Azure CycleCloud",
                "Google Cloud HPC",
                "Custom HPC Cluster",
            ]
        )
        form.addRow("Saved HPC Profile:", self.combo_profile)

        self.input_host = QLineEdit("hpc.university.edu")
        form.addRow("Hostname / IP:", self.input_host)

        self.input_user = QLineEdit("researcher")
        form.addRow("Username:", self.input_user)

        self.spin_port = QSpinBox()
        self.spin_port.setRange(1, 65535)
        self.spin_port.setValue(22)
        form.addRow("SSH Port:", self.spin_port)

        self.input_key = QLineEdit("~/.ssh/id_rsa")
        form.addRow("SSH Key Path:", self.input_key)

        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pass.setPlaceholderText("(Optional SSH Password)")
        form.addRow("Password / Token:", self.input_pass)

        self.combo_scheduler = QComboBox()
        self.combo_scheduler.addItems(["Slurm", "PBS / Torque", "IBM LSF", "Grid Engine (SGE)", "Local Execution"])
        form.addRow("Batch Scheduler:", self.combo_scheduler)

        self.input_remote_dir = QLineEdit("/home/researcher/acf_workspace")
        form.addRow("Remote Work Dir:", self.input_remote_dir)

        self.input_scratch_dir = QLineEdit("/scratch/researcher/acf")
        form.addRow("Scratch Directory:", self.input_scratch_dir)

        self.combo_mpi = QComboBox()
        self.combo_mpi.addItems(["srun", "mpirun", "mpiexec"])
        form.addRow("MPI Launcher:", self.combo_mpi)

        self.combo_gpu = QComboBox()
        self.combo_gpu.addItems(["CUDA (NVIDIA A100/H100)", "ROCm (AMD MI250X)", "Intel OneAPI GPU", "CPU-Only Mode"])
        form.addRow("GPU Mode:", self.combo_gpu)

        main_layout.addLayout(form)

        # Action Buttons
        btn_box = QHBoxLayout()
        self.btn_test = QPushButton("🔍 Test Connection")
        self.btn_save = QPushButton("💾 Save Profile")
        self.btn_connect = QPushButton("⚡ Connect HPC")
        self.btn_close = QPushButton("Cancel")

        self.btn_test.clicked.connect(self._test_connection)
        self.btn_save.clicked.connect(self._save_profile)
        self.btn_connect.clicked.connect(self._connect_hpc)
        self.btn_close.clicked.connect(self.reject)

        btn_box.addWidget(self.btn_test)
        btn_box.addWidget(self.btn_save)
        btn_box.addWidget(self.btn_connect)
        btn_box.addWidget(self.btn_close)

        main_layout.addLayout(btn_box)

    def _test_connection(self) -> None:
        """
        NOTE (correction — dangerous fabrication): this used to
        unconditionally claim "Successfully verified SSH connectivity"
        with a fixed fake "Latency: 12 ms", regardless of whether any
        connection was ever attempted - there is no socket/SSH/
        paramiko call anywhere in this class. An operator testing a
        completely unreachable or misconfigured host would still be
        told the connection succeeded. Same fabricated-success pattern
        already fixed in this same package's HPCTerminalPanel (see its
        "[NOT CONNECTED]" disclosure) - this dialog was evidently
        missed in that pass. Not fabricated.
        """
        QMessageBox.warning(
            self,
            "HPC Connection Test",
            "[NOT CONNECTED]: no real SSH/network connection is attempted by this dialog - "
            f"{self.input_user.text()}@{self.input_host.text()} was never actually contacted.",
        )

    def _save_profile(self) -> None:
        """
        NOTE (correction — dangerous fabrication): this used to
        unconditionally claim the profile was "Saved... to
        config/hpc_profiles/" - no file is written anywhere in this
        method. An operator could believe their connection settings
        were persisted when nothing was written to disk. Not
        fabricated.
        """
        QMessageBox.warning(
            self,
            "Save HPC Profile",
            f"[NOT SAVED]: no real profile storage is connected here - '{self.combo_profile.currentText()}' "
            "was not written to disk. Use get_connection_config() and persist it yourself if needed.",
        )

    def _connect_hpc(self) -> None:
        self.accept()

    def get_connection_config(self) -> dict[str, Any]:
        """Return configured connection profile parameters."""
        return {
            "profile_name": self.combo_profile.currentText(),
            "hostname": self.input_host.text(),
            "username": self.input_user.text(),
            "port": self.spin_port.value(),
            "key_path": self.input_key.text(),
            "scheduler": self.combo_scheduler.currentText(),
            "remote_dir": self.input_remote_dir.text(),
            "scratch_dir": self.input_scratch_dir.text(),
            "mpi_launcher": self.combo_mpi.currentText(),
            "gpu_mode": self.combo_gpu.currentText(),
        }
