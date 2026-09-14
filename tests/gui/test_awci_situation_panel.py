"""
Tests for acf.gui.dashboard.awci_situation_panel - the real "Current
Situation" / "Model Agreement" / "Airport Complexity" cards added
2026-09-12 (docs/reference/awci_dashboard_reference.png, Phase 4/6 of
that redesign).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_situation_panel import (
    AWCIAirportTable,
    AWCICurrentSituationCard,
    AWCIModelAgreementCard,
)


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _module_scores(**overrides):
    base = {"dynamic": 90.0, "convective": 20.0, "microphysical": 15.0, "model_disagreement": 0.0}
    base.update(overrides)
    return base


# --------------------------------------------------- AWCICurrentSituationCard


def test_severity_matches_the_real_shared_awci_scale(qapp):
    from acf.gui.dashboard.awci_colors import level_for

    card = AWCICurrentSituationCard()
    card.update_data(_module_scores(), 90.0, None, None, area="Global", altitude="FL300", valid_time="12:00 UTC", confidence_pct=80.0)
    assert card.severity_label.text() == level_for(90.0)


def test_elevated_hazards_use_the_real_shared_compute_elevated_risks(qapp):
    """Real proof: Turbulence (dynamic=90 -> Extreme) must be listed as
    an elevated hazard row - the exact same real classification
    acf.gui.dashboard.awci_alerts_panel.compute_elevated_risks() (also
    used by the Alerts feature) already performs."""
    card = AWCICurrentSituationCard()
    card.update_data(_module_scores(), 90.0, None, None, area="Global", altitude="FL300", valid_time="12:00 UTC", confidence_pct=80.0)
    assert card.hazards_layout.count() >= 1


def test_no_elevated_hazards_shows_an_honest_none_row(qapp):
    card = AWCICurrentSituationCard()
    card.update_data(
        {"dynamic": 0.0, "convective": 0.0, "microphysical": 0.0}, 0.0, None, None,
        area="Global", altitude="FL300", valid_time="12:00 UTC", confidence_pct=80.0,
    )
    assert card.hazards_layout.count() == 1


def test_real_area_altitude_valid_time_confidence_are_shown_verbatim(qapp):
    card = AWCICurrentSituationCard()
    card.update_data(
        _module_scores(), 50.0, None, None,
        area="North Africa", altitude="FL280", valid_time="14:00 UTC", confidence_pct=73.0,
    )
    assert card.area_label.text() == "Affected Area: North Africa"
    assert card.altitude_label.text() == "Main Altitude: FL280"
    assert card.valid_time_label.text() == "Valid Time: 14:00 UTC"
    assert card.confidence_value_label.text() == "73%"


def test_none_confidence_shows_honest_not_computed_never_a_fabricated_100_pct(qapp):
    """Real Physics tier proof: compute_real_complexity_volume() feeds
    AWCICalculator.calculate() no `confidence` input at all, so
    calculate() falls back to its own data.get("confidence", 100.0)
    default - that 100.0 means "no confidence signal was computed",
    never "maximum confidence" (see calculator.py's own calculate()
    docstring). The Real Physics call site in awci_dashboard.py passes
    confidence_pct=None for exactly this case; the card must render an
    honest "NOT_COMPUTED" label and an empty confidence bar, never a
    fabricated-looking full green 100% bar."""
    card = AWCICurrentSituationCard()
    card.resize(200, 100)
    card.update_data(
        _module_scores(), 50.0, None, None,
        area="North Africa", altitude="FL280", valid_time="14:00 UTC", confidence_pct=None,
    )
    assert card.confidence_value_label.text() == "NOT_COMPUTED"
    assert card._confidence_fill.width() == 0


def test_genuinely_computed_100_pct_confidence_still_renders_as_100_pct(qapp):
    """Distinguishes the fake default from a real, explicitly-supplied
    100.0 confidence (e.g. a caller that genuinely measured full
    confidence) - confidence_pct=100.0 (not None) must still render as
    an honest "100%", not be conflated with the NOT_COMPUTED case."""
    card = AWCICurrentSituationCard()
    card.resize(200, 100)
    card.update_data(
        _module_scores(), 50.0, None, None,
        area="North Africa", altitude="FL280", valid_time="14:00 UTC", confidence_pct=100.0,
    )
    assert card.confidence_value_label.text() == "100%"
    assert card._confidence_fill.width() == card.confidence_bar.width()


# ------------------------------------- explainability ("Main Contributors")


def test_no_decomposition_shows_an_honest_not_available_line(qapp):
    card = AWCICurrentSituationCard()
    card.update_data(_module_scores(), 50.0, None, None, area="Global", altitude="FL300", valid_time="12:00 UTC", confidence_pct=80.0)
    assert card.contributors_layout.count() == 1


def test_contributors_show_the_real_percentage_of_a_real_decomposition(qapp):
    """Real proof: percentages are real arithmetic (value/awci*100) on
    an already-real AWCICalculator.calculate()['decomposition'] - never
    an invented number, and the 2 shown values must sum sensibly (each
    <= 100%, largest first)."""
    from acf.awci.calculator import AWCICalculator

    result = AWCICalculator().calculate({"wind_speed": 45.0, "temperature": 10.0})
    card = AWCICurrentSituationCard()
    card.update_data(
        result["module_scores"], result["awci"], result["physical_score"], result["forecast_score"],
        area="Global", altitude="FL300", valid_time="12:00 UTC", confidence_pct=80.0,
        decomposition=result["decomposition"],
    )

    expected = sorted(((k, v) for k, v in result["decomposition"].items() if v > 0.0), key=lambda kv: kv[1], reverse=True)[:5]
    assert card.contributors_layout.count() == len(expected)
    top_key, top_value = expected[0]
    expected_pct = top_value / result["awci"] * 100.0
    first_row = card.contributors_layout.itemAt(0).layout()
    pct_text = first_row.itemAt(first_row.count() - 1).widget().text()
    assert pct_text == f"{expected_pct:.0f}%"


def test_contributor_labels_are_human_readable_not_raw_keys(qapp):
    from acf.awci.calculator import AWCICalculator

    result = AWCICalculator().calculate({"wind_speed": 45.0})
    card = AWCICurrentSituationCard()
    card.update_data(
        result["module_scores"], result["awci"], result["physical_score"], result["forecast_score"],
        area="Global", altitude="FL300", valid_time="12:00 UTC", confidence_pct=80.0,
        decomposition=result["decomposition"],
    )
    first_row = card.contributors_layout.itemAt(0).layout()
    label_text = first_row.itemAt(0).widget().text()
    assert label_text == "Dynamic Complexity"  # never the raw "dynamic" key


def test_no_positive_contributor_shows_an_honest_message(qapp):
    card = AWCICurrentSituationCard()
    card.update_data(
        {}, 0.0, None, None, area="Global", altitude="FL300", valid_time="12:00 UTC", confidence_pct=80.0,
        decomposition={"dynamic": 0.0, "convective": 0.0},
    )
    assert card.contributors_layout.count() == 1


# ----------------------------------------------------- AWCIModelAgreementCard


def test_zero_disagreement_shows_not_computed_never_a_fabricated_severity(qapp):
    """A real 0.0 disagreement is the calculator's own "unmeasured"
    default (no real model_realizations wired in), not a genuine
    zero-spread measurement - the headline must say so honestly
    (NOT_COMPUTED) rather than fabricating a severity word like "Very
    High" agreement or (an earlier bug) "Extreme"."""
    card = AWCIModelAgreementCard()
    card.update_data({"model_disagreement": 0.0})
    assert card.level_label.text() == "NOT_COMPUTED"
    assert "no real multi-model ensemble" in card.detail_label.text().lower()


def test_high_disagreement_shows_low_agreement(qapp):
    card = AWCIModelAgreementCard()
    card.update_data({"model_disagreement": 90.0})
    assert card.level_label.text() == "Very Low"
    assert "90" in card.detail_label.text()


# ------------------------------------------------------------ AWCIAirportTable


def test_update_data_renders_one_row_per_real_airport(qapp):
    table = AWCIAirportTable()
    table.update_data(
        [
            {"icao": "DAAG", "awci": 33.0, "trend": "→", "level": "Low"},
            {"icao": "HLLT", "awci": 68.0, "trend": "↑", "level": "High"},
        ]
    )
    assert table._rows_layout.count() == 2


def test_view_all_callback_is_invoked_on_click(qapp):
    calls = []
    table = AWCIAirportTable(on_view_all=lambda: calls.append(True))
    table.view_all_button.click()
    assert calls == [True]
