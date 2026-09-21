"""Tests for the new awci.reports package (generator.py/
aviation_report.py), built while working through the full
remaining-gaps list ("On les attaque toutes un par un") after it was
identified as the specific, named gap in docs/architecture/
acf_awci_architecture_gap_analysis.md ("no standalone
reports/aviation_report.py generator").

aviation_report.py is a real assembler composing 3 already-real,
already-tested systems (awci.airport.weather, awci.decision,
awci.provenance) - no new computation. Tests verify graceful
degradation (every optional section honestly "not available" when its
underlying real data is not supplied) and correct composition when it
is.
"""

from __future__ import annotations

from acf.core.contracts.provenance import Provenance
from awci.complexity.calculator import AWCICalculator
from awci.complexity.result import build_awci_result
from awci.knowledge.icao.live_source import LiveReport, LiveStationBundle
from awci.knowledge.icao.metar_decoder import METARDecoder
from awci.reports.aviation_report import AviationReport, build_aviation_report, format_aviation_report
from awci.reports.generator import ReportSection, render_report

_REAL_KJFK_METAR = "KJFK 211200Z 27015G25KT 3SM -RA BKN008 OVC015 12/10 A2985"

_REAL_INPUT_DATA = {
    "temperature": 250.0,
    "wind": 20.0,
    "wind_shear": 10.0,
    "theta_e": 320.0,
    "humidity": 0.01,
    "cape": 1500.0,
    "updraft_velocity": 15.0,
    "cin": 50.0,
    "precipitation": 5.0,
    "precipitation_phase_severity": 0.3,
    "pressure": 1000.0,
    "topographic": 500.0,
    "confidence": 80.0,
    "temporal": 5.0,
}


class _FakeHub:
    def fetch_station(self, icao_code: str, timeout: float = 8.0) -> LiveStationBundle:
        bundle = LiveStationBundle(icao_code=icao_code)
        bundle.metar = LiveReport(raw_text=_REAL_KJFK_METAR, decoded=METARDecoder.decode(_REAL_KJFK_METAR))
        return bundle


class _FailingHub:
    def fetch_station(self, icao_code: str, timeout: float = 8.0) -> LiveStationBundle:
        bundle = LiveStationBundle(icao_code=icao_code)
        bundle.metar = LiveReport(error=f"{icao_code} fetch failed: network error")
        return bundle


# --------------------------------------------------------------------- generator.py


def test_render_report_includes_title_and_every_section():
    sections = (
        ReportSection(title="Alpha", lines=("line 1", "line 2")),
        ReportSection(title="Beta", lines=("only line",)),
    )
    text = render_report("My Report", sections)
    assert "My Report" in text
    assert "Alpha" in text
    assert "line 1" in text
    assert "Beta" in text
    assert "only line" in text


def test_render_report_shows_not_available_for_an_empty_section():
    sections = (ReportSection(title="Empty", lines=()),)
    text = render_report("Title", sections)
    assert "Empty" in text
    assert "not available" in text


# --------------------------------------------------------------------- aviation_report.py: weather-only


def test_build_aviation_report_weather_only_leaves_decision_and_audit_none():
    report = build_aviation_report("KJFK", hub=_FakeHub())
    assert isinstance(report, AviationReport)
    assert report.icao_code == "KJFK"
    assert report.weather.is_real_data is True
    assert report.decision is None
    assert report.audit is None


def test_format_aviation_report_weather_only_shows_not_available_for_optional_sections():
    report = build_aviation_report("KJFK", hub=_FakeHub())
    text = format_aviation_report(report)
    assert "KJFK" in text
    assert "BKN008" in text or "800" in text  # real ceiling surfaced somehow
    assert text.count("not available") >= 2  # Hazards section + Provenance section


def test_format_aviation_report_weather_only_never_shows_a_fabricated_hazard():
    report = build_aviation_report("KJFK", hub=_FakeHub())
    text = format_aviation_report(report)
    assert "Turbulence Risk" not in text
    assert "Recommendations" not in text


def test_build_aviation_report_honestly_surfaces_a_real_fetch_failure():
    report = build_aviation_report("KJFK", hub=_FailingHub())
    assert report.weather.is_real_data is False
    text = format_aviation_report(report)
    assert "Fetch failed" in text
    assert "network error" in text


# --------------------------------------------------------------------- aviation_report.py: full composition


def _real_calculator_and_output():
    calculator = AWCICalculator()
    output = calculator.calculate(_REAL_INPUT_DATA)
    return calculator, output


def test_build_aviation_report_with_module_scores_populates_decision():
    calculator, output = _real_calculator_and_output()
    report = build_aviation_report(
        "KJFK",
        hub=_FakeHub(),
        module_scores=output["module_scores"],
        overall_awci=output["awci"],
        active_hazard_keys=("cat_turbulence",),
    )
    assert report.decision is not None
    assert report.audit is None
    keys = {a.key for a in report.decision.situation.assessments}
    assert "turbulence" in keys
    assert "cat_turbulence" in report.decision.recommendations


def test_format_aviation_report_with_decision_shows_real_hazard_levels_and_recommendations():
    calculator, output = _real_calculator_and_output()
    report = build_aviation_report(
        "KJFK",
        hub=_FakeHub(),
        module_scores=output["module_scores"],
        overall_awci=output["awci"],
        active_hazard_keys=("cat_turbulence",),
    )
    text = format_aviation_report(report)
    assert "Overall Complexity" in text
    assert "Recommendations:" in text
    assert "[cat_turbulence]" in text


def test_build_aviation_report_with_awci_result_populates_audit():
    calculator, output = _real_calculator_and_output()
    provenance = Provenance(generator="AWCICalculator", algorithm_version="v1")
    result = build_awci_result(output, provenance=provenance)
    report = build_aviation_report("KJFK", hub=_FakeHub(), awci_result=result, calculator=calculator)
    assert report.audit is not None
    assert report.decision is None
    assert report.audit.lineage.model == "v1"


def test_format_aviation_report_with_audit_shows_real_provenance_fields():
    calculator, output = _real_calculator_and_output()
    provenance = Provenance(generator="AWCICalculator", algorithm_version="v1")
    result = build_awci_result(output, provenance=provenance)
    report = build_aviation_report("KJFK", hub=_FakeHub(), awci_result=result, calculator=calculator)
    text = format_aviation_report(report)
    assert "Model: v1" in text
    assert "Fully specified provenance: False" in text
    assert "Missing fields:" in text


def test_build_aviation_report_requires_both_module_scores_and_overall_awci():
    """Decision must stay None if only one of the two required real
    inputs is supplied - never a partial, fabricated situation."""
    calculator, output = _real_calculator_and_output()
    report = build_aviation_report("KJFK", hub=_FakeHub(), module_scores=output["module_scores"])
    assert report.decision is None


def test_full_report_combines_weather_decision_and_audit_together():
    calculator, output = _real_calculator_and_output()
    provenance = Provenance(generator="AWCICalculator", algorithm_version="v1")
    result = build_awci_result(output, provenance=provenance)
    report = build_aviation_report(
        "KJFK",
        hub=_FakeHub(),
        module_scores=output["module_scores"],
        overall_awci=output["awci"],
        awci_result=result,
        calculator=calculator,
    )
    text = format_aviation_report(report)
    # Every top-level section has real content (not itself a bare
    # "not available" body) - individual sub-fields within the
    # provenance section may still legitimately say "not available"
    # (e.g. lead_time_hours/vertical_level were never supplied here).
    assert "Weather\n-------\nnot available" not in text
    assert "Hazards & Confidence\n--------------------\nnot available" not in text
    assert "Model, Calculation & Provenance" in text
    assert "Turbulence Risk" in text
    assert "Model: v1" in text


# --------------------------------------------------------------------- discipline


def test_aviation_report_never_computes_a_new_awci_score():
    """Assembler discipline: aviation_report.py must never construct
    or call an AWCICalculator itself - only compose already-computed
    results a caller supplies."""
    import awci.reports.aviation_report as aviation_report_module

    assert not hasattr(aviation_report_module, "AWCICalculator")
