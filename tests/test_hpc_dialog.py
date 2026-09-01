"""Unit test suite for ACF-HPC-002 HPC Connection Dialog & Remote Terminal Panel."""

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from acf.gui.esoc.hpc_connection_dialog import HPCConnectionDialog
from acf.gui.esoc.hpc_terminal_panel import HPCTerminalPanel


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


def test_hpc_connection_dialog_does_not_fake_success(qapp, monkeypatch):
    """
    CORRECTED: _test_connection() used to unconditionally claim
    "Successfully verified SSH connectivity" with a fixed fake
    "Latency: 12 ms" - no socket/SSH call is made anywhere in this
    class. _save_profile() used to unconditionally claim the profile
    was saved to config/hpc_profiles/ - no file is written anywhere.
    Both are dangerous fabricated-success confirmations with zero real
    action behind them. See hpc_connection_dialog.py's own NOTE
    (correction).
    """
    seen = {}

    def fake_warning(parent, title, text, *args, **kwargs):
        seen[title] = text
        return QMessageBox.StandardButton.Ok

    monkeypatch.setattr(QMessageBox, "warning", fake_warning)

    dialog = HPCConnectionDialog()
    dialog._test_connection()
    assert "[NOT CONNECTED]" in seen["HPC Connection Test"]
    assert "Successfully verified" not in seen["HPC Connection Test"]

    dialog._save_profile()
    assert "[NOT SAVED]" in seen["Save HPC Profile"]
    assert "Saved profile" not in seen["Save HPC Profile"]


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
