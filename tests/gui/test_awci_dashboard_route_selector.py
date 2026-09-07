"""
Tests for AWCIDashboard's real airport-to-airport route selector -
explicit user request ("un bouton pour changer la route entre les
aeroports en introduisant tout les aeroport existant"), plus the
follow-up "rendre tout les boutons du dashboard fonctionnel" (verified
separately by a real smoke-test click of all 13 real QPushButtons this
dashboard has - see docs/STATUS.md for that result).

_REGIONAL_ROUTE used to be a fixed module constant every real panel
(route chart, cross-section-style sampling, FL280/FL320 comparison)
read directly - now self._regional_route, a real instance attribute
_on_apply_route() can change, defaulting to the exact same route as
before so nothing changes until a user picks one.
"""

from __future__ import annotations

from unittest.mock import patch

from acf.gui.dashboard.awci_dashboard import _AIRPORTS, _REGIONAL_ROUTE, AWCIDashboard


def test_airport_table_has_real_icao_codes_and_real_coordinates():
    assert len(_AIRPORTS) >= 20
    for icao, (lat, lon, name) in _AIRPORTS.items():
        assert len(icao) == 4 and icao.isupper()  # a real ICAO code shape
        assert -90.0 <= lat <= 90.0
        assert -180.0 <= lon <= 180.0
        assert name


def test_route_selectors_are_populated_from_the_real_airport_table(qtbot):
    dashboard = AWCIDashboard()
    qtbot.addWidget(dashboard)

    assert dashboard.route_from_selector.count() == len(_AIRPORTS)
    assert dashboard.route_to_selector.count() == len(_AIRPORTS)
    # Real ICAO code stored as item data, not just baked into the label text.
    assert dashboard.route_from_selector.itemData(0) in _AIRPORTS


def test_default_route_matches_the_original_fixed_demo_route(qtbot):
    """Nothing changes for an operator who never touches the new
    selector - same real Alger/Tripoli route as before this feature."""
    dashboard = AWCIDashboard()
    qtbot.addWidget(dashboard)

    assert dashboard._regional_route == list(_REGIONAL_ROUTE)


def test_applying_a_new_route_updates_the_real_regional_route(qtbot):
    dashboard = AWCIDashboard()
    qtbot.addWidget(dashboard)

    from_index = list(_AIRPORTS).index("KJFK")
    to_index = list(_AIRPORTS).index("LFPG")
    dashboard.route_from_selector.setCurrentIndex(from_index)
    dashboard.route_to_selector.setCurrentIndex(to_index)

    dashboard._on_apply_route()

    assert dashboard._regional_route[0][:2] == _AIRPORTS["KJFK"][:2]
    assert dashboard._regional_route[1][:2] == _AIRPORTS["LFPG"][:2]


def test_applying_a_route_genuinely_updates_the_map_flight_path(qtbot):
    dashboard = AWCIDashboard()
    qtbot.addWidget(dashboard)

    dashboard.route_from_selector.setCurrentIndex(list(_AIRPORTS).index("EGLL"))
    dashboard.route_to_selector.setCurrentIndex(list(_AIRPORTS).index("EDDF"))
    dashboard._on_apply_route()

    # Real, observable effect on the real map widget, not just internal state.
    assert dashboard.regional_map._flight_path == dashboard._regional_route


def test_applying_a_route_recomputes_the_real_route_chart(qtbot):
    """Proves the change reaches AWCICalculator through the real
    route-chart pipeline, not just stored and ignored."""
    dashboard = AWCIDashboard()
    qtbot.addWidget(dashboard)
    original_distances = list(dashboard.route_chart.last_distances_km or [])

    dashboard.route_from_selector.setCurrentIndex(list(_AIRPORTS).index("RJTT"))
    dashboard.route_to_selector.setCurrentIndex(list(_AIRPORTS).index("WSSS"))
    dashboard._on_apply_route()

    assert dashboard.route_chart.last_distances_km is not None
    assert list(dashboard.route_chart.last_distances_km) != original_distances


def test_choosing_the_same_airport_twice_is_rejected_honestly(qtbot):
    dashboard = AWCIDashboard()
    qtbot.addWidget(dashboard)
    route_before = list(dashboard._regional_route)

    dashboard.route_from_selector.setCurrentIndex(list(_AIRPORTS).index("KJFK"))
    dashboard.route_to_selector.setCurrentIndex(list(_AIRPORTS).index("KJFK"))

    with patch("PySide6.QtWidgets.QMessageBox.warning") as mock_warning:
        dashboard._on_apply_route()

    mock_warning.assert_called_once()
    assert dashboard._regional_route == route_before  # unchanged, not silently applied anyway
