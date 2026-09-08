"""Unit test suite for ACF-HPC-002 HPC Connection Dialog & Remote Terminal Panel."""

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from acf.gui.esoc.hpc_connection_dialog import HPCConnectionDialog
from acf.gui.esoc.hpc_terminal_panel import HPCTerminalPanel

# See tests/test_hpc_connector.py's own comment for the full story: on an
# ONM-networked machine (this one), the real "login2.fennec.meteo.dz" hostname
# resolves to a real, reachable 10.16.20.2 - _test_connection() below now does a
# genuine DNS+TCP probe (see hpc_connection_dialog.py's own NOTE), so a unit test
# must use a guaranteed-unresolvable hostname to stay network-safe and
# deterministic regardless of which machine runs it. ".invalid" is an
# IANA/RFC 2606-reserved TLD.
OFFLINE_TEST_HOSTNAME = "test-offline-host.invalid"


@pytest.fixture(scope="session")
def qapp():
    """Ensure a PySide6 QApplication instance exists for Qt widget tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_hpc_connection_dialog(qapp):
    dialog = HPCConnectionDialog()
    assert dialog is not None
    config = dialog.get_connection_config()
    assert "hostname" in config
    assert "username" in config
    assert config["scheduler"] in ["Slurm", "PBS / Torque", "IBM LSF", "Grid Engine (SGE)", "Local Execution"]


def test_hpc_connection_dialog_test_connection_and_save_are_now_real(qapp, monkeypatch, tmp_path):
    """
    CORRECTED (original finding): _test_connection() used to
    unconditionally claim "Successfully verified SSH connectivity" with
    a fixed fake "Latency: 12 ms" - no socket/SSH call was made anywhere
    in this class. _save_profile() used to unconditionally claim the
    profile was saved to config/hpc_profiles/ - no file was written
    anywhere. Both were dangerous fabricated-success confirmations.

    UPDATED (later): both methods are now genuinely real -
    _test_connection() does a real DNS resolution + TCP connect,
    _save_profile() really writes a YAML file (see
    hpc_connection_dialog.py's own NOTE comments on each). This test now
    verifies the real behavior, kept network- and filesystem-safe: an
    always-unresolvable hostname (this file's own OFFLINE_TEST_HOSTNAME -
    on this ONM-networked machine, the real default "fennec" hostname is
    genuinely reachable, which would otherwise make this test perform a
    real network probe) for the connection test, and a tmp_path-
    redirected save location (avoids ever writing into the real repo's
    config/hpc_profiles/ during a test run - same test-isolation
    principle as this session's earlier ~/.acf/recent_projects.json fix).
    """
    seen = {}

    def fake_critical(parent, title, text, *args, **kwargs):
        seen[title] = text
        return QMessageBox.StandardButton.Ok

    def fake_information(parent, title, text, *args, **kwargs):
        seen[title] = text
        return QMessageBox.StandardButton.Ok

    monkeypatch.setattr(QMessageBox, "critical", fake_critical)
    monkeypatch.setattr(QMessageBox, "information", fake_information)
    monkeypatch.setattr(
        HPCConnectionDialog, "_saved_profile_path", staticmethod(lambda key: tmp_path / f"{key}.connection.yaml")
    )

    dialog = HPCConnectionDialog()
    dialog.input_host.setText(OFFLINE_TEST_HOSTNAME)

    # Real DNS resolution genuinely fails for an .invalid hostname -
    # deterministic on every machine, never reaches an actual socket.
    dialog._test_connection()
    assert "[DNS FAILED]" in seen["HPC Connection Test"]
    assert OFFLINE_TEST_HOSTNAME in seen["HPC Connection Test"]

    # Real file write, redirected to tmp_path.
    dialog._save_profile()
    saved_path = tmp_path / "fennec.connection.yaml"
    assert saved_path.exists()
    assert "written to" in seen["Save HPC Profile"]
    # The password field must never be persisted, even though this form
    # never had one entered - a real, present password would make this
    # assertion meaningful; ensure the key is at least never emitted.
    assert "password" not in saved_path.read_text(encoding="utf-8").lower()


def test_hpc_terminal_panel(qapp):
    """
    CORRECTED: used to assert a fabricated "squeue" response (job id
    "1024") that was returned for ANY command regardless of whether it
    was ever really executed. With no registry supplied, the terminal
    now honestly reports it has no real HPC connector to route through.
    """
    term = HPCTerminalPanel()
    assert term is not None
    term.cmd_input.setText("squeue")
    term._exec_cmd()
    assert "[NOT CONNECTED]" in term.terminal_output.toPlainText()
