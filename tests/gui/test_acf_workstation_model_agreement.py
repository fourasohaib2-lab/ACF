from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QProgressBar

from acf.gui.dashboard.acf_workstation_model_agreement import ModelAgreementPanel


def _flush_deferred_deletes(qapp: QApplication) -> None:
    """`deleteLater()` only schedules a deferred-delete event - it is not
    applied until the event loop actually processes it. Flush that
    explicitly so a `findChildren()` check right after an update reflects
    real widget removal rather than pending-but-not-yet-applied deletes."""
    qapp.sendPostedEvents(None, QEvent.DeferredDelete)
    qapp.processEvents()
    qapp.sendPostedEvents(None, QEvent.DeferredDelete)


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def _temperature_fields() -> dict[str, np.ndarray]:
    # A real, physically-significant ~10 K temperature spread across four
    # models (280 K, 283.5 K, 284 K, 290 K). Old (buggy) normalization by
    # the ensemble mean's own magnitude (~284 K) made every score come out
    # >=0.98 "High Agreement" regardless of this real disagreement.
    return {
        "AROME": np.full((4, 4), 280.0),
        "ALADIN": np.full((4, 4), 283.5),
        "ARPEGE": np.full((4, 4), 284.0),
        "WRF": np.full((4, 4), 290.0),
    }


def test_model_agreement_bars_from_real_per_model_fields(qapp, qtbot):
    panel = ModelAgreementPanel()
    qtbot.addWidget(panel)
    per_model_field = {
        "AROME": np.full((4, 4), 10.0),
        "ALADIN": np.full((4, 4), 10.5),
        "ARPEGE": np.full((4, 4), 9.0),
        "WRF": np.full((4, 4), 12.0),
    }
    spread_field = np.full((4, 4), 1.2)
    panel.update_from_disagreement(per_model_field, spread_field)

    assert set(panel.model_scores.keys()) == {"AROME", "ALADIN", "ARPEGE", "WRF"}
    for score in panel.model_scores.values():
        assert 0.0 <= score <= 1.0
    assert panel.verdict_label.text() in {"High Agreement", "Moderate Agreement", "Low Agreement"}


def test_model_agreement_discriminates_real_high_disagreement(qapp, qtbot):
    """Spread comparable to the real inter-model deviation -> low scores.

    This is the exact scenario the reviewer used to demonstrate the
    original bug: a real, physically-significant 10 K temperature spread
    that used to saturate to ~1.0 ("High Agreement") regardless of the
    real disagreement, because it was normalized against the ensemble
    mean's own ~284 K magnitude instead of against real spread.
    """
    panel = ModelAgreementPanel()
    qtbot.addWidget(panel)
    per_model_field = _temperature_fields()
    # Real spread comparable in magnitude to the real deviations (~4-5.6 K).
    spread_field = np.full((4, 4), 5.0)
    panel.update_from_disagreement(per_model_field, spread_field)

    assert set(panel.model_scores.keys()) == {"AROME", "ALADIN", "ARPEGE", "WRF"}
    # The most-deviating model (WRF, 290 K, 5.625 K from the 284.375 K
    # ensemble mean) must score low once deviation is measured against a
    # real spread of comparable magnitude.
    assert panel.model_scores["WRF"] < 0.2
    overall = sum(panel.model_scores.values()) / len(panel.model_scores)
    assert overall < 0.75
    assert panel.verdict_label.text() in {"Moderate Agreement", "Low Agreement"}


def test_model_agreement_discriminates_real_low_disagreement(qapp, qtbot):
    """Same real per-model deviations, but real spread is much larger ->
    the same absolute deviations are now genuinely small relative to how
    much the models actually disagree, so scores should read high."""
    panel = ModelAgreementPanel()
    qtbot.addWidget(panel)
    per_model_field = _temperature_fields()
    # Real spread far larger than the real deviations (~4-5.6 K).
    spread_field = np.full((4, 4), 50.0)
    panel.update_from_disagreement(per_model_field, spread_field)

    for score in panel.model_scores.values():
        assert score > 0.85
    overall = sum(panel.model_scores.values()) / len(panel.model_scores)
    assert overall >= 0.75
    assert panel.verdict_label.text() == "High Agreement"


def test_model_agreement_with_no_real_models_is_honest(qapp, qtbot):
    panel = ModelAgreementPanel()
    qtbot.addWidget(panel)
    panel.update_from_disagreement({}, None)
    assert panel.model_scores == {}
    assert "NOT_COMPUTED" in panel.verdict_label.text()


def test_model_agreement_clears_stale_rows_on_no_models(qapp, qtbot):
    """Regression: rows were added via `self._rows_layout.addLayout(row)`
    (a QHBoxLayout, not a widget), so the old clear loop's `item.widget()`
    was always None and nothing was ever actually removed - stale
    agreement bars from a previous run survived a later "no models"
    result, showing real-looking bars underneath a
    NOT_COMPUTED_NO_MODELS_AVAILABLE verdict."""
    panel = ModelAgreementPanel()
    qtbot.addWidget(panel)

    panel.update_from_disagreement(
        {
            "AROME": np.full((4, 4), 10.0),
            "ALADIN": np.full((4, 4), 10.5),
        },
        np.full((4, 4), 1.0),
    )
    _flush_deferred_deletes(qapp)
    assert len(panel.findChildren(QProgressBar)) == 2

    panel.update_from_disagreement(
        {
            "ARPEGE": np.full((4, 4), 9.0),
            "WRF": np.full((4, 4), 12.0),
            "AROME": np.full((4, 4), 11.0),
        },
        np.full((4, 4), 1.0),
    )
    _flush_deferred_deletes(qapp)
    assert len(panel.findChildren(QProgressBar)) == 3

    panel.update_from_disagreement({}, None)
    _flush_deferred_deletes(qapp)
    assert panel.model_scores == {}
    assert "NOT_COMPUTED" in panel.verdict_label.text()
    assert len(panel.findChildren(QProgressBar)) == 0
