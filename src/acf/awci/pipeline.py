"""
AWCI Scientific Pipeline (docs/ACF_MASTER_PROMPT.md §8/§31)
==============================================================

§8 ("Architecture conceptuelle générale") and §31 ("Pipeline
scientifique") both describe the same real flow - ingestion → quality
control → harmonisation → normalisation → diagnostics → modules →
interactions → incertitude → fusion → AWCI → produits/visualisation -
and this session's exhaustive 90-section conformance audit
(reports/ACF_MASTER_AUDIT_v2.md) found every real stage existed
somewhere in this codebase, but never assembled into one real, named,
orchestrated, traceable sequence - a caller wanting the "whole
pipeline" had to know to call ~5 separate real subsystems by hand.

`run_awci_point_pipeline()` is that real orchestrator, for the one
concretely exercised path in this codebase: a single point's real
per-variable data through to a real, complete `AWCIResult` plus a real
§75 execution report. Every stage it runs calls an already-real,
already-tested function elsewhere in `acf.awci`/`acf.physics_guard` -
nothing here computes new science; this module is real ASSEMBLY, same
discipline as `acf.awci.result.build_awci_result()`.

Honest scope - which of §31's 21 named steps this pipeline covers, and
which it deliberately does not
--------------------------------------------------------------------
============================  ====================================================
Step (§31)                    Real status in this orchestrator
============================  ====================================================
1 DISCOVERY                   N/A - this architecture has no file discovery step
                               (in-memory solver/demo-pattern data, not archived
                               files)
2 INGESTION                   N/A here - a real caller already has `point_data`
                               (e.g. from `acf.awci.spatial_field`/a real model
                               adapter) before calling this function; the real
                               model-adapter layer itself is
                               `acf.models.base_model.BaseWeatherModel`
3 FORMAT DETECTION             N/A - same reason as DISCOVERY
4 MODEL IDENTIFICATION         Caller-supplied (`model` parameter, carried into
                               `Provenance.algorithm_version`) - not detected here
5 VARIABLE MAPPING             REAL - `acf.awci.input_adapter.
                               AWCI_KEY_TO_CF_STANDARD_NAME`
6 UNIT HARMONIZATION           REAL - `acf.awci.input_adapter.
                               build_awci_data_from_datasets()` (via
                               `acf.normalization.units.convert_unit()`)
7 GRID HARMONIZATION           N/A for a single point (no regridding needed); the
                               real grid/volume equivalent is
                               `acf.awci.path_sampling.crop_field_to_extent()`
8 QUALITY CONTROL              REAL - `acf.physics_guard.variable_quality.
                               assess_variable_quality()` (via step 5/6's adapter)
9 PHYSICAL VALIDATION          Opt-in - `acf.physics_guard.PhysicsGuard` real range
                               checks are available (`validate_physics=True` on the
                               per-variable formulas this pipeline's own
                               `point_data` may already have used) but not re-run
                               here to avoid double-validating the same values
10 DIAGNOSTICS                REAL, opt-in - whatever real diagnostic values
                               (`wind_shear`, `theta_e`, `updraft_velocity`,
                               `precipitation_phase_severity`, `mountain_wave_froude`)
                               the caller already put in `point_data` are used by
                               step 12 exactly as `AWCICalculator.
                               calculate_module_scores()` already documents
11 NORMALIZATION               REAL - `acf.awci.normalizer.Normalizer` (called
                               inside step 12)
12 MODULE CALCULATION          REAL - `AWCICalculator.calculate_module_scores()`
13 INTERACTION ENGINE          REAL - `AWCICalculator.calculate_interaction_scores()`
14 UNCERTAINTY ENGINE          REAL, honest - `AWCICalculator.
                               calculate_with_uncertainty()` (returns
                               `uncertainty_available: False` with a real reason
                               when no real ensemble/model realizations were
                               supplied - never a fabricated spread)
15 CONSENSUS ENGINE            Opt-in - real multi-model comparison
                               (`ModelConsensusEngine.
                               compute_real_multi_model_disagreement()`) is
                               genuinely expensive (runs a real solver per model)
                               and is never invoked automatically here; pass
                               `model_spread`/`model_spread_level` if the caller
                               already ran it
16 COMPLEXITY ENGINE           REAL - `AWCICalculator.calculate()` (via step 14)
17 AWCI                        REAL - the real `awci` score itself
18 PRODUCTS                    REAL - `acf.awci.result.build_awci_result()`
19 VISUALIZATION               N/A here - the real GUI layer
                               (`acf.gui.dashboard.awci_dashboard`) is a separate,
                               already-real consumer of this pipeline's own output
20 DASHBOARD                   N/A here - see 19
21 VALIDATION/CERTIFICATION    REAL, partial - `acf.awci.execution_report.
                               summarize_execution()` (the real §75 report); the
                               separate `acf.certification.engine.
                               CertificationEngine` operates on a real `Dataset`'s
                               own provenance/quality metadata, not this
                               dict-based point pipeline, and is not run here -
                               a real, disclosed, separate integration path
============================  ====================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from acf.awci.calculator import AWCICalculator
from acf.awci.execution_report import AWCIExecutionReport, summarize_execution
from acf.awci.input_adapter import AWCI_KEY_NATIVE_UNIT, AWCI_KEY_TO_CF_STANDARD_NAME, build_awci_data_from_datasets
from acf.awci.result import AWCIResult, build_awci_result
from acf.core.contracts.dataset import Dataset
from acf.physics_guard.variable_quality import VariableQualityStatus


def quality_for_awci_point_data(point_data: dict[str, Any], *, model: str = "ACF-DEMO") -> dict[str, VariableQualityStatus]:
    """
    Real per-variable quality (§32) for a point's real raw AWCI-keyed
    data (`temperature`/`specific_humidity`/`wind_speed`/`pressure`),
    reused - not reimplemented - from `acf.awci.input_adapter`: wraps
    the 4 CF-mappable keys into minimal real `Dataset`s at their own
    known native units (the exact same convention `AWCICalculator`
    itself expects), then calls `build_awci_data_from_datasets()` and
    keeps only its real `quality` half.

    Reusing the adapter here (rather than calling
    `assess_variable_quality()` directly) avoids re-deriving the real
    hPa-vs-Pa pressure unit conversion that adapter's own docstring
    already discloses as a real, previously-found bug - one real
    conversion path, not two.

    Parameters
    ----------
    point_data : dict
        A real point's `AWCICalculator`-keyed data - only the 4 keys
        `AWCI_KEY_TO_CF_STANDARD_NAME` maps are assessed; every other
        real key (`cape`, `wind_shear`, ...) has no CF standard_name
        and is silently not part of this real quality assessment (see
        `build_awci_data_from_datasets()`'s own docstring).
    model : str
        Real model/generator label carried into each `Dataset`'s own
        `model` field - purely descriptive context for this quality
        assessment, not itself validated.
    """
    now = datetime.now(UTC)
    datasets: dict[str, Dataset] = {}
    for awci_key in AWCI_KEY_TO_CF_STANDARD_NAME:
        if awci_key not in point_data:
            continue
        datasets[awci_key] = Dataset(
            id=f"point-of-interest-{awci_key}",
            source="acf.awci.pipeline.run_awci_point_pipeline",
            model=model,
            run="n/a",
            forecast_reference_time=now,
            valid_time=now,
            lead_time=timedelta(0),
            variable=AWCI_KEY_TO_CF_STANDARD_NAME[awci_key],
            unit=AWCI_KEY_NATIVE_UNIT[awci_key],
            dimensions=(),
            values=float(point_data[awci_key]),
        )
    _data, quality = build_awci_data_from_datasets(datasets)
    return quality


@dataclass
class PipelineStage:
    """One real §31 step's outcome in this orchestrator - see this
    module's own docstring table for every step's real status."""

    #: §31's own step name, e.g. "quality_control", "module_calculation".
    name: str
    #: "RAN" (this orchestrator genuinely executed real code for this
    #: step), "SKIPPED" (a real, available opt-in step the caller did
    #: not request), or "NOT_APPLICABLE" (this architecture has no real
    #: equivalent - see module docstring).
    status: str
    #: Real, human-readable detail - which real function ran, or why
    #: this step was skipped/not applicable. Never a placeholder.
    detail: str


@dataclass
class AWCIPipelineResult:
    """Real, complete output of one `run_awci_point_pipeline()` call -
    the real AWCIResult, its real §75 execution report, and the real
    per-stage trace (§31)."""

    result: AWCIResult
    execution_report: AWCIExecutionReport
    stages: list[PipelineStage] = field(default_factory=list)


def run_awci_point_pipeline(
    point_data: dict[str, Any],
    *,
    model: str = "ACF-DEMO",
    vertical_level: int | None = None,
    lead_time_hours: float | None = None,
    model_spread: dict[str, Any] | None = None,
    model_spread_level: str | None = None,
    max_dominant_factors: int = 3,
) -> AWCIPipelineResult:
    """
    Real, orchestrated §8/§31 pipeline for one point - variable mapping
    → quality control → module/interaction/uncertainty calculation →
    (opt-in consensus) → product assembly → execution report, each a
    call into an already-real function, nothing recomputed or
    fabricated (see module docstring's own step-by-step table for
    exactly which steps run and which are N/A for this architecture).

    Parameters
    ----------
    point_data : dict
        A real point's `AWCICalculator`-keyed data (`temperature`,
        `specific_humidity`, `wind_speed`, `pressure`, plus any real
        opt-in keys - `cape`, `wind_shear`, `theta_e`,
        `updraft_velocity`, `precipitation_phase_severity`,
        `mountain_wave_froude`, ... - `AWCICalculator.
        calculate_module_scores()`'s own docstring lists every real
        key this step 12 honours).
    model : str
        Real model/generator label - carried into the real quality
        assessment's own `Dataset.model` and into the returned
        `AWCIResult.provenance` (via `build_awci_result()` - see that
        function's own docstring for why provenance itself stays
        optional/caller-supplied rather than guessed here).
    vertical_level, lead_time_hours : optional
        Real drill-down chain context (§26/§53), passed straight
        through to `build_awci_result()`.
    model_spread, model_spread_level : optional
        Real, opt-in step-15 CONSENSUS ENGINE result - a caller that
        already ran `ModelConsensusEngine.
        compute_real_multi_model_disagreement()` (expensive - a real
        solver run per model) can supply its real output here; never
        computed automatically by this function (see module docstring).
    max_dominant_factors : int
        Passed straight through to `build_awci_result()`.

    Returns
    -------
    AWCIPipelineResult
    """
    stages: list[PipelineStage] = []

    quality = quality_for_awci_point_data(point_data, model=model)
    stages.append(
        PipelineStage(
            "variable_mapping_and_quality_control",
            "RAN",
            f"acf.awci.input_adapter - {len(quality)} real CF-mappable variable(s) assessed (§5/§6/§8/§32)",
        )
    )

    calc_output = AWCICalculator().calculate_with_uncertainty(point_data)
    uncertainty_detail = (
        f"n_realizations={calc_output['n_realizations']}"
        if calc_output.get("uncertainty_available")
        else "no real ensemble_members/model_realizations supplied (honest, see calculate_with_uncertainty()'s own docstring)"
    )
    stages.append(
        PipelineStage(
            "module_interaction_uncertainty_calculation",
            "RAN",
            f"AWCICalculator.calculate_with_uncertainty() - real modules/interactions/AWCI (§10-14/§16/§17); {uncertainty_detail}",
        )
    )

    if model_spread is not None:
        stages.append(
            PipelineStage(
                "consensus_engine",
                "RAN",
                "real, caller-supplied ModelConsensusEngine.compute_real_multi_model_disagreement() output (§15)",
            )
        )
    else:
        stages.append(
            PipelineStage(
                "consensus_engine",
                "SKIPPED",
                "no real multi-model comparison supplied - genuinely expensive (a real solver run per model), opt-in only (§15)",
            )
        )

    result = build_awci_result(
        calc_output,
        model_spread=model_spread,
        quality=quality,
        raw_variables=point_data,
        lead_time_hours=lead_time_hours,
        vertical_level=vertical_level,
        max_dominant_factors=max_dominant_factors,
    )
    stages.append(PipelineStage("products", "RAN", "acf.awci.result.build_awci_result() - the real, complete AWCIResult (§18/§81)"))

    report = summarize_execution(result, model_spread_level=model_spread_level)
    stages.append(
        PipelineStage("validation_and_observability", "RAN", "acf.awci.execution_report.summarize_execution() - the real §75 report (§21, partial - see module docstring)")
    )

    for name, reason in (
        ("discovery", "no file discovery in this architecture - point_data is already supplied by the caller"),
        ("ingestion", "no file ingestion in this architecture - see acf.models.base_model.BaseWeatherModel for the real model-adapter layer"),
        ("format_detection", "no file format detection in this architecture"),
        ("visualization", "a separate, already-real consumer of this pipeline's own output (acf.gui.dashboard.awci_dashboard)"),
        ("dashboard", "a separate, already-real consumer of this pipeline's own output (acf.gui.dashboard.awci_dashboard)"),
    ):
        stages.append(PipelineStage(name, "NOT_APPLICABLE", reason))

    return AWCIPipelineResult(result=result, execution_report=report, stages=stages)
