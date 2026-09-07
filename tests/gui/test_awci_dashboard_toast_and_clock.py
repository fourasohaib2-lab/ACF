"""
Tests wiring AWCIDashboard's real toast notifications and live UTC
clock (2026-09-07, "rends-le exceptionnel" 2026-modernization pass) -
see awci_toast.py's own module docstring for what stays a blocking
QMessageBox vs. what becomes a toast.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from acf.gui.dashboard.awci_dashboard import AWCIDashboard, _AIRPORTS


def test_dashboard_has_a_real_toast_manager(qtbot):
    dashboard = AWCIDashboard()
    qtbot.addWidget(dashboard)

    assert dashboard._toasts is not None


def test_applying_a_route_shows_a_success_toast(qtbot):
    dashboard = AWCIDashboard()
    qtbot.addWidget(dashboard)
    dashboard.route_from_selector.setCurrentIndex(list(_AIRPORTS).index("KJFK"))
    dashboard.route_to_selector.setCurrentIndex(list(_AIRPORTS).index("LFPG"))

    dashboard._on_apply_route()

    assert len(dashboard._toasts._active) == 1


def test_disconnecting_hpc_shows_an_info_toast(qtbot):
    dashboard = AWCIDashboard()
    qtbot.addWidget(dashboard)
    dashboard._hpc = MagicMock()
    dashboard._hpc_connected = True
    dashboard.hpc_button.setText("🔌 Disconnect (FENNEC)")

    dashboard._toggle_hpc_connection()

    assert len(dashboard._toasts._active) == 1


def test_importing_a_real_file_shows_a_success_toast_not_a_blocking_dialog(qtbot, tmp_path):
    """The old behavior (QMessageBox.information) is gone - a real
    import success no longer blocks the operator."""
    from acf.data.manager import DataManager

    fake_dataset = MagicMock()
    fake_dataset.name = "test.grib"
    fake_dataset.filetype = "GRIB"
    fake_dataset.variables = {"t2m": None, "msl": None}

    dashboard = AWCIDashboard()
    qtbot.addWidget(dashboard)
    bogus = tmp_path / "test.grib"
    bogus.write_bytes(b"\x00")

    with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=(str(bogus), "")), patch.object(
        DataManager, "open", return_value=fake_dataset
    ), patch("PySide6.QtWidgets.QMessageBox.information") as mock_info:
        dashboard._import_model_file()

    mock_info.assert_not_called()
    assert len(dashboard._toasts._active) == 1


def test_clock_label_shows_a_real_ticking_utc_time_and_has_a_fixed_width(qtbot):
    dashboard = AWCIDashboard()
    qtbot.addWidget(dashboard)

    text = dashboard.clock_label.text()
    assert text.endswith(" UTC")
    assert len(text) == len("00:00:00 UTC")
    # Real fix for a real flaky-test bug found this session: a fixed
    # width so ticking seconds can never change header.sizeHint().
    assert dashboard.clock_label.minimumWidth() == dashboard.clock_label.maximumWidth()
