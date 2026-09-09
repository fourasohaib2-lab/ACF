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
    import success no longer blocks the operator.

    Updated 2026-09-08 for the import button's new end-to-end wiring:
    a usable file now also computes real AWCI (a second success toast),
    so this test builds a genuinely extractable dataset (the exact
    shape ACF's real NetCDFReader produces) and asserts both toasts;
    a file that matches nothing still toasts once with an error kind
    (see test_awci_dashboard_imported_model.py for the wiring tests)."""
    import numpy as np

    from acf.data.dataset import Dataset
    from acf.data.manager import DataManager

    fake_dataset = Dataset(name="test.grib", filetype="GRIB", source="xarray")
    lats = np.linspace(20.0, 44.0, 25)
    lons = np.linspace(-8.0, 15.0, 20)
    LAT, LON = np.meshgrid(lats, lons, indexing="ij")
    fake_dataset.add_variable("latitude", lats)
    fake_dataset.add_variable("longitude", lons)
    fake_dataset.add_variable("t2m", 288.0 + 0.3 * LAT - 0.02 * LON)
    fake_dataset.add_variable("u10", 3.0 + 0.05 * LON)
    fake_dataset.add_variable("v10", 1.0 + 0.02 * LAT)
    fake_dataset.add_variable("sp", np.full_like(LAT, 1013.0))
    for name, unit in (("t2m", "K"), ("u10", "m s-1"), ("v10", "m s-1"), ("sp", "hPa")):
        fake_dataset.set_metadata(f"{name}_units", unit)

    dashboard = AWCIDashboard()
    qtbot.addWidget(dashboard)
    bogus = tmp_path / "test.grib"
    bogus.write_bytes(b"\x00")

    with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName", return_value=(str(bogus), "")), patch.object(
        DataManager, "open", return_value=fake_dataset
    ), patch("PySide6.QtWidgets.QMessageBox.information") as mock_info:
        dashboard._import_model_file()

    mock_info.assert_not_called()
    # Toast 1: load success. Toast 2: real AWCI computed from it.
    assert len(dashboard._toasts._active) == 2
    assert dashboard._last_point_mode == "imported_model"


def test_clock_label_shows_a_real_ticking_utc_time_and_has_a_fixed_width(qtbot):
    dashboard = AWCIDashboard()
    qtbot.addWidget(dashboard)

    text = dashboard.clock_label.text()
    assert text.endswith(" UTC")
    assert len(text) == len("00:00:00 UTC")
    # Real fix for a real flaky-test bug found this session: a fixed
    # width so ticking seconds can never change header.sizeHint().
    assert dashboard.clock_label.minimumWidth() == dashboard.clock_label.maximumWidth()
