"""
Tests for AWCIFooter's 5 real, clickable buttons - explicit user
request ("la barre d'outils en bas ... sont des boutons je veux les
rendre des boutons fonctionnelles"). These used to be purely
decorative QLabel cells (real feature names, no click handler at all)
- see awci_footer.py's own module docstring for what each real key now
does and why (each maps to an existing real dashboard feature its own
label already honestly describes, never a new/fabricated action).
"""

from __future__ import annotations

from unittest.mock import patch

from acf.gui.dashboard.awci_dashboard import AWCIDashboard
from acf.gui.dashboard.awci_footer import AWCIFooter, AWCIFooterCell


def test_footer_has_all_5_real_clickable_cells(qtbot):
    footer = AWCIFooter()
    qtbot.addWidget(footer)

    assert set(footer.cells.keys()) == {
        "synthetic_view",
        "decision_support",
        "multi_scale",
        "adaptive_to_mission",
        "research_stage",
    }
    for cell in footer.cells.values():
        assert isinstance(cell, AWCIFooterCell)


def test_clicking_a_cell_emits_the_real_item_key(qtbot):
    footer = AWCIFooter()
    qtbot.addWidget(footer)
    received = []
    footer.itemClicked.connect(received.append)

    footer.cells["research_stage"].clicked.emit()

    assert received == ["research_stage"]


def test_footer_cell_shows_a_pointing_hand_cursor():
    from PySide6.QtCore import Qt

    cell = AWCIFooterCell("🧪", "RESEARCH STAGE", "desc")
    assert cell.cursor().shape() == Qt.CursorShape.PointingHandCursor


class TestFooterDispatchReachesTheRealDashboardFeature:
    def test_synthetic_view_reverts_to_demo_mode(self, qtbot):
        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)
        dashboard._real_physics_active = True

        with patch.object(dashboard, "_revert_to_demo") as mock_revert:
            dashboard._on_footer_item_clicked("synthetic_view")

        mock_revert.assert_called_once()

    def test_decision_support_opens_real_alerts(self, qtbot):
        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)

        with patch.object(dashboard, "_open_alerts") as mock_alerts:
            dashboard._on_footer_item_clicked("decision_support")

        mock_alerts.assert_called_once()

    def test_adaptive_to_mission_opens_real_vertical_profile(self, qtbot):
        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)

        with patch.object(dashboard, "_open_vertical_profile") as mock_profile:
            dashboard._on_footer_item_clicked("adaptive_to_mission")

        mock_profile.assert_called_once()

    def test_research_stage_opens_real_execution_report(self, qtbot):
        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)

        with patch.object(dashboard, "_open_execution_report") as mock_report:
            dashboard._on_footer_item_clicked("research_stage")

        mock_report.assert_called_once()

    def test_multi_scale_cycles_through_all_3_real_view_modes(self, qtbot):
        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)
        assert dashboard.view_mode_global_radio.isChecked() is True

        dashboard._on_footer_item_clicked("multi_scale")
        assert dashboard.view_mode_regional_radio.isChecked() is True

        dashboard._on_footer_item_clicked("multi_scale")
        assert dashboard.view_mode_cross_section_radio.isChecked() is True

        dashboard._on_footer_item_clicked("multi_scale")
        assert dashboard.view_mode_global_radio.isChecked() is True  # real full cycle back

    def test_multi_scale_genuinely_changes_the_real_map_extent(self, qtbot):
        """Not just a radio-button state flip - the same real map-extent
        change _on_view_mode_changed() already makes for a manual click."""
        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)
        extent_before = dashboard.global_map.camera.current_extent()

        dashboard._on_footer_item_clicked("multi_scale")  # -> Regional

        assert dashboard.global_map.camera.current_extent() != extent_before
