"""
Tests for Task 9 of the 2026-09-14 AWCI dashboard-fixes plan: Current
Situation / Model Agreement / Airport Complexity moving out of their own
full-width row ABOVE the hero map and into a narrow RIGHT column BESIDE
it (the reference image's own arrangement), plus the second-row card
fidelity fixes that came with it (un-clipped "Vertical Cross Section"
and "Atmospheric Profile" titles).

Every assertion below is driven through the REAL dashboard construction
path (`AWCIDashboard()`), never a hand-fed fixture, and the width
assertions are measured on a REAL rendered layout at a real size, not on
stretch factors alone - stretch factors were exactly what silently
failed to arbitrate before this task (see Task 8's own report).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_cross_section import AWCICrossSection
from acf.gui.dashboard.awci_dashboard import AWCIDashboard
from acf.gui.dashboard.awci_situation_panel import AWCIAirportTable


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _laid_out_dashboard(width: int = 1520, height: int = 1650) -> AWCIDashboard:
    """A REAL dashboard, really laid out at a real size (screen_scale=1.0
    - `compute_screen_scale()` returns its 0.6 floor under
    QT_QPA_PLATFORM=offscreen, which would under-represent every real
    size measured below)."""
    dashboard = AWCIDashboard(screen_scale=1.0)
    dashboard.resize(width, height)
    dashboard.show()
    QApplication.processEvents()
    return dashboard


# ------------------------------------------------- the right column's position


def _row_index_of(layout, widget) -> int | None:
    """Which top-level item of `layout` has `widget` somewhere beneath it."""

    def _contains(item, target) -> bool:
        child_widget = item.widget()
        if child_widget is not None:
            return child_widget is target or target in child_widget.findChildren(type(target))
        child_layout = item.layout()
        if child_layout is not None:
            return any(_contains(child_layout.itemAt(j), target) for j in range(child_layout.count()))
        return False

    for i in range(layout.count()):
        if _contains(layout.itemAt(i), widget):
            return i
    return None


def test_the_situation_cards_share_the_hero_maps_own_row(qapp):
    """The whole point of Task 9: these three cards are no longer their
    own full-width row above the map - they sit in the SAME content-layout
    row as the map, i.e. beside it."""
    dashboard = AWCIDashboard()
    content_layout = dashboard.global_map.parentWidget().layout()

    map_row = _row_index_of(content_layout, dashboard.global_map)
    assert map_row is not None
    for card in (
        dashboard.current_situation_card,
        dashboard.model_agreement_card,
        dashboard.airport_table,
    ):
        assert _row_index_of(content_layout, card) == map_row


def test_the_hazard_row_shares_that_row_too(qapp):
    """In the reference image the AWCI GLOBAL gauge + 6 hazard cards stop
    where the Current Situation column begins - so the hazard row belongs
    in the map's own left column, not in a full-width row of its own."""
    dashboard = AWCIDashboard()
    content_layout = dashboard.global_map.parentWidget().layout()

    assert _row_index_of(content_layout, dashboard.hazard_row) == _row_index_of(
        content_layout, dashboard.global_map
    )


def test_the_right_column_is_really_narrower_than_the_map_column(qapp):
    """Measured on a really-laid-out dashboard, not from stretch factors:
    the reference image gives its right column roughly a quarter of the
    content width and the map the rest."""
    dashboard = _laid_out_dashboard()

    map_width = dashboard.global_map.width()
    column_left = min(
        dashboard.current_situation_card.x(),
        dashboard.airport_table.x(),
    )
    column_right = max(
        dashboard.model_agreement_card.x() + dashboard.model_agreement_card.width(),
        dashboard.airport_table.x() + dashboard.airport_table.width(),
    )
    column_width = column_right - column_left

    assert column_width < map_width
    share = column_width / (column_width + map_width)
    assert 0.22 <= share <= 0.38, f"right column took {share:.0%} of the row"


def test_the_right_column_really_sits_beside_the_map_not_above_it(qapp):
    """Geometry, not layout bookkeeping: every one of the three cards
    starts to the RIGHT of the map's right edge, and the column's own
    vertical span really overlaps the map's."""
    dashboard = _laid_out_dashboard()

    map_right = dashboard.global_map.mapTo(dashboard, dashboard.global_map.rect().topRight()).x()
    for card in (
        dashboard.current_situation_card,
        dashboard.model_agreement_card,
        dashboard.airport_table,
    ):
        card_left = card.mapTo(dashboard, card.rect().topLeft()).x()
        assert card_left >= map_right, f"{type(card).__name__} is not beside the map"

    map_top = dashboard.global_map.mapTo(dashboard, dashboard.global_map.rect().topLeft()).y()
    map_bottom = map_top + dashboard.global_map.height()
    table_top = dashboard.airport_table.mapTo(dashboard, dashboard.airport_table.rect().topLeft()).y()
    assert table_top < map_bottom  # really overlapping the map's own band


def test_moving_the_situation_row_really_shortened_the_whole_dashboard(qapp):
    """The freed vertical space is the measurable point of the move: the
    content column's own size hint must now be materially shorter than the
    ~1880px it was while those cards had a full-width row of their own."""
    dashboard = AWCIDashboard(screen_scale=1.0)
    content_widget = dashboard.global_map.parentWidget()

    assert content_widget.sizeHint().height() <= 1720


# ---------------------------------------- the situation cards' own wiring is intact


def test_the_relocated_cards_keep_their_real_signal_wiring(qapp, monkeypatch):
    """Only their parent/layout position changed - the airport table's
    real "View all airports" button must still open the dashboard's own
    real dialog (the connection is made at construction time, so the
    method is patched on the CLASS, before the dashboard is built), and
    the cards must still be fed by refresh()."""
    opened: list[object] = []
    monkeypatch.setattr(
        AWCIDashboard, "_open_all_airports_dialog", lambda self, *_a, **_k: opened.append(1)
    )
    dashboard = AWCIDashboard()

    dashboard.refresh()
    dashboard.airport_table.view_all_button.click()

    assert opened == [1]
    assert dashboard.current_situation_card.confidence_value_label.text().endswith("%")
    assert dashboard.airport_table._rows_layout.count() > 0


def test_the_airport_table_keeps_its_rows_under_its_header_when_stretched(qtbot):
    """The card is routinely taller than its content in the new right
    column; without a trailing stretch Qt opened a wide empty band between
    its title and its rows."""
    table = AWCIAirportTable()
    qtbot.addWidget(table)
    table.update_data([
        {"icao": "DAAG", "awci": 33.0, "trend": "→", "level": "Low"},
        {"icao": "HLLT", "awci": 40.0, "trend": "→", "level": "Moderate"},
    ])
    table.resize(320, 460)
    table.show()
    QApplication.processEvents()

    first_row_label = table._rows_layout.itemAt(0).layout().itemAt(0).widget()
    # the first real row starts in the card's own top half, not floated
    # down into the middle of a 460px-tall card
    assert first_row_label.y() < table.height() * 0.4
    # ...and the "View all airports" link is pushed to the bottom
    assert table.view_all_button.y() > table.height() * 0.7


# ------------------------------------------- second-row card title clipping


def test_the_analysis_panels_are_no_longer_squeezed_by_the_route_selector(qapp):
    """The Flight Route Analysis panel's two long airport combos used to
    floor its minimum width at ~650px inside a 5-panel row, squeezing the
    Vertical Cross Section and Atmospheric Profile panels to ~84px and
    clipping their titles to "VERTICAL"."""
    dashboard = _laid_out_dashboard()

    assert dashboard.cross_section.width() >= 180
    assert dashboard.atmospheric_profile.width() >= 180
    # ...and the route panel no longer takes more than its neighbours can
    # afford: at most ~1.6x the narrowest sibling, not ~7x.
    assert dashboard.route_chart.width() <= dashboard.cross_section.width() * 1.6


def test_the_route_selectors_minimum_width_is_no_longer_floored_by_its_longest_airport(qapp):
    dashboard = AWCIDashboard()

    for combo in (dashboard.route_from_selector, dashboard.route_to_selector):
        assert combo.minimumContentsLength() == 12
        # every real airport is still selectable - no item was shortened
        assert combo.count() > 1
        assert any("Algiers" in combo.itemText(i) for i in range(combo.count()))


def test_the_cross_section_card_uses_the_reference_images_own_short_title(qapp):
    dashboard = AWCIDashboard()

    assert dashboard.cross_section._base_title == "VERTICAL CROSS SECTION"


def test_a_cross_section_label_goes_on_its_own_second_line(qtbot):
    """A one-line "<title> — <label>" clips in a ~250px-wide card; the
    label is still shown in full, on a second line."""
    import numpy as np

    panel = AWCICrossSection("VERTICAL CROSS SECTION")
    qtbot.addWidget(panel)
    panel.set_external_cross_section(
        np.array([0.0, 100.0]), np.array([500.0, 300.0]), np.array([[10.0, 20.0], [30.0, 40.0]]),
        "IMPORTED MODEL",
    )

    assert panel._title.splitlines() == ["VERTICAL CROSS SECTION", "IMPORTED MODEL"]
