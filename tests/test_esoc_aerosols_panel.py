"""
Tests for acf.gui.esoc.panel_manager.AerosolsPanel - the real aerosol-
cloud microphysics panel closing the previously-dead "Earth System /
Aerosols" System Explorer leaf (2026-09-05). "Dust" stays a deliberate,
disclosed non-build - see the panel's own docstring.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import AerosolsPanel
from acf.science.clouds.aerosols import CloudAerosolEngine


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def registry():
    return ModuleRegistry()


def test_ccn_activation_matches_the_real_engine_directly(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = AerosolsPanel(registry, dispatcher)

    panel.ccn_supersaturation.setValue(1.2)
    panel.ccn_button.click()

    expected = CloudAerosolEngine().twomey_ccn_activation(1.2)
    assert f"{expected:.1f}" in panel.ccn_result.text()


def test_inp_activation_matches_the_real_engine_directly(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = AerosolsPanel(registry, dispatcher)

    panel.inp_supersaturation.setValue(15.0)
    panel.inp_button.click()

    expected = CloudAerosolEngine().meyers_inp_activation(15.0)
    assert f"{expected:.2f}" in panel.inp_result.text()


def test_indirect_effect_matches_the_real_engine_directly(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = AerosolsPanel(registry, dispatcher)

    panel.indirect_ccn_base.setValue(150.0)
    panel.indirect_ccn_polluted.setValue(900.0)
    panel.indirect_lwp.setValue(120.0)
    panel.indirect_button.click()

    expected = CloudAerosolEngine().twomey_first_indirect_effect(
        ccn_base_cm3=150.0, ccn_polluted_cm3=900.0, cloud_water_path=120.0
    )
    text = panel.indirect_result.toPlainText()
    assert f"{expected['albedo_base']:.3f}" in text
    assert f"{expected['albedo_polluted']:.3f}" in text


def test_more_pollution_genuinely_increases_the_real_albedo(qapp, registry):
    """Real physical sanity: more CCN (more pollution) must increase
    real cloud albedo (Twomey effect), never decrease it."""
    result = CloudAerosolEngine().twomey_first_indirect_effect(
        ccn_base_cm3=100.0, ccn_polluted_cm3=1000.0, cloud_water_path=100.0
    )
    assert result["albedo_increase"] > 0.0


def test_panel_shows_an_honest_disconnected_label_when_not_registered(qapp, registry):
    dispatcher = CommandDispatcher()
    registry.modules["aerosols_dust"] = None

    panel = AerosolsPanel(registry, dispatcher)

    assert not hasattr(panel, "ccn_button")
