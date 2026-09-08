"""
Tests for acf.gui.esoc.panel_manager.ProductsPanel - the real Weather
Bulletins / Aviation SIGMETs / Hydrological Warnings panel closing the
previously-empty "Products" System Explorer category (2026-09-04,
sixth of 7 ESOC categories with no real panel).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.aviation.icao.sigmet_decoder import SIGMETDecoder
from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import ProductsPanel
from acf.hydrology.flooding.flood_engine import FloodForecastEngine
from acf.reports.briefings.briefing_generator import BriefingGenerator

_REAL_SIGMET = (
    "LFFF SIGMET 1 VALID 041200/041600 LFPW- LFFF PARIS FIR SEV TURB "
    "FCST AT 1200Z FL100/FL340 MOV E 25KT="
)


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def registry():
    return ModuleRegistry()


def test_bulletin_requires_a_real_synoptic_summary(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = ProductsPanel(registry, dispatcher)

    panel.bulletin_summary.setText("")
    panel.bulletin_button.click()

    assert "⚠" in panel.bulletin_result.toPlainText()


def test_bulletin_matches_the_real_generator_directly(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = ProductsPanel(registry, dispatcher)

    panel.bulletin_summary.setText("Deep low pressure system tracking NE.")
    panel.bulletin_type.setCurrentText("Marine Briefing")
    panel.bulletin_button.click()

    expected = BriefingGenerator.generate_briefing(
        briefing_type="Marine Briefing", synoptic_summary="Deep low pressure system tracking NE."
    )
    # Timestamp differs by real wall-clock seconds - compare the
    # content minus the real generated timestamp line.
    result_lines = panel.bulletin_result.toPlainText().splitlines()
    expected_lines = expected["content"].splitlines()
    assert result_lines[0] == expected_lines[0]
    assert "Deep low pressure system tracking NE." in panel.bulletin_result.toPlainText()


def test_sigmet_decodes_a_real_valid_message_matching_the_decoder_directly(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = ProductsPanel(registry, dispatcher)

    panel.sigmet_input.setText(_REAL_SIGMET)
    panel.sigmet_button.click()

    expected = SIGMETDecoder.decode(_REAL_SIGMET)
    text = panel.sigmet_result.toPlainText()
    assert expected.fir_code in text
    assert expected.phenomenon in text
    assert str(expected.flight_level_bottom) in text
    assert str(expected.flight_level_top) in text


def test_sigmet_honestly_rejects_an_invalid_message(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = ProductsPanel(registry, dispatcher)

    panel.sigmet_input.setText("garbage not a real sigmet")
    panel.sigmet_button.click()

    assert "⚠" in panel.sigmet_result.toPlainText()


def test_sigmet_requires_real_input_text(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = ProductsPanel(registry, dispatcher)

    panel.sigmet_input.setText("")
    panel.sigmet_button.click()

    assert "⚠" in panel.sigmet_result.toPlainText()


def test_flood_risk_computed_on_construction_matches_the_real_engine_directly(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = ProductsPanel(registry, dispatcher)

    expected = FloodForecastEngine().evaluate_flash_flood_risk(
        precip_3h_mm=panel.flood_precip.value(),
        soil_saturation_pct=panel.flood_saturation.value(),
        basin_slope_m_km=panel.flood_slope.value(),
        basin_area_km2=panel.flood_area.value(),
    )
    text = panel.flood_result.toPlainText()
    assert str(expected["flash_flood_index"]) in text
    assert expected["risk_level"] in text
    assert str(expected["estimated_peak_discharge_m3_s"]) in text


def test_flood_risk_genuinely_varies_with_real_input(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = ProductsPanel(registry, dispatcher)

    panel.flood_precip.setValue(5.0)
    panel.flood_saturation.setValue(10.0)
    panel.flood_button.click()
    low_risk_text = panel.flood_result.toPlainText()

    panel.flood_precip.setValue(150.0)
    panel.flood_saturation.setValue(95.0)
    panel.flood_button.click()
    high_risk_text = panel.flood_result.toPlainText()

    assert low_risk_text != high_risk_text
    assert "GREEN" in low_risk_text or "MODERATE" in low_risk_text
    assert "RED" in high_risk_text or "CRITICAL" in high_risk_text
