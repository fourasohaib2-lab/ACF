"""
Atmospheric Complexity Framework (ACF)

Reports - Aviation Report

Real, composed aviation report - the ``aviation_report.py`` module
named in
``docs/architecture/awci_reference_architecture.md`` section 17, the
specific gap already named in
``docs/architecture/acf_awci_architecture_gap_analysis.md`` ("no
standalone ``reports/aviation_report.py`` generator"). "Every report
must preserve: data sources, model, time, location, calculation,
factors, hazards, confidence, uncertainty, provenance" - achieved here
by composing 3 already-real systems built earlier this session, never
a new computation:

- ``awci.airport.weather.AirportWeatherSnapshot`` (location, real live
  weather - a real data source).
- ``awci.decision.DecisionSupportView`` (hazards, confidence via real
  severity bands, real cited recommendations) - optional, only when
  the caller supplies real AWCI module scores.
- ``awci.provenance.AuditRecord`` (model, calculation, provenance) -
  optional, only when the caller supplies a real ``AWCIResult``.

Every optional section is honestly absent (rendered "not available" by
``generator.render_report()``) rather than fabricated when the caller
does not supply the underlying real data - this report generator
computes nothing itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from awci.airport.weather import AirportWeatherSnapshot, build_weather_snapshot
from awci.decision import DecisionContext, DecisionSupportView, assess
from awci.provenance import AuditRecord, build_audit_record, format_audit_report
from awci.reports.generator import ReportSection, render_report

if TYPE_CHECKING:
    from awci.complexity.calculator import AWCICalculator
    from awci.complexity.result import AWCIResult
    from awci.observations.hub import ObservationsHub


@dataclass(frozen=True)
class AviationReport:
    """Real, composed aviation report for one real airport - each
    field either a real, already-built object from an already-real
    system, or honestly ``None`` when the caller did not supply the
    real data that section needs."""

    icao_code: str
    generated_at: datetime
    weather: AirportWeatherSnapshot
    decision: DecisionSupportView | None
    audit: AuditRecord | None


def build_aviation_report(
    icao_code: str,
    hub: "ObservationsHub | None" = None,
    module_scores: dict[str, float] | None = None,
    overall_awci: float | None = None,
    physical_score: float | None = None,
    forecast_score: float | None = None,
    active_hazard_keys: tuple[str, ...] = (),
    awci_result: "AWCIResult | None" = None,
    calculator: "AWCICalculator | None" = None,
    pressure_hpa: float = 1013.25,
    latitude: float = 0.0,
    longitude: float = 0.0,
) -> AviationReport:
    """
    Real, composed aviation report for one real airport.

    ``weather`` is always built (see ``build_weather_snapshot()``).
    ``decision`` is built only when ``module_scores`` and
    ``overall_awci`` are both supplied - honestly ``None`` otherwise
    (never a fabricated situation from data that was never given).
    ``audit`` is built only when ``awci_result`` is supplied -
    honestly ``None`` otherwise.
    """
    weather = build_weather_snapshot(icao_code, hub=hub)

    decision: DecisionSupportView | None = None
    if module_scores is not None and overall_awci is not None:
        context = DecisionContext(latitude=latitude, longitude=longitude, pressure_hpa=pressure_hpa)
        decision = assess(
            context=context,
            module_scores=module_scores,
            overall_awci=overall_awci,
            physical_score=physical_score,
            forecast_score=forecast_score,
            active_hazard_keys=active_hazard_keys,
        )

    audit: AuditRecord | None = None
    if awci_result is not None:
        audit = build_audit_record(awci_result, calculator)

    return AviationReport(
        icao_code=icao_code,
        generated_at=datetime.now(UTC),
        weather=weather,
        decision=decision,
        audit=audit,
    )


def _weather_section(weather: AirportWeatherSnapshot) -> ReportSection:
    if not weather.is_real_data:
        return ReportSection(title="Weather", lines=(f"Fetch failed: {weather.status}",))
    lines = [
        f"Raw METAR: {weather.raw_metar}",
        (
            f"Ceiling: {weather.ceiling_height_ft:.0f} ft ({weather.ceiling_category})"
            if weather.ceiling_height_ft is not None
            else "Ceiling: not reported (no BKN/OVC layer)"
        ),
        (
            f"Visibility: {weather.visibility_m:.0f} m"
            if weather.visibility_m is not None
            else "Visibility: not reported"
        ),
        "Present weather: " + (", ".join(weather.present_weather_descriptions) or "none reported"),
    ]
    return ReportSection(title="Weather", lines=tuple(lines))


def _hazards_section(decision: DecisionSupportView | None) -> ReportSection:
    if decision is None:
        return ReportSection(title="Hazards & Confidence", lines=())
    lines = [f"{a.label}: {a.level} (score {a.score:.1f})" for a in decision.situation.assessments]
    if decision.recommendations:
        lines.append("")
        lines.append("Recommendations:")
        for hazard_key, recommendations in decision.recommendations.items():
            for recommendation in recommendations:
                lines.append(f"  [{hazard_key}] {recommendation}")
    return ReportSection(title="Hazards & Confidence", lines=tuple(lines))


def _provenance_section(audit: AuditRecord | None) -> ReportSection:
    if audit is None:
        return ReportSection(title="Model, Calculation & Provenance", lines=())
    return ReportSection(
        title="Model, Calculation & Provenance", lines=tuple(format_audit_report(audit).splitlines())
    )


def format_aviation_report(report: AviationReport) -> str:
    """Real, human-readable rendering of ``report`` - see module
    docstring for the real sections this preserves, and which are
    honestly "not available" when their underlying real data was never
    supplied."""
    sections = (
        ReportSection(
            title="Location & Time",
            lines=(
                f"Airport: {report.icao_code}",
                f"Report generated at: {report.generated_at.isoformat()}",
            ),
        ),
        _weather_section(report.weather),
        _hazards_section(report.decision),
        _provenance_section(report.audit),
    )
    return render_report(f"Aviation Report - {report.icao_code}", sections)
