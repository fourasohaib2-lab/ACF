"""
Tests for acf.gui.dashboard.awci_component_detail - real per-module
complexity detail (explicit user request "rend les bouton des
différents complexité utilisable pour rendre tout le details de la
situation"). Every fact in COMPONENT_INFO must match
acf.awci.calculator.AWCICalculator/acf.awci.normalizer.Normalizer's
own real formulas, not a re-derived guess.
"""

from __future__ import annotations

from acf.awci.calculator import AWCICalculator
from acf.awci.normalizer import Normalizer
from acf.gui.dashboard.awci_component_detail import COMPONENT_INFO, AWCIComponentDetailDialog


def test_component_info_covers_all_seven_real_modules():
    assert set(COMPONENT_INFO.keys()) == {
        "dynamic", "thermodynamic", "convective", "microphysical", "topographic", "temporal", "confidence",
    }


def test_dynamic_formula_matches_the_real_normalizer():
    """Cross-check against the REAL Normalizer.normalize_wind(), not a re-typed copy."""
    info = COMPONENT_INFO["dynamic"]
    assert info.real_inputs == ("wind_speed",)
    assert Normalizer.normalize_wind(25.0) == 0.5  # 25/50 - the exact real formula the description claims


def test_convective_formula_matches_the_real_calculator_blend():
    """0.7 CAPE + 0.3 CIN - the exact real blend calculate_module_scores() uses."""
    result = AWCICalculator().calculate_module_scores({"cape": 5000.0, "cin": 0.0})
    assert result["convective"] == 0.7  # 0.7 * (5000/5000) + 0.3 * 0


def test_thermodynamic_formula_matches_the_real_calculator_blend():
    result = AWCICalculator().calculate_module_scores({"temperature": 273.15 + 50.0, "specific_humidity": 0.03})
    assert result["thermodynamic"] == 1.0  # 0.5*1.0 + 0.5*1.0 at the real clip ceiling


def test_confidence_is_real_and_inverted():
    """Lower confidence = higher complexity - a real, documented inversion, not the raw normalized value."""
    result = AWCICalculator().calculate_module_scores({"confidence": 100.0})
    assert result["confidence"] == 0.0
    result_low = AWCICalculator().calculate_module_scores({"confidence": 0.0})
    assert result_low["confidence"] == 1.0


def test_real_in_real_physics_flags_match_the_actual_pipeline():
    """Real, verified fact: only dynamic/thermodynamic are genuinely
    solver-driven in Real Physics mode today (acf.awci.vertical_field.
    compute_real_complexity_volume() supplies no cape/cin/precipitation/
    altitude/temporal_change/confidence)."""
    assert COMPONENT_INFO["dynamic"].real_in_real_physics is True
    assert COMPONENT_INFO["thermodynamic"].real_in_real_physics is True
    for key in ("convective", "microphysical", "topographic", "temporal", "confidence"):
        assert COMPONENT_INFO[key].real_in_real_physics is False, key


def test_dialog_shows_real_score_and_real_inputs_in_demo_mode(qtbot):
    dialog = AWCIComponentDetailDialog()
    qtbot.addWidget(dialog)
    dialog.show_component("dynamic", 79.3, {"wind_speed": 39.65}, "demo")
    assert "79.3" in dialog.score_label.text()
    assert "39.65" in dialog.inputs_label.text()
    assert "REAL" in dialog.badge_label.text()


def test_dialog_shows_honest_default_badge_in_real_physics_mode_for_a_pinned_module(qtbot):
    dialog = AWCIComponentDetailDialog()
    qtbot.addWidget(dialog)
    dialog.show_component("convective", 0.0, {"temperature": 290.0, "wind_speed": 5.0}, "real_physics")
    assert "DEFAULT" in dialog.badge_label.text()
    assert "not supplied" in dialog.inputs_label.text()


def test_dialog_shows_real_badge_in_real_physics_mode_for_a_genuinely_computed_module(qtbot):
    dialog = AWCIComponentDetailDialog()
    qtbot.addWidget(dialog)
    dialog.show_component("dynamic", 15.9, {"wind_speed": 7.956}, "real_physics")
    assert "REAL" in dialog.badge_label.text()
    assert "Real Physics solver" in dialog.badge_label.text()


def test_dialog_shows_the_real_formula_text():
    dialog = AWCIComponentDetailDialog()
    dialog.show_component("dynamic", 50.0, {"wind_speed": 25.0}, "demo")
    assert "normalize_wind" in dialog.formula_label.text()


def test_dialog_shows_the_real_weight_status(qtbot):
    """Explicit user request: docs/ACF_MASTER_PROMPT.md section 80's
    weight-status vocabulary (initial/expert-based/calibrated/
    validated) surfaced in the same explainability dialog - the real
    status from acf.awci.weights.WeightsManager.get_weight_status(),
    not a second, independent guess."""
    dialog = AWCIComponentDetailDialog()
    qtbot.addWidget(dialog)
    dialog.show_component("dynamic", 50.0, {"wind_speed": 25.0}, "demo")
    assert "EXPERT-BASED" in dialog.weight_status_label.text()
    assert "not recalibrated" in dialog.weight_status_label.text()
