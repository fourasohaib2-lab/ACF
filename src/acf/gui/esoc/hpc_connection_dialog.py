"""ESOC HPC Connection Wizard & Profile Dialog (ACF-HPC-002)."""

from __future__ import annotations

import socket
from pathlib import Path
from typing import Any

import yaml
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

from acf.gui_screen_utils import fit_dialog_to_screen

# Ordered presets shown in "Saved HPC Profile". ``key`` is the lookup name passed
# to HPCConfiguration.get_cluster_profile() / HPCConnectionManager.connect(), so it
# MUST match a key under ``cluster_profiles:`` in config/hpc.yaml for the profile to
# resolve to real settings. Everything else is only a starting point for the form -
# the operator can override any field before connecting.
PROFILE_PRESETS: dict[str, dict[str, Any]] = {
    "FENNEC — ONM (login2.fennec.meteo.dz)": {
        "key": "fennec",
        "hostname": "login2.fennec.meteo.dz",
        "username": "sfoura",
        "port": 22,
        "key_path": "~/.ssh/id_rsa",
        "scheduler": "Slurm",
        "remote_dir": "/onm/dem/home/sfoura/ACF",
        "scratch_dir": "/mnt/beegfs",
        "mpi_launcher": "srun",
        "gpu_mode": "CPU-Only Mode",
    },
    "Local Workstation": {
        "key": "local",
        "hostname": "localhost",
        "username": "",  # filled from the running user in _apply_profile()
        "port": 22,
        "key_path": "~/.ssh/id_rsa",
        "scheduler": "Local Execution",
        "remote_dir": "/tmp/acf_run",
        "scratch_dir": "/tmp/acf_scratch",
        "mpi_launcher": "mpirun",
        "gpu_mode": "CPU-Only Mode",
    },
    "University HPC (hpc.university.edu)": {
        "key": "university_hpc",
        "hostname": "hpc.university.edu",
        "username": "researcher",
        "port": 22,
        "key_path": "~/.ssh/id_rsa",
        "scheduler": "Slurm",
        "remote_dir": "/home/researcher/acf_workspace",
        "scratch_dir": "/scratch/researcher/acf",
        "mpi_launcher": "srun",
        "gpu_mode": "CUDA (NVIDIA A100/H100)",
    },
    "Custom HPC Cluster": {
        "key": "custom",
        "hostname": "",
        "username": "",
        "port": 22,
        "key_path": "~/.ssh/id_rsa",
        "scheduler": "Slurm",
        "remote_dir": "",
        "scratch_dir": "",
        "mpi_launcher": "srun",
        "gpu_mode": "CPU-Only Mode",
    },
}

DEFAULT_PROFILE = "FENNEC — ONM (login2.fennec.meteo.dz)"


def _project_root() -> Path:
    """Locate the ACF project root (the directory containing src/acf)."""
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        if (parent / "src" / "acf").exists() or (parent / ".git").exists():
            return parent
    return Path.cwd()


class HPCConnectionDialog(QDialog):
    """Wizard dialog for configuring SSH parameters, scheduler settings, and HPC connection profiles."""

    def __init__(self, parent: Any | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("🔌 Universal HPC Connection Wizard & Profiles")
        # NOTE (real responsive-sizing fix, 2026-09-05): was a hardcoded
        # self.resize(600, 480) - clamp to the actual screen instead, same
        # fix as gui_screen_utils.fit_window_to_screen for main windows.
        fit_dialog_to_screen(self, 600, 480)

        main_layout = QVBoxLayout(self)

        title = QLabel("🔌 CONFIGURE HPC REMOTE CLUSTER CONNECTION")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #4FC3F7; margin-bottom: 10px;")
        main_layout.addWidget(title)

        form = QFormLayout()

        # Host Profile Selector
        self.combo_profile = QComboBox()
        self.combo_profile.addItems(list(PROFILE_PRESETS))
        form.addRow("Saved HPC Profile:", self.combo_profile)

        self.input_host = QLineEdit()
        form.addRow("Hostname / IP:", self.input_host)

        self.input_user = QLineEdit()
        form.addRow("Username:", self.input_user)

        self.spin_port = QSpinBox()
        self.spin_port.setRange(1, 65535)
        self.spin_port.setValue(22)
        form.addRow("SSH Port:", self.spin_port)

        self.input_key = QLineEdit()
        form.addRow("SSH Key Path:", self.input_key)

        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pass.setPlaceholderText("(Optional SSH Password — never written to disk)")
        form.addRow("Password / Token:", self.input_pass)

        self.combo_scheduler = QComboBox()
        self.combo_scheduler.addItems(["Slurm", "PBS / Torque", "IBM LSF", "Grid Engine (SGE)", "Local Execution"])
        form.addRow("Batch Scheduler:", self.combo_scheduler)

        self.input_remote_dir = QLineEdit()
        form.addRow("Remote Work Dir:", self.input_remote_dir)

        self.input_scratch_dir = QLineEdit()
        form.addRow("Scratch Directory:", self.input_scratch_dir)

        self.combo_mpi = QComboBox()
        self.combo_mpi.addItems(["srun", "mpirun", "mpiexec"])
        form.addRow("MPI Launcher:", self.combo_mpi)

        self.combo_gpu = QComboBox()
        self.combo_gpu.addItems(["CUDA (NVIDIA A100/H100)", "ROCm (AMD MI250X)", "Intel OneAPI GPU", "CPU-Only Mode"])
        form.addRow("GPU Mode:", self.combo_gpu)

        main_layout.addLayout(form)

        self.label_status = QLabel("")
        self.label_status.setWordWrap(True)
        self.label_status.setStyleSheet("color: #B0BEC5; margin-top: 6px;")
        main_layout.addWidget(self.label_status)

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

        # The profile selector now actually drives the form (it previously changed
        # nothing, so the displayed profile name and the displayed settings could
        # disagree - e.g. "Local Workstation" shown next to hpc.university.edu).
        self.combo_profile.currentTextChanged.connect(self._apply_profile)
        self.combo_profile.setCurrentText(DEFAULT_PROFILE)
        self._apply_profile(DEFAULT_PROFILE)

    # ------------------------------------------------------------------ profiles

    def _apply_profile(self, label: str) -> None:
        """Populate every field from the selected preset, overlaid with any saved YAML profile."""
        preset = dict(PROFILE_PRESETS.get(label, {}))
        if not preset:
            return
        preset.update(self._load_saved_profile(preset.get("key", "")))
        if preset.get("key") == "local" and not preset.get("username"):
            import getpass

            preset["username"] = getpass.getuser()

        self.input_host.setText(str(preset.get("hostname", "")))
        self.input_user.setText(str(preset.get("username", "")))
        self.spin_port.setValue(int(preset.get("port", 22) or 22))
        self.input_key.setText(str(preset.get("key_path", "~/.ssh/id_rsa")))
        self.input_remote_dir.setText(str(preset.get("remote_dir", "")))
        self.input_scratch_dir.setText(str(preset.get("scratch_dir", "")))
        self._select(self.combo_scheduler, str(preset.get("scheduler", "")))
        self._select(self.combo_mpi, str(preset.get("mpi_launcher", "")))
        self._select(self.combo_gpu, str(preset.get("gpu_mode", "")))

        key = preset.get("key", "")
        self.label_status.setText(f"Profile key passed to the connector: {key!r} (must exist under cluster_profiles: in config/hpc.yaml)")

    @staticmethod
    def _saved_profile_path(key: str) -> Path:
        """Where this dialog persists a profile.

        Deliberately NOT ``<key>.yaml``: config/hpc_profiles/ already holds
        hand-written cluster descriptions (fennec.yaml and friends) with a richer,
        different schema, and overwriting one of those with this dialog's flat
        connection fields would destroy real configuration.
        """
        return _project_root() / "config" / "hpc_profiles" / f"{key}.connection.yaml"

    def _load_saved_profile(self, key: str) -> dict[str, Any]:
        """Return a previously saved connection profile for ``key``, or {} if absent."""
        if not key:
            return {}
        path = self._saved_profile_path(key)
        if not path.exists():
            return {}
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}

    @staticmethod
    def _select(combo: QComboBox, value: str) -> None:
        """Select ``value`` in ``combo`` if present, case-insensitively; otherwise leave it alone."""
        if not value:
            return
        for i in range(combo.count()):
            if combo.itemText(i).lower() == value.lower():
                combo.setCurrentIndex(i)
                return
        for i in range(combo.count()):
            if value.lower() in combo.itemText(i).lower():
                combo.setCurrentIndex(i)
                return

    # ------------------------------------------------------------------- actions

    def _test_connection(self) -> None:
        """Genuinely probe host:port over TCP and report exactly what was observed.

        NOTE (correction — dangerous fabrication): this used to
        unconditionally claim "Successfully verified SSH connectivity"
        with a fixed fake "Latency: 12 ms", regardless of whether any
        connection was ever attempted. It was then replaced by a blanket
        "[NOT CONNECTED]" warning, which was honest but useless. It now
        performs a real DNS resolution plus a real TCP connect with a
        5 s timeout, and reports the measured round-trip. This proves
        reachability of the SSH port only - it does NOT authenticate, so
        it never claims the credentials are valid.
        """
        host = self.input_host.text().strip()
        port = self.spin_port.value()
        if not host:
            QMessageBox.warning(self, "HPC Connection Test", "No hostname / IP entered.")
            return

        try:
            addr_info = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
        except socket.gaierror as exc:
            self.label_status.setText(f"DNS resolution failed for {host}")
            QMessageBox.critical(
                self,
                "HPC Connection Test",
                f"[DNS FAILED] {host} could not be resolved: {exc}\n\n"
                "Nothing was contacted. Check the hostname, your DNS, or whether you need to be on the ONM network / VPN.",
            )
            return

        resolved = addr_info[0][4][0]
        family, socktype, proto = addr_info[0][0], addr_info[0][1], addr_info[0][2]

        import time as _time

        sock = socket.socket(family, socktype, proto)
        sock.settimeout(5.0)
        start = _time.monotonic()
        try:
            sock.connect(addr_info[0][4])
        except OSError as exc:
            sock.close()
            self.label_status.setText(f"{host}:{port} unreachable")
            QMessageBox.critical(
                self,
                "HPC Connection Test",
                f"[UNREACHABLE] {host} resolves to {resolved}, but TCP port {port} did not accept a connection "
                f"within 5 s: {exc}\n\nNo SSH authentication was attempted.",
            )
            return
        elapsed_ms = (_time.monotonic() - start) * 1000.0

        banner = ""
        try:
            sock.settimeout(3.0)
            banner = sock.recv(256).decode("utf-8", "replace").strip()
        except OSError:
            banner = ""
        finally:
            sock.close()

        self.label_status.setText(f"{host}:{port} reachable ({elapsed_ms:.0f} ms)")
        QMessageBox.information(
            self,
            "HPC Connection Test",
            f"[REACHABLE] {host} ({resolved}) accepted a TCP connection on port {port} in {elapsed_ms:.0f} ms.\n"
            + (f"Server banner: {banner}\n" if banner else "")
            + "\nThis confirms the port is open. It does NOT verify your username, SSH key or password - "
            "use ⚡ Connect HPC for the real authenticated session.",
        )

    def _save_profile(self) -> None:
        """Write the current form to config/hpc_profiles/<key>.yaml.

        NOTE (correction — dangerous fabrication): this used to
        unconditionally claim the profile was "Saved... to
        config/hpc_profiles/" while no file was written anywhere. It now
        really writes the YAML and reports the exact path, or the exact
        error. The password field is deliberately never persisted.
        """
        config = self.get_connection_config()
        key = config["profile_key"] or "custom"
        path = self._saved_profile_path(key)

        payload = {k: v for k, v in config.items() if k != "password"}
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
        except OSError as exc:
            QMessageBox.critical(self, "Save HPC Profile", f"[NOT SAVED] Could not write {path}: {exc}")
            return

        self.label_status.setText(f"Profile written to {path}")
        QMessageBox.information(
            self,
            "Save HPC Profile",
            f"Profile '{config['profile_name']}' written to:\n{path}\n\n"
            "The password / token was not written to disk.",
        )

    def _connect_hpc(self) -> None:
        """Validate the minimum required fields, then hand the config back to the caller."""
        if not self.input_host.text().strip():
            QMessageBox.warning(self, "Connect HPC", "A hostname / IP is required.")
            return
        if not self.input_user.text().strip():
            QMessageBox.warning(self, "Connect HPC", "A username is required.")
            return
        self.accept()

    def get_connection_config(self) -> dict[str, Any]:
        """Return configured connection profile parameters.

        ``profile_key`` is the lookup name for config/hpc.yaml's ``cluster_profiles``;
        ``profile_name`` stays the human-readable label shown in the combo box.
        """
        label = self.combo_profile.currentText()
        return {
            "profile_name": label,
            "profile_key": PROFILE_PRESETS.get(label, {}).get("key", "custom"),
            "hostname": self.input_host.text().strip(),
            "username": self.input_user.text().strip(),
            "port": self.spin_port.value(),
            "key_path": self.input_key.text().strip(),
            "password": self.input_pass.text() or None,
            "scheduler": self.combo_scheduler.currentText(),
            "remote_dir": self.input_remote_dir.text().strip(),
            "scratch_dir": self.input_scratch_dir.text().strip(),
            "mpi_launcher": self.combo_mpi.currentText(),
            "gpu_mode": self.combo_gpu.currentText(),
        }
