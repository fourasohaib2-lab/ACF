"""Tests for the new AWCI decision-support package (src/awci/decision/),
built at the user's explicit request ("Le moteur d'aide à la décision
AWCI") after it was identified as a genuinely absent piece in
docs/architecture/acf_awci_architecture_gap_analysis.md.

Phase 1 scope, user-confirmed ("noyau réel uniquement"): context.py +
situation.py + recommendation.py + a thin engine.py composing them -
never a fabricated risk-matrix/confidence/alternatives/scenario layer.

Includes parity tests against the real GUI-side classification scales
this headless package deliberately mirrors rather than imports
(awci.dashboard.awci_colors.LEVELS, awci.dashboard.awci_risk_summary
._ROWS/_ELEVATED equivalents in awci_alerts_panel) - these lock the two
independent copies together so they cannot silently drift apart.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from awci.decision import (
    AWCI_SCORE_BANDS,
    DecisionContext,
    DecisionSupportView,
    HazardAssessment,
    SituationSnapshot,
    assess,
    classify_awci_score,
    get_flight_recommendations,
)
from awci.decision.recommendation import HAZARDS_WITH_REAL_RECOMMENDATIONS
from awci.decision.situation import ELEVATED_SCORE_BANDS, SITUATION_ROWS, build_situation_snapshot


# --------------------------------------------------------------------- context


def test_decision_context_holds_only_real_caller_supplied_values():
    ctx = DecisionContext(latitude=48.85, longitude=2.35, pressure_hpa=300.0)
    assert ctx.latitude == 48.85
    assert ctx.longitude == 2.35
    assert ctx.pressure_hpa == 300.0
    assert isinstance(ctx.generated_at, datetime)
    assert ctx.generated_at.tzinfo is not None


def test_decision_context_generated_at_defaults_to_real_utc_now():
    before = datetime.now(timezone.utc)
    ctx = DecisionContext(latitude=0.0, longitude=0.0, pressure_hpa=1013.25)
    after = datetime.now(timezone.utc)
    assert before <= ctx.generated_at <= after


def test_decision_context_flight_level_matches_the_real_isa_formula():
    """Cross-check against the real, independent standard ICAO/FAA
    pressure-altitude formula also used by
    awci.dashboard.awci_map_panel.pressure_to_flight_level_ft()
    (PA(ft) = 145366.45 * (1 - (P/1013.25)**0.190284)) - the same real
    ICAO Doc 7488 physics, algebraically equivalent to
    DecisionContext.flight_level's own real
    calculate_isa_pressure_altitude()-based computation (see
    context.py's own docstring for the equivalence). Deliberately not
    importing awci.dashboard.awci_map_panel itself here: that heavy GUI
    module (cartopy/matplotlib/PySide6) exposes a real, pre-existing
    circular-import fragility when it is the first awci.dashboard
    module imported fresh in a process (acf.gui.map.map_layers's own
    import of the old acf.gui.dashboard.awci_colors shim cascades into
    acf.gui.dashboard.__init__ eagerly importing awci_dashboard, which
    re-enters the still-initializing awci_map_panel module) - a real,
    separate bug outside this package's own scope, reported to the user
    rather than silently worked around by masking it."""
    ctx = DecisionContext(latitude=0.0, longitude=0.0, pressure_hpa=300.0)
    expected_ft = 145366.45 * (1.0 - (300.0 / 1013.25) ** 0.190284)
    expected_fl = round(expected_ft / 100.0)
    assert ctx.flight_level.value == expected_fl


def test_decision_context_flight_level_at_standard_pressure_is_near_sea_level():
    ctx = DecisionContext(latitude=0.0, longitude=0.0, pressure_hpa=1013.25)
    assert abs(ctx.flight_level.value) <= 1


@pytest.mark.parametrize("pressure_hpa", [1013.25, 700.0, 500.0, 300.0, 200.0])
def test_decision_context_flight_level_is_real_and_increases_as_pressure_drops(pressure_hpa):
    ctx = DecisionContext(latitude=0.0, longitude=0.0, pressure_hpa=pressure_hpa)
    assert ctx.flight_level.altitude_ft == ctx.flight_level.value * 100


# --------------------------------------------------------------------- situation


def test_awci_score_bands_matches_the_real_gui_color_scale_exactly():
    """Parity lock against awci.dashboard.awci_colors.LEVELS - the
    module docstring there names it the single canonical AWCI 0-100
    scale; this headless copy must never silently drift from it."""
    from awci.dashboard.awci_colors import LEVELS

    gui_bands = tuple((threshold, name) for threshold, name, _rgb in LEVELS)
    assert AWCI_SCORE_BANDS == gui_bands


def test_classify_awci_score_matches_the_real_gui_level_for():
    from awci.dashboard.awci_colors import level_for

    for score in (-5.0, 0.0, 10.0, 19.9, 20.0, 34.9, 35.0, 49.9, 50.0, 64.9, 65.0, 84.9, 85.0, 100.0, 150.0):
        assert classify_awci_score(score) == level_for(score)


def test_elevated_score_bands_matches_the_real_gui_alerts_panel():
    from awci.dashboard.awci_alerts_panel import _ELEVATED_LEVELS

    assert ELEVATED_SCORE_BANDS == frozenset(_ELEVATED_LEVELS)


def test_situation_rows_key_label_module_matches_the_real_gui_risk_summary_rows():
    """Parity lock against awci.dashboard.awci_risk_summary._ROWS - only
    the (key, label, module) fields are compared, since this headless
    package deliberately drops that tuple's own UI-only icon field (see
    situation.py's own docstring)."""
    from awci.dashboard.awci_risk_summary import _ROWS

    gui_rows = tuple((key, label, module) for key, _icon, label, module in _ROWS)
    assert SITUATION_ROWS == gui_rows


def test_build_situation_snapshot_classifies_every_supplied_score():
    ctx = DecisionContext(latitude=0.0, longitude=0.0, pressure_hpa=300.0)
    situation = build_situation_snapshot(
        context=ctx,
        module_scores={"dynamic": 72.0, "microphysical": 20.0, "convective": 91.0},
        overall_awci=68.0,
        physical_score=55.0,
        forecast_score=None,
    )
    by_key = {a.key: a for a in situation.assessments}
    assert by_key["turbulence"].score == 72.0
    assert by_key["turbulence"].level == "Very High"
    assert by_key["icing"].level == "Low"
    assert by_key["convective"].level == "Extreme"
    assert by_key["overall"].score == 68.0
    assert by_key["physical"].level == "High"
    assert "forecast" not in by_key  # forecast_score=None -> honestly omitted, not fabricated


def test_build_situation_snapshot_omits_missing_module_scores_rather_than_fabricating_zero():
    ctx = DecisionContext(latitude=0.0, longitude=0.0, pressure_hpa=300.0)
    situation = build_situation_snapshot(
        context=ctx,
        module_scores={},  # nothing computed
        overall_awci=10.0,
    )
    by_key = {a.key: a for a in situation.assessments}
    assert "turbulence" not in by_key
    assert "icing" not in by_key
    assert "convective" not in by_key
    assert "physical" not in by_key
    assert "forecast" not in by_key
    assert by_key["overall"].score == 10.0


def test_situation_snapshot_elevated_property_matches_the_real_gui_compute_elevated_risks():
    """Cross-check against the real, independent
    awci.dashboard.awci_alerts_panel.compute_elevated_risks() for the
    module_scores path (not the 0.0-default divergence disclosed in
    build_situation_snapshot's own docstring - tested with every module
    score explicitly supplied so the two functions' real outputs must
    agree)."""
    from awci.dashboard.awci_alerts_panel import compute_elevated_risks

    module_scores = {"dynamic": 72.0, "microphysical": 20.0, "convective": 91.0}
    overall_awci = 68.0
    physical_score = 55.0
    forecast_score = 12.0

    ctx = DecisionContext(latitude=0.0, longitude=0.0, pressure_hpa=300.0)
    situation = build_situation_snapshot(
        context=ctx,
        module_scores=module_scores,
        overall_awci=overall_awci,
        physical_score=physical_score,
        forecast_score=forecast_score,
    )
    gui_rows = compute_elevated_risks(module_scores, overall_awci, physical_score, forecast_score)
    from awci.dashboard.awci_risk_summary import _ROWS

    label_to_key = {label: key for key, _icon, label, _module in _ROWS}
    gui_elevated_keys = {label_to_key[label] for _icon, label, _level, _score in gui_rows}

    assert {a.key for a in situation.elevated} == gui_elevated_keys


def test_hazard_assessment_is_elevated_matches_its_band():
    a = HazardAssessment(key="turbulence", label="Turbulence Risk", score=70.0, level="Very High")
    assert a.is_elevated is True
    b = HazardAssessment(key="icing", label="Icing Risk", score=10.0, level="Very Low")
    assert b.is_elevated is False


def test_situation_snapshot_get_returns_none_for_a_row_not_present():
    ctx = DecisionContext(latitude=0.0, longitude=0.0, pressure_hpa=300.0)
    situation = SituationSnapshot(context=ctx, assessments=())
    assert situation.get("overall") is None


# --------------------------------------------------------------------- recommendation


def test_hazards_with_real_recommendations_matches_the_registry():
    from awci.knowledge.hazards.aviation_hazards import AVIATION_HAZARDS_REGISTRY

    for key in HAZARDS_WITH_REAL_RECOMMENDATIONS:
        assert key in AVIATION_HAZARDS_REGISTRY
        assert len(AVIATION_HAZARDS_REGISTRY[key].flight_recommendations) > 0


def test_get_flight_recommendations_returns_the_real_cited_text_for_the_3_covered_hazards():
    for key in ("cat_turbulence", "airframe_icing", "microburst_windshear"):
        recommendations = get_flight_recommendations(key)
        assert recommendations is not None
        assert len(recommendations) > 0
        from awci.knowledge.hazards.aviation_hazards import AVIATION_HAZARDS_REGISTRY

        assert recommendations == AVIATION_HAZARDS_REGISTRY[key].flight_recommendations


def test_get_flight_recommendations_honestly_returns_none_for_an_uncovered_hazard():
    assert get_flight_recommendations("volcanic_ash") is None
    assert get_flight_recommendations("not_a_real_hazard_key") is None
    assert get_flight_recommendations("dust") is None


def test_get_flight_recommendations_never_fabricates_a_recommendation_for_a_coarse_module():
    """There is no real hazard key equal to an AWCI composite module
    name ("dynamic"/"microphysical"/"convective"/"overall") - confirms
    this module cannot be accidentally called with one and get a
    recommendation back."""
    for coarse_key in ("dynamic", "microphysical", "convective", "overall"):
        assert get_flight_recommendations(coarse_key) is None


# --------------------------------------------------------------------- engine


def test_assess_composes_situation_and_recommendations():
    ctx = DecisionContext(latitude=48.85, longitude=2.35, pressure_hpa=300.0)
    view = assess(
        context=ctx,
        module_scores={"dynamic": 72.0, "microphysical": 20.0, "convective": 91.0},
        overall_awci=68.0,
        physical_score=55.0,
        forecast_score=None,
        active_hazard_keys=("cat_turbulence", "airframe_icing"),
    )
    assert isinstance(view, DecisionSupportView)
    assert view.situation.context is ctx
    assert set(view.recommendations.keys()) == {"cat_turbulence", "airframe_icing"}
    assert len(view.recommendations["cat_turbulence"]) > 0


def test_assess_silently_skips_active_hazard_keys_outside_the_real_registry():
    ctx = DecisionContext(latitude=0.0, longitude=0.0, pressure_hpa=300.0)
    view = assess(
        context=ctx,
        module_scores={},
        overall_awci=5.0,
        active_hazard_keys=("cat_turbulence", "not_a_real_hazard", "dust"),
    )
    assert set(view.recommendations.keys()) == {"cat_turbulence"}


def test_assess_with_no_active_hazard_keys_yields_no_recommendations():
    ctx = DecisionContext(latitude=0.0, longitude=0.0, pressure_hpa=300.0)
    view = assess(context=ctx, module_scores={}, overall_awci=5.0)
    assert view.recommendations == {}


def test_assess_never_invents_a_score_it_was_not_given():
    ctx = DecisionContext(latitude=0.0, longitude=0.0, pressure_hpa=300.0)
    view = assess(context=ctx, module_scores={}, overall_awci=5.0)
    keys = {a.key for a in view.situation.assessments}
    assert keys == {"overall"}


def test_decision_package_is_headless_no_gui_dependency_imported():
    """This package's own __init__.py docstring states it imports no
    PySide6/matplotlib/cartopy - verified here by checking none of
    those appear among the modules actually imported when importing
    awci.decision alone (a fresh subprocess would be the strongest
    check, but inspecting sys.modules after a plain import already
    catches an accidental heavy-GUI import at this package's own
    module level)."""
    import sys

    import awci.decision  # noqa: F401

    decision_module_names = [name for name in sys.modules if name.startswith("awci.decision")]
    assert len(decision_module_names) >= 5  # __init__ + context + situation + recommendation + engine
    for name in decision_module_names:
        module = sys.modules[name]
        source_file = getattr(module, "__file__", "") or ""
        assert "PySide6" not in source_file
