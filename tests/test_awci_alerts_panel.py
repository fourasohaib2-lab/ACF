"""
Tests for acf.gui.dashboard.awci_alerts_panel - real, non-fabricated
active alerts (explicit user request "un autre bouton pour les
alertes"). Every alert here must be traceable to a real, already-
computed AWCI module score or a real decoded METAR field - never a
second, independent guess.
"""

from __future__ import annotations

from acf.aviation.icao.live_source import LiveStationBundle
from acf.aviation.icao.metar_decoder import METARDecoder
from acf.gui.dashboard.awci_alerts_panel import (
    AWCIAlertsDialog,
    compute_elevated_risks,
    compute_live_condition_flags,
    count_active_alerts,
)


def test_no_elevated_risks_when_every_score_is_low():
    module_scores = {"dynamic": 5.0, "thermodynamic": 5.0, "convective": 5.0, "microphysical": 5.0, "topographic": 5.0, "temporal": 5.0}
    elevated = compute_elevated_risks(module_scores, overall_awci=10.0, physical_score=10.0, forecast_score=10.0)
    assert elevated == []


def test_elevated_risk_appears_only_at_high_or_above():
    """Real regression guard: Moderate (35-49) must NOT be treated as
    an alert - only High/Very High/Extreme, matching the dialog's own
    documented scope."""
    module_scores = {"dynamic": 40.0}  # Moderate under AWCIRiskSummary's own _band()
    elevated = compute_elevated_risks(module_scores, overall_awci=0.0, physical_score=None, forecast_score=None)
    assert elevated == []

    module_scores_high = {"dynamic": 55.0}  # High
    elevated_high = compute_elevated_risks(module_scores_high, overall_awci=0.0, physical_score=None, forecast_score=None)
    assert len(elevated_high) == 1
    assert elevated_high[0][2] == "High"


def test_elevated_risks_are_real_not_fabricated_reusing_risk_summarys_own_bands():
    """Turbulence=dynamic, Convective=convective, Icing=microphysical -
    same real mapping AWCIRiskSummary itself uses (imported directly,
    not re-derived)."""
    module_scores = {"dynamic": 90.0, "convective": 90.0, "microphysical": 90.0}
    elevated = compute_elevated_risks(module_scores, overall_awci=90.0, physical_score=None, forecast_score=None)
    labels = {label for _icon, label, _level, _score in elevated}
    assert "Turbulence Risk" in labels
    assert "Convective Risk" in labels
    assert "Icing Risk" in labels
    assert "Overall Complexity" in labels


def test_none_physical_forecast_scores_are_honestly_skipped_not_treated_as_zero():
    """A None physical_score/forecast_score means AWCICalculator itself
    couldn't renormalize it - must not silently become a fabricated
    'Low' or 'High' alert row."""
    elevated = compute_elevated_risks({}, overall_awci=0.0, physical_score=None, forecast_score=None)
    labels = {label for _icon, label, _level, _score in elevated}
    assert "Physical Complexity" not in labels
    assert "Forecast Complexity" not in labels


def _metar_with(raw: str):
    bundle = LiveStationBundle(icao_code="TEST")
    bundle.metar.raw_text = raw
    bundle.metar.decoded = METARDecoder.decode(raw)
    return bundle


def test_live_condition_flags_empty_without_any_fetch():
    assert compute_live_condition_flags(None) == []
    assert compute_live_condition_flags({}) == []


def test_live_condition_flags_detect_a_real_thunderstorm():
    bundle = _metar_with("METAR TEST 030000Z 12010KT 8000 TSRA BKN020 20/18 Q1013")
    flags = compute_live_condition_flags({"TEST": bundle})
    assert any("Thunderstorm" in f for f in flags)


def test_live_condition_flags_detect_a_real_strong_gust():
    bundle = _metar_with("METAR TEST 030000Z 12025G45KT 9999 SCT020 20/18 Q1013")
    flags = compute_live_condition_flags({"TEST": bundle})
    assert any("Strong wind gusts" in f and "45" in f for f in flags)


def test_live_condition_flags_detect_real_low_visibility():
    bundle = _metar_with("METAR TEST 030000Z 12005KT 0800 FG OVC002 05/05 Q1013")
    flags = compute_live_condition_flags({"TEST": bundle})
    assert any("Low visibility" in f for f in flags)


def test_live_condition_flags_stay_quiet_for_a_real_calm_metar():
    bundle = _metar_with("METAR TEST 030000Z 09005KT CAVOK 20/10 Q1020")
    flags = compute_live_condition_flags({"TEST": bundle})
    assert flags == []


def test_count_active_alerts_matches_the_sum_of_both_real_sources():
    module_scores = {"dynamic": 90.0}
    bundle = _metar_with("METAR TEST 030000Z 12025G45KT 9999 TSRA SCT020 20/18 Q1013")
    count = count_active_alerts(module_scores, overall_awci=90.0, physical_score=None, forecast_score=None, live_bundles={"TEST": bundle})
    elevated = compute_elevated_risks(module_scores, 90.0, None, None)
    flags = compute_live_condition_flags({"TEST": bundle})
    assert count == len(elevated) + len(flags)


def test_dialog_refresh_shows_an_honest_no_elevated_risk_state(qtbot):
    dialog = AWCIAlertsDialog()
    qtbot.addWidget(dialog)
    dialog.refresh({}, overall_awci=0.0, physical_score=None, forecast_score=None, live_bundles=None)
    assert dialog.risk_rows_container.count() == 1  # the honest "no elevated risk" row


def test_dialog_refresh_shows_real_elevated_rows(qtbot):
    dialog = AWCIAlertsDialog()
    qtbot.addWidget(dialog)
    dialog.refresh({"dynamic": 90.0, "convective": 90.0}, overall_awci=90.0, physical_score=None, forecast_score=None, live_bundles=None)
    assert dialog.risk_rows_container.count() >= 2


def test_dialog_refresh_shows_honest_no_live_data_state_before_any_fetch(qtbot):
    dialog = AWCIAlertsDialog()
    qtbot.addWidget(dialog)
    dialog.refresh({}, overall_awci=0.0, physical_score=None, forecast_score=None, live_bundles=None)
    live_text = dialog.live_rows_container.itemAt(0).widget().text()
    assert "No live station data fetched yet" in live_text


def test_dialog_refresh_is_idempotent_not_appending_stale_rows(qtbot):
    """Calling refresh() twice must not leave the previous call's rows
    behind (a real regression this dialog's own _clear_layout() exists
    to prevent)."""
    dialog = AWCIAlertsDialog()
    qtbot.addWidget(dialog)
    dialog.refresh({"dynamic": 90.0}, overall_awci=90.0, physical_score=None, forecast_score=None, live_bundles=None)
    first_count = dialog.risk_rows_container.count()
    dialog.refresh({"dynamic": 90.0}, overall_awci=90.0, physical_score=None, forecast_score=None, live_bundles=None)
    assert dialog.risk_rows_container.count() == first_count
