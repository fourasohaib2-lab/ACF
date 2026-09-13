from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_model_agreement import ModelAgreementPanel


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


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


def test_model_agreement_with_no_real_models_is_honest(qapp, qtbot):
    panel = ModelAgreementPanel()
    qtbot.addWidget(panel)
    panel.update_from_disagreement({}, None)
    assert panel.model_scores == {}
    assert "NOT_COMPUTED" in panel.verdict_label.text()
