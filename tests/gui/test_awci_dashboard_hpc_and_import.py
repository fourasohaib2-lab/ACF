"""
Tests for AWCIDashboard's "🔌 Connect HPC" and "📂 Import Model File"
buttons - explicit user request ("ajoute un bouton pour la connexion à
hpc et un autre bouton pour faire entrer des fichiers de modèle").

NOTE (correction, 2026-09-07 - real, reproducible bug found while
verifying the HPC button against a real connection, with the user's
explicit permission): _toggle_hpc_connection() held its
_HPCConnectWorker only as a local variable. A real HPC connect takes
~2-3s of real network I/O (unlike this dashboard's other, fast/CPU-
bound QRunnable workers, e.g. _RealFieldWorker) - long enough that
Python's garbage collector was reliably collecting the worker/its
signals QObject (no C++ parent, no other live reference) before the
background thread ever got to emit `finished`. Confirmed directly: a
wrapped slot never printed even after a real 20s wait following a
successful real SSH connection (SUCCESS logged, but nothing update GUI
side). Fixed by holding the worker on self (self._hpc_connect_worker)
for the duration of the async call - see that attribute's own comment.

Every test here mocks HPCConnectionManager.connect()/disconnect() at
the class level - NONE of these tests ever make a real network
connection. The real fix above was independently verified by hand
against the user's own real HPC cluster (with explicit permission),
not by these tests - these lock in the async/GC-safety behavior
deterministically and repeatably instead.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from acf.gui.dashboard.awci_dashboard import AWCIDashboard
from acf.gui.esoc.hpc_connection_dialog import HPCConnectionDialog


def _real_ssh_connector_stub(is_real: bool) -> MagicMock:
    stub = MagicMock()
    stub.is_real_connection = is_real
    return stub


class TestHPCConnectionButton:
    def test_button_exists_with_the_real_expected_label(self, qtbot):
        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)
        assert dashboard.hpc_button.text() == "🔌 Connect HPC"

    def test_connecting_genuinely_updates_state_after_a_real_async_delay(self, qtbot):
        """The regression test for the GC-race bug itself: connect()
        is mocked to sleep briefly (simulating real network latency,
        the exact condition that exposed the bug) before returning -
        qtbot.waitUntil() gives the background QRunnable real time to
        finish and for GC to have every opportunity to run in between,
        the same real-world condition that broke this before the fix."""
        import time

        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)

        def _slow_connect(profile, overrides=None):
            time.sleep(0.3)
            return True

        with patch.object(HPCConnectionDialog, "exec", return_value=1), patch.object(
            HPCConnectionDialog,
            "get_connection_config",
            return_value={"profile_key": "fennec", "profile_name": "FENNEC"},
        ), patch("acf.hpc_connector.HPCConnectionManager.connect", side_effect=_slow_connect), patch(
            "acf.hpc_connector.HPCConnectionManager.__init__", return_value=None
        ):
            dashboard._toggle_hpc_connection()
            # A real HPCConnectionManager.__init__ is mocked away too
            # (it loads config/hpc.yaml for real otherwise) - attach a
            # real, controlled ssh_connector stub the same way the real
            # manager exposes one.
            dashboard._hpc.ssh_connector = _real_ssh_connector_stub(is_real=True)

            qtbot.waitUntil(lambda: dashboard._hpc_connected is True, timeout=5000)

        assert dashboard.hpc_button.text() == "🔌 Disconnect (FENNEC)"
        assert dashboard._hpc_connect_worker is None  # released once delivered, not leaked

    def test_disconnecting_calls_the_real_manager_and_resets_state(self, qtbot):
        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)
        dashboard._hpc = MagicMock()
        dashboard._hpc_connected = True
        dashboard.hpc_button.setText("🔌 Disconnect (FENNEC)")

        dashboard._toggle_hpc_connection()

        dashboard._hpc.disconnect.assert_called_once()
        assert dashboard._hpc_connected is False
        assert dashboard.hpc_button.text() == "🔌 Connect HPC"

    def test_a_workflow_completing_without_a_real_ssh_transport_is_reported_honestly(self, qtbot):
        """Same is_real_connection discipline as ESOC's own
        _connect_hpc() - a completed local/offline workflow must not
        be shown as 'Connected'."""
        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)

        with patch.object(HPCConnectionDialog, "exec", return_value=1), patch.object(
            HPCConnectionDialog, "get_connection_config", return_value={"profile_key": "fennec", "profile_name": "FENNEC"}
        ), patch("acf.hpc_connector.HPCConnectionManager.connect", return_value=True), patch(
            "acf.hpc_connector.HPCConnectionManager.__init__", return_value=None
        ), patch("PySide6.QtWidgets.QMessageBox.warning", return_value=None):
            dashboard._toggle_hpc_connection()
            dashboard._hpc.ssh_connector = _real_ssh_connector_stub(is_real=False)

            qtbot.waitUntil(lambda: dashboard.hpc_button.isEnabled() is True, timeout=5000)

        assert dashboard._hpc_connected is False
        assert dashboard.hpc_button.text() == "🔌 Connect HPC"

    def test_cancelling_the_dialog_makes_no_connection_attempt(self, qtbot):
        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)

        with patch.object(HPCConnectionDialog, "exec", return_value=0), patch(
            "acf.hpc_connector.HPCConnectionManager.connect"
        ) as mock_connect:
            dashboard._toggle_hpc_connection()

        mock_connect.assert_not_called()
        assert dashboard._hpc_connected is False


class TestImportModelFileButton:
    def test_button_exists_with_the_real_expected_label(self, qtbot):
        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)
        assert dashboard.import_model_button.text() == "📂 Import Model File"

    def test_cancelling_the_file_dialog_imports_nothing(self, qtbot):
        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)

        with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=("", "")):
            dashboard._import_model_file()

        assert dashboard._imported_dataset is None

    def test_a_genuinely_unreadable_file_reports_an_honest_error_not_a_crash(self, qtbot, tmp_path):
        bogus = tmp_path / "not_a_real_model_file.xyz"
        bogus.write_text("nonsense")

        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)

        with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=(str(bogus), "")), patch(
            "PySide6.QtWidgets.QMessageBox.critical"
        ) as mock_critical:
            dashboard._import_model_file()

        mock_critical.assert_called_once()
        assert dashboard._imported_dataset is None
        assert dashboard.play_evolution_button.isEnabled() is False

    def test_a_successful_import_enables_the_4d_evolution_button(self, qtbot):
        """Regression guard for a real bug found 2026-09-11 (full AWCI
        rescan): this button's own tooltip has always advertised a real
        import-tier 4D evolution capability ("With an imported model
        file active instead: computes and animates the real per-grid-
        cell AWCI evolution...") but nothing ever called
        setEnabled(True) for that path - only _on_real_physics_ready()
        did, making the import-only path unreachable from the real UI.
        DataManager.open() is mocked (matching this file's own
        established convention) to return a real, valid Dataset rather
        than requiring a real model file on disk."""
        from acf.data.dataset import Dataset

        dataset = Dataset(name="mock-import", filetype="NetCDF", source="xarray")
        dataset.add_variable("t2m", [[288.0, 289.0], [290.0, 291.0]])
        dataset.add_variable("latitude", [30.0, 31.0])
        dataset.add_variable("longitude", [0.0, 1.0])

        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)
        assert dashboard.play_evolution_button.isEnabled() is False

        with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=("fake.nc", "")), patch(
            "acf.data.manager.DataManager.open", return_value=dataset
        ):
            dashboard._import_model_file()

        assert dashboard._imported_dataset is dataset
        assert dashboard.play_evolution_button.isEnabled() is True

    def test_reverting_to_demo_keeps_the_button_enabled_while_an_import_is_still_active(self, qtbot):
        """Same real bug as above, second half: _revert_to_demo() used
        to unconditionally disable this button even though the import
        tier's own dataset/evolution are deliberately kept alive by
        that same method (see test_imported_evolution_survives_revert_
        to_demo) - disabling it made that surviving state unreachable
        too."""
        from acf.data.dataset import Dataset

        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)
        dashboard._imported_dataset = Dataset(name="d", filetype="NetCDF", source="xarray")

        dashboard._revert_to_demo()

        assert dashboard.play_evolution_button.isEnabled() is True

    def test_reverting_to_demo_disables_the_button_when_no_import_is_active(self, qtbot):
        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)
        assert dashboard._imported_dataset is None

        dashboard._revert_to_demo()

        assert dashboard.play_evolution_button.isEnabled() is False

    @pytest.mark.skipif(
        not __import__("pathlib").Path.home().joinpath("RESTOR/ALADIN/data/FULLPOS_2026083100_0000").exists(),
        reason="Real RESTOR ALADIN archive not present on this machine (machine-local only, not in git)",
    )
    def test_importing_a_real_fa_file_loads_it_through_the_real_pipeline(self, qtbot):
        """Same real file this session's data-ingestion fixes
        (ffca691) were verified against - proves this button reaches
        that same real, working pipeline, not a second one."""
        from pathlib import Path

        real_file = Path.home() / "RESTOR/ALADIN/data/FULLPOS_2026083100_0000"
        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)

        with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=(str(real_file), "")), patch(
            "PySide6.QtWidgets.QMessageBox.information"
        ):
            dashboard._import_model_file()

        assert dashboard._imported_dataset is not None
        assert dashboard._imported_dataset.filetype == "FA"
        assert len(dashboard._imported_dataset.variables) == 97
