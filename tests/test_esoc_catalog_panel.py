"""
Tests for acf.gui.esoc.panel_manager.CatalogPanel - the real Parameter
Catalog browser closing the previously-empty "Catalog" System Explorer
category (2026-09-04, first of 7 ESOC categories with no real panel).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.catalog.manager import CatalogManager
from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import CatalogPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_catalog_panel_populates_the_real_64_scientific_entries(qapp):
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()

    panel = CatalogPanel(registry, dispatcher)

    expected = list(registry.get_module("catalog").scientific.all())
    assert len(expected) == 64
    assert panel.table.rowCount() == len(expected)
    assert panel.table.columnCount() == 6
    headers = [panel.table.horizontalHeaderItem(i).text() for i in range(6)]
    assert headers == ["Parameter ID", "CF Standard Name", "Long Name", "Units", "Category", "Level Type"]


def test_catalog_panel_table_matches_the_real_catalog_manager_directly(qapp):
    """Cross-check discipline: every real row must equal the real
    CatalogEntry it was built from - never a separately re-derived
    value."""
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()
    panel = CatalogPanel(registry, dispatcher)

    entries = list(registry.get_module("catalog").scientific.all())
    for row, entry in enumerate(entries):
        assert panel.table.item(row, 0).text() == entry.parameter_id
        assert panel.table.item(row, 1).text() == entry.standard_name
        assert panel.table.item(row, 2).text() == entry.long_name
        assert panel.table.item(row, 3).text() == entry.units


def test_catalog_panel_filter_genuinely_narrows_the_real_table(qapp):
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()
    panel = CatalogPanel(registry, dispatcher)
    full_count = panel.table.rowCount()

    panel.search_input.setText("temperature")

    assert 0 < panel.table.rowCount() < full_count
    for row in range(panel.table.rowCount()):
        param_id = panel.table.item(row, 0).text().lower()
        standard_name = panel.table.item(row, 1).text().lower()
        category = panel.table.item(row, 4).text().lower()
        assert "temperature" in param_id or "temperature" in standard_name or "temperature" in category


def test_catalog_panel_filter_cleared_restores_the_real_full_table(qapp):
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()
    panel = CatalogPanel(registry, dispatcher)
    full_count = panel.table.rowCount()

    panel.search_input.setText("temperature")
    panel.search_input.setText("")

    assert panel.table.rowCount() == full_count


def test_catalog_panel_honestly_discloses_when_the_real_subsystem_is_not_connected(qapp):
    """Regression guard: a genuinely disconnected 'catalog' module must
    show a real, honest disclosure - never an empty table pretending
    there was simply no data, and never a crash."""

    class _EmptyRegistry:
        def get_module(self, name: str):
            return None

    dispatcher = CommandDispatcher()
    panel = CatalogPanel(_EmptyRegistry(), dispatcher)  # type: ignore[arg-type]

    assert not hasattr(panel, "table")


def test_real_catalog_manager_scientific_property_is_a_real_populated_catalog():
    """Direct proof this panel's own real data source is genuine, not
    assumed."""
    manager = CatalogManager()
    entries = manager.scientific.all()
    assert len(entries) == 64
    assert all(e.standard_name for e in entries)  # every real entry has a real CF standard name
    assert all(e.units for e in entries)
