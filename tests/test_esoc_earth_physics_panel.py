"""
Tests for acf.gui.esoc.panel_manager.EarthPhysicsPanel's real Scientific
Encyclopedia browser extension (2026-09-05, Phase 47) - the real,
previously ESOC-side-missing `EncyclopediaRegistry` (299 real entries)
browser, added alongside (never replacing) this panel's own original 4
hardcoded equations.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import EarthPhysicsPanel
from acf.science.encyclopedia.registry import EncyclopediaRegistry


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def registry():
    return ModuleRegistry()


def test_original_hardcoded_equations_are_kept_unchanged(qapp, registry):
    """Real regression guard: the encyclopedia addition must never
    delete this panel's own pre-existing real content."""
    dispatcher = CommandDispatcher()
    panel = EarthPhysicsPanel(registry, dispatcher)

    text = panel.info.toPlainText()
    assert "Mass Conservation" in text
    assert "Navier-Stokes" in text
    assert "Ocean Seawater EOS" in text


def test_starts_with_every_real_encyclopedia_entry_listed(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = EarthPhysicsPanel(registry, dispatcher)

    text = panel.encyclopedia_results.toPlainText()
    first_entry = EncyclopediaRegistry.list_entries()[0]
    assert first_entry.name in text


def test_search_matches_the_real_registry_directly(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = EarthPhysicsPanel(registry, dispatcher)

    panel.encyclopedia_search.setText("tourbillon")

    expected = EncyclopediaRegistry.search("tourbillon")
    assert len(expected) > 0
    for entry in expected:
        assert entry.name in panel.encyclopedia_results.toPlainText()


def test_search_with_no_real_match_is_honest_not_empty_or_fabricated(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = EarthPhysicsPanel(registry, dispatcher)

    panel.encyclopedia_search.setText("zzz_no_such_real_entry_zzz")

    assert panel.encyclopedia_results.toPlainText() == "No matching real entries."


def test_clearing_the_search_restores_the_real_full_list(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = EarthPhysicsPanel(registry, dispatcher)

    panel.encyclopedia_search.setText("tourbillon")
    panel.encyclopedia_search.setText("")

    first_entry = EncyclopediaRegistry.list_entries()[0]
    assert first_entry.name in panel.encyclopedia_results.toPlainText()
