"""
Tests for acf.awci.validation_cases - real validation-case schema and
store (docs/ACF_MASTER_PROMPT.md section 36). This session's
exhaustive 90-section conformance audit (reports/ACF_MASTER_AUDIT_v2.md)
found this genuinely absent from the codebase before this module.

Every case constructed here is clearly-labeled synthetic example data
for testing the real schema/store mechanics - this module's own
docstring discloses it ships with zero real historical cases.
"""

from __future__ import annotations

import json
from datetime import date

import pytest

from acf.awci.validation_cases import (
    CaseDatabase,
    CaseNotFoundError,
    DuplicateCaseIdError,
    ValidationCase,
    WeatherRegime,
)


def _case(case_id: str = "CASE-2026-001", regime: WeatherRegime = WeatherRegime.CONVECTIVE, region: str = "Alger") -> ValidationCase:
    return ValidationCase(
        case_id=case_id,
        date=date(2026, 6, 15),
        region=region,
        season="summer",
        weather_regime=regime,
        model_runs={"AROME": "2026061500"},
        observations={"metar": "DAAG 151200Z 24015KT 9999 SCT030 30/18 Q1010"},
        operational_impact="Moderate turbulence reported on approach.",
    )


def test_new_database_is_genuinely_empty():
    db = CaseDatabase()
    assert len(db) == 0
    assert db.all_cases() == []


def test_add_and_get_a_real_case():
    db = CaseDatabase()
    case = _case()
    db.add_case(case)
    assert len(db) == 1
    assert db.get_case("CASE-2026-001") is case


def test_add_case_rejects_a_duplicate_case_id():
    db = CaseDatabase()
    db.add_case(_case())
    with pytest.raises(DuplicateCaseIdError, match="CASE-2026-001"):
        db.add_case(_case())


def test_get_case_raises_for_an_unknown_id():
    db = CaseDatabase()
    with pytest.raises(CaseNotFoundError):
        db.get_case("does-not-exist")


def test_update_case_replaces_an_existing_entry():
    db = CaseDatabase()
    db.add_case(_case())
    updated = _case()
    updated.awci = 42.0
    db.update_case(updated)
    assert db.get_case("CASE-2026-001").awci == 42.0


def test_update_case_raises_for_an_unknown_id():
    db = CaseDatabase()
    with pytest.raises(CaseNotFoundError):
        db.update_case(_case())


def test_cases_by_regime_filters_correctly():
    db = CaseDatabase()
    db.add_case(_case("CASE-1", WeatherRegime.CONVECTIVE))
    db.add_case(_case("CASE-2", WeatherRegime.FOG))
    db.add_case(_case("CASE-3", WeatherRegime.CONVECTIVE))

    convective = db.cases_by_regime(WeatherRegime.CONVECTIVE)
    assert {c.case_id for c in convective} == {"CASE-1", "CASE-3"}


def test_cases_by_region_filters_correctly():
    db = CaseDatabase()
    db.add_case(_case("CASE-1", region="Alger"))
    db.add_case(_case("CASE-2", region="Oran"))

    assert [c.case_id for c in db.cases_by_region("Oran")] == ["CASE-2"]


def test_cases_with_expert_assessment_only_returns_ones_that_actually_have_one():
    db = CaseDatabase()
    without = _case("CASE-1")
    with_assessment = _case("CASE-2")
    with_assessment.expert_assessment = "Correctly flagged as high complexity by the on-duty forecaster."
    db.add_case(without)
    db.add_case(with_assessment)

    assert [c.case_id for c in db.cases_with_expert_assessment()] == ["CASE-2"]


def test_regime_coverage_counts_every_real_category_including_zero():
    db = CaseDatabase()
    db.add_case(_case("CASE-1", WeatherRegime.CONVECTIVE))

    coverage = db.regime_coverage()
    assert coverage[WeatherRegime.CONVECTIVE] == 1
    assert coverage[WeatherRegime.FOG] == 0
    assert set(coverage.keys()) == set(WeatherRegime)


def test_compute_error_requires_a_real_awci_score_first():
    db = CaseDatabase()
    db.add_case(_case())
    with pytest.raises(ValueError, match="no real 'awci' score"):
        db.compute_error("CASE-2026-001", ground_truth=50.0)


def test_compute_error_is_real_absolute_difference_and_is_stored_back():
    db = CaseDatabase()
    case = _case()
    case.awci = 62.0
    db.add_case(case)

    error = db.compute_error("CASE-2026-001", ground_truth=55.0)

    assert error == pytest.approx(7.0)
    assert db.get_case("CASE-2026-001").error == pytest.approx(7.0)


def test_to_json_and_from_json_round_trip(tmp_path):
    db = CaseDatabase()
    case = _case()
    case.awci = 71.5
    case.expert_assessment = "Real forecaster note."
    db.add_case(case)
    path = tmp_path / "cases.json"

    db.to_json(path)
    reloaded = CaseDatabase.from_json(path)

    assert len(reloaded) == 1
    reloaded_case = reloaded.get_case("CASE-2026-001")
    assert reloaded_case.date == case.date
    assert reloaded_case.weather_regime == case.weather_regime
    assert reloaded_case.awci == case.awci
    assert reloaded_case.expert_assessment == case.expert_assessment


def test_to_json_writes_real_valid_json(tmp_path):
    db = CaseDatabase()
    db.add_case(_case())
    path = tmp_path / "cases.json"
    db.to_json(path)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload[0]["case_id"] == "CASE-2026-001"
    assert payload[0]["weather_regime"] == "convective"


def test_validation_case_accepts_a_real_regime_string():
    """A real caller loading from JSON/a dict passes the enum's own
    string value - __post_init__ must accept it, not require the
    caller to construct the enum member first."""
    case = ValidationCase(
        case_id="X",
        date=date(2026, 1, 1),
        region="Test",
        season="winter",
        weather_regime="fog",
    )
    assert case.weather_regime == WeatherRegime.FOG


def test_weather_regime_covers_all_10_categories_from_section_36():
    expected = {
        "simple",
        "complex",
        "convective",
        "wind",
        "icing",
        "fog",
        "mountainous",
        "high_model_divergence",
        "low_operational_impact",
        "high_operational_impact",
    }
    assert {r.value for r in WeatherRegime} == expected
