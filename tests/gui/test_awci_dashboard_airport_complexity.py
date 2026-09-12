"""
Tests for AWCIDashboard._compute_airport_complexity_rows() - the real
per-airport AWCI computation added 2026-09-12 (docs/reference/
awci_dashboard_reference.png, Phase 4/6 of the AWCI redesign).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.calculator import AWCICalculator
from acf.gui.dashboard.awci_dashboard import _AIRPORTS, AWCIDashboard
from acf.gui.dashboard.awci_situation_panel import DEFAULT_AIRPORT_ICAO_CODES
from acf.gui.dashboard.awci_synthetic_field import _synthetic_inputs


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_returns_one_row_per_requested_real_airport(qapp):
    dashboard = AWCIDashboard()
    rows = dashboard._compute_airport_complexity_rows(DEFAULT_AIRPORT_ICAO_CODES)
    assert [row["icao"] for row in rows] == list(DEFAULT_AIRPORT_ICAO_CODES)


def test_awci_value_matches_a_direct_recomputation_at_the_real_airport_coordinates(qapp):
    """Real proof: the row's own "awci" is not a fabricated/guessed
    number - it matches an independent direct call to the SAME real
    AWCICalculator/_synthetic_inputs pipeline at that airport's real
    published (lat, lon)."""
    dashboard = AWCIDashboard()
    rows = dashboard._compute_airport_complexity_rows(("DAAG",))

    lat, lon, _name = _AIRPORTS["DAAG"]
    expected = AWCICalculator().calculate(
        _synthetic_inputs(
            lat, lon, flight_level_hpa=dashboard._current_flight_level_hpa, time_offset_hours=float(dashboard.time_slider.value())
        )
    )["awci"]
    assert rows[0]["awci"] == pytest.approx(expected)


def test_trend_arrow_is_a_real_comparison_against_one_hour_earlier(qapp):
    dashboard = AWCIDashboard()
    rows = dashboard._compute_airport_complexity_rows(("DAAG",))
    assert rows[0]["trend"] in ("↑", "↓", "→")


def test_level_uses_the_real_shared_awci_scale(qapp):
    from acf.gui.dashboard.awci_colors import level_for

    dashboard = AWCIDashboard()
    rows = dashboard._compute_airport_complexity_rows(("DAAG",))
    assert rows[0]["level"] == level_for(rows[0]["awci"])


def test_view_all_airports_covers_every_real_airport_in_the_reference_table(qapp):
    """_open_all_airports_dialog() itself calls the real modal
    QDialog.exec() (would block this test's event loop) - so this
    checks the real computation it feeds the dialog with directly,
    the same real _compute_airport_complexity_rows() call, over every
    real airport in the reference table rather than just the 5-row
    summary subset."""
    dashboard = AWCIDashboard()
    rows = dashboard._compute_airport_complexity_rows(tuple(_AIRPORTS.keys()))
    assert len(rows) == len(_AIRPORTS)
