"""Master HPC Workflow Engine for AROME & ALADIN Operational Forecasting Cycles (ACF-HPC-104).

This module provides the core orchestration engine for executing weather forecast cycles
(AROME 1.3km and ALADIN 7.5km) on High-Performance Computing (HPC) clusters.
It implements end-to-end cycle preparation, data assimilation (3D-Var/4D-Var),
SURFEX surface coupling, core model integration, post-processing (FULLPOS),
operational product generation, quality control, archiving, and cleanup.
"""

from __future__ import annotations

import logging
import sys
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from acf.hpc_connector.logging import log_hpc_event
from acf.hpc_workflow.workflow_factory import WorkflowFactory
from acf.hpc_workflow.workflow_manager import WorkflowManager
from acf.hpc_workflow.workflow_status import (
    WorkflowError,
    WorkflowExecutionError,
    WorkflowValidationError,
)

# Logger setup
logger = logging.getLogger("acf.hpc_workflow.workflow_engine")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s][ACF-WORKFLOW-ENGINE][%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# -----------------------------------------------------------------------------
# Enums
# -----------------------------------------------------------------------------


class ForecastCycle(str, Enum):
    """Operational forecast cycles corresponding to UTC run times (00, 06, 12, 18 UTC)."""

    UTC_00 = "00UTC"
    UTC_06 = "06UTC"
    UTC_12 = "12UTC"
    UTC_18 = "18UTC"

    @classmethod
    def from_string(cls, val: str | ForecastCycle) -> ForecastCycle:
        """Parse string input into a valid ForecastCycle enum instance."""
        if isinstance(val, ForecastCycle):
            return val

        cleaned = str(val).strip().upper().replace(" ", "").replace("_", "")
        if cleaned in ("00", "00UTC", "UTC00", "RUN00"):
            return cls.UTC_00
        elif cleaned in ("06", "06UTC", "UTC06", "RUN06"):
            return cls.UTC_06
        elif cleaned in ("12", "12UTC", "UTC12", "RUN12"):
            return cls.UTC_12
        elif cleaned in ("18", "18UTC", "UTC18", "RUN18"):
            return cls.UTC_18
        else:
            raise ValueError(f"Invalid ForecastCycle '{val}'. Allowed cycles: 00UTC, 06UTC, 12UTC, 18UTC.")

    def __str__(self) -> str:
        return self.value


class WorkflowStage(str, Enum):
    """Operational stages of the AROME/ALADIN forecasting workflow."""

    INITIALIZATION = "INITIALIZATION"
    PREPROCESSING = "PREPROCESSING"
    OBSERVATION_CHECK = "OBSERVATION_CHECK"
    ASSIMILATION = "ASSIMILATION"
    SURFEX = "SURFEX"
    PREP = "PREP"
    MODEL_RUN = "MODEL_RUN"
    POST_PROCESSING = "POST_PROCESSING"
    PRODUCT_GENERATION = "PRODUCT_GENERATION"
    QUALITY_CONTROL = "QUALITY_CONTROL"
    ARCHIVING = "ARCHIVING"
    CLEANUP = "CLEANUP"

    def __str__(self) -> str:
        return self.value


# -----------------------------------------------------------------------------
# Exception Hierarchy
# -----------------------------------------------------------------------------


class WorkflowEngineError(WorkflowError):
    """Base exception class for all HPC WorkflowEngine operations."""


class ConfigurationError(WorkflowEngineError):
    """Exception raised when workflow configuration loading or validation fails."""


class EnvironmentValidationError(WorkflowEngineError, WorkflowValidationError):
    """Exception raised when HPC environment validation fails."""


class CycleInitializationError(WorkflowEngineError):
    """Exception raised when initializing a forecasting cycle fails."""


class StageExecutionError(WorkflowEngineError, WorkflowExecutionError):
    """Exception raised when an individual workflow stage execution fails."""

    def __init__(
        self,
        stage: WorkflowStage,
        message: str,
        cause: Exception | None = None,
    ) -> None:
        self.stage: WorkflowStage = stage
        self.cause: Exception | None = cause
        super().__init__(f"Stage '{stage.value}' failed: {message}")


class WorkflowExecutionAbortedError(WorkflowEngineError):
    """Exception raised when workflow execution is aborted due to a prior stage failure."""


# -----------------------------------------------------------------------------
# Dataclasses
# -----------------------------------------------------------------------------


@dataclass
class WorkflowConfig:
    """Operational workflow configuration parameters dataclass."""

    model_name: str = "AROME"
    cycle: ForecastCycle = ForecastCycle.UTC_00
    forecast_length: str = "24h"
    work_dir: Path = field(default_factory=lambda: Path("/tmp/acf_hpc_work"))
    output_dir: Path = field(default_factory=lambda: Path("/tmp/acf_hpc_output"))
    archive_dir: Path = field(default_factory=lambda: Path("/tmp/acf_hpc_archive"))
    num_cores: int = 64
    mpi_tasks: int = 16
    omp_threads: int = 4
    hpc_cluster: str = "default_hpc"
    environment_vars: dict[str, str] = field(default_factory=dict)
    extra_params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.cycle, str):
            self.cycle = ForecastCycle.from_string(self.cycle)
        self.work_dir = Path(self.work_dir)
        self.output_dir = Path(self.output_dir)
        self.archive_dir = Path(self.archive_dir)

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary representation."""
        return {
            "model_name": self.model_name,
            "cycle": self.cycle.value,
            "forecast_length": self.forecast_length,
            "work_dir": str(self.work_dir),
            "output_dir": str(self.output_dir),
            "archive_dir": str(self.archive_dir),
            "num_cores": self.num_cores,
            "mpi_tasks": self.mpi_tasks,
            "omp_threads": self.omp_threads,
            "hpc_cluster": self.hpc_cluster,
            "environment_vars": self.environment_vars,
            "extra_params": self.extra_params,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowConfig:
        """Create WorkflowConfig instance from a dictionary."""
        cycle_val = data.get("cycle", ForecastCycle.UTC_00)
        cycle = ForecastCycle.from_string(cycle_val) if isinstance(cycle_val, str) else cycle_val
        return cls(
            model_name=str(data.get("model_name", "AROME")),
            cycle=cycle,
            forecast_length=str(data.get("forecast_length", "24h")),
            work_dir=Path(data.get("work_dir", "/tmp/acf_hpc_work")),
            output_dir=Path(data.get("output_dir", "/tmp/acf_hpc_output")),
            archive_dir=Path(data.get("archive_dir", "/tmp/acf_hpc_archive")),
            num_cores=int(data.get("num_cores", 64)),
            mpi_tasks=int(data.get("mpi_tasks", 16)),
            omp_threads=int(data.get("omp_threads", 4)),
            hpc_cluster=str(data.get("hpc_cluster", "default_hpc")),
            environment_vars=dict(data.get("environment_vars", {})),
            extra_params=dict(data.get("extra_params", {})),
        )


@dataclass
class StageResult:
    """Execution result and metrics for an individual workflow stage."""

    stage: WorkflowStage
    success: bool
    start_time: float
    end_time: float
    duration_seconds: float
    output_files: list[Path] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
    logs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert stage result to dictionary representation."""
        return {
            "stage": self.stage.value,
            "success": self.success,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration_seconds,
            "output_files": [str(f) for f in self.output_files],
            "metrics": self.metrics,
            "error_message": self.error_message,
            "logs": self.logs,
        }


@dataclass
class CycleContext:
    """Operational forecasting cycle execution context and state tracker."""

    workflow_id: str
    model_name: str
    cycle: ForecastCycle
    forecast_length: str
    config: WorkflowConfig
    current_stage: WorkflowStage = WorkflowStage.INITIALIZATION
    completed_stages: list[WorkflowStage] = field(default_factory=list)
    stage_results: dict[str, StageResult] = field(default_factory=dict)
    work_dir: Path = field(default_factory=lambda: Path("/tmp/acf_hpc_work"))
    created_at: float = field(default_factory=time.time)
    is_failed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.cycle, str):
            self.cycle = ForecastCycle.from_string(self.cycle)
        self.work_dir = Path(self.work_dir)

    def record_stage_result(self, result: StageResult) -> None:
        """Record stage execution result into context tracking."""
        stage_name = result.stage.value
        self.stage_results[stage_name] = result
        if result.success:
            if result.stage not in self.completed_stages:
                self.completed_stages.append(result.stage)
        else:
            self.is_failed = True


@dataclass
class ExecutionSummary:
    """Summary report of an entire operational workflow execution."""

    workflow_id: str
    model_name: str
    cycle: ForecastCycle
    status: str
    start_time: float
    end_time: float
    total_duration_seconds: float
    completed_stages: list[WorkflowStage] = field(default_factory=list)
    failed_stage: WorkflowStage | None = None
    stage_results: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    job_id: str = ""

    def __post_init__(self) -> None:
        if not self.job_id:
            self.job_id = self.workflow_id

    def to_dict(self) -> dict[str, Any]:
        """Convert execution summary to dictionary representation."""
        return {
            "workflow_id": self.workflow_id,
            "job_id": self.job_id,
            "model_name": self.model_name,
            "cycle": self.cycle.value,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_duration_seconds": self.total_duration_seconds,
            "completed_stages": [s.value for s in self.completed_stages],
            "failed_stage": self.failed_stage.value if self.failed_stage else None,
            "stage_results": self.stage_results,
            "metrics": self.metrics,
        }


# -----------------------------------------------------------------------------
# WorkflowEngine Class
# -----------------------------------------------------------------------------


class WorkflowEngine:
    """Master HPC Workflow Engine orchestrating AROME & ALADIN operational forecasting cycles.

    NOTE (correction): the per-stage `action()` implementations below
    (run_preprocessing, run_observation_check, run_assimilation,
    run_surfex, run_prep, run_model, post_processing,
    generate_products, run_quality_control, archive_results, cleanup)
    genuinely exercise real orchestration mechanics - real timing, real
    logging, real stage sequencing with halt-on-failure, and real files
    written to real paths - but no real HPC backend is connected: there
    is no real AROME/ALADIN model binary invocation, no real 3D-Var/
    4D-Var solver, no real SURFEX coupling, no real observation
    network, and no real job submitted via
    acf.hpc_connector.scheduler_interface (fixed earlier this session
    to honestly report "NOT_SUBMITTED_*" rather than fabricate). Each
    stage's `metrics` dict used to contain fixed numbers (e.g.
    "innovations_rms": 0.12, "min_pressure_hpa": 980.5) presented with
    no disclosure that they are illustrative placeholders rather than
    real computed diagnostics - a genuine risk if ever read by a
    monitoring/reporting layer. Every stage's metrics dict now carries
    an explicit "simulated": True marker so any consumer can detect
    this programmatically, mirroring the `is_real_data`/`NOT_VERIFIED_*`
    disclosure pattern used throughout this codebase. Kept (not
    gutted, per this session's standing rule) since the orchestration
    architecture itself is genuinely useful and worth preserving ahead
    of real HPC backend integration.
    """

    def __init__(self, config: WorkflowConfig | dict[str, Any] | None = None) -> None:
        """Initialize the WorkflowEngine with factory, manager, and configuration."""
        self.factory = WorkflowFactory()
        self.manager = WorkflowManager()
        self.config: WorkflowConfig = self.load_configuration(config) if config else WorkflowConfig()
        self.initialized: bool = False
        self._log("INFO", "Initialized Master HPC WorkflowEngine for AROME & ALADIN")

    def _log(self, level: str, message: str) -> None:
        """Helper to emit consistent logs to Python logging and HPC connector logger."""
        lvl = level.upper()
        if lvl == "DEBUG":
            logger.debug(message)
        elif lvl == "WARNING":
            logger.warning(message)
        elif lvl == "ERROR":
            logger.error(message)
        else:
            logger.info(message)
        log_hpc_event(level, message)

    def load_configuration(
        self,
        config_input: Path | str | dict[str, Any] | WorkflowConfig | None = None,
    ) -> WorkflowConfig:
        """Load, parse, and validate operational configuration for HPC forecast workflows."""
        self._log("INFO", "Loading workflow configuration...")
        if config_input is None:
            self._log("INFO", "No explicit config supplied. Using default WorkflowConfig.")
            return WorkflowConfig()

        if isinstance(config_input, WorkflowConfig):
            self.config = config_input
            return config_input

        if isinstance(config_input, dict):
            try:
                config = WorkflowConfig.from_dict(config_input)
                self.config = config
                return config
            except Exception as err:
                msg = f"Failed to parse configuration dictionary: {err}"
                self._log("ERROR", msg)
                raise ConfigurationError(msg) from err

        path = Path(config_input)
        if not path.exists():
            msg = f"Configuration file not found at path: {path}"
            self._log("ERROR", msg)
            raise ConfigurationError(msg)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not isinstance(data, dict):
                raise ConfigurationError(f"YAML content at {path} is not a valid key-value mapping.")
            config = WorkflowConfig.from_dict(data)
            self.config = config
            self._log("INFO", f"Successfully loaded configuration from {path}")
            return config
        except Exception as err:
            msg = f"Error reading configuration file {path}: {err}"
            self._log("ERROR", msg)
            raise ConfigurationError(msg) from err

    def validate_environment(self) -> bool:
        """Validate HPC runtime environment, directory write permissions, and resources."""
        self._log("INFO", "Validating HPC environment...")

        if sys.version_info < (3, 12):
            msg = f"Python 3.12+ required, but running on Python {sys.version}"
            self._log("ERROR", msg)
            raise EnvironmentValidationError(msg)

        for path_attr, path_obj in [
            ("work_dir", self.config.work_dir),
            ("output_dir", self.config.output_dir),
            ("archive_dir", self.config.archive_dir),
        ]:
            try:
                path_obj.mkdir(parents=True, exist_ok=True)
                test_file = path_obj / f".write_test_{uuid.uuid4().hex[:8]}"
                test_file.write_text("test", encoding="utf-8")
                test_file.unlink()
            except Exception as err:
                msg = f"HPC environment validation failed: Directory '{path_obj}' ({path_attr}) is not writable: {err}"
                self._log("ERROR", msg)
                raise EnvironmentValidationError(msg) from err

        self._log("INFO", "HPC environment validation completed successfully.")
        return True

    def initialize(self, config: WorkflowConfig | dict[str, Any] | None = None) -> bool:
        """Initialize the workflow engine, load configuration, and validate environment."""
        self._log("INFO", "Initializing WorkflowEngine runtime...")
        if config is not None:
            self.load_configuration(config)
        self.validate_environment()
        self.initialized = True
        self._log("INFO", "WorkflowEngine successfully initialized.")
        return True

    def prepare_cycle(
        self,
        cycle: ForecastCycle | str,
        model_name: str = "AROME",
        forecast_length: str = "24h",
    ) -> CycleContext:
        """Prepare operational cycle context, directory structures, and parameters."""
        cycle_enum = ForecastCycle.from_string(cycle)
        wf_id = f"wf_{model_name.lower()}_{cycle_enum.value.lower()}_{uuid.uuid4().hex[:8]}"
        self._log(
            "INFO",
            f"Preparing cycle {cycle_enum.value} for model {model_name} (ID: {wf_id})",
        )

        cycle_work_dir = self.config.work_dir / wf_id
        cycle_work_dir.mkdir(parents=True, exist_ok=True)

        context = CycleContext(
            workflow_id=wf_id,
            model_name=model_name,
            cycle=cycle_enum,
            forecast_length=forecast_length,
            config=self.config,
            work_dir=cycle_work_dir,
            current_stage=WorkflowStage.INITIALIZATION,
        )
        self._log("INFO", f"Cycle context prepared at {cycle_work_dir}")
        return context

    def _execute_stage(
        self,
        context: CycleContext,
        stage: WorkflowStage,
        action: Callable[[CycleContext], tuple[list[Path], dict[str, Any]]],
    ) -> StageResult:
        """Internal helper orchestrating timed stage execution with logging and metrics."""
        context.current_stage = stage
        start_time = time.time()
        logs: list[str] = []
        msg_start = f"Starting stage [{stage.value}] for workflow {context.workflow_id}"
        self._log("INFO", msg_start)
        logs.append(msg_start)

        try:
            output_files, metrics = action(context)
            end_time = time.time()
            duration = end_time - start_time
            msg_ok = f"Completed stage [{stage.value}] in {duration:.2f}s"
            self._log("INFO", msg_ok)
            logs.append(msg_ok)

            result = StageResult(
                stage=stage,
                success=True,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                output_files=output_files,
                metrics=metrics,
                logs=logs,
            )
            context.record_stage_result(result)
            return result
        except Exception as err:
            end_time = time.time()
            duration = end_time - start_time
            error_msg = f"Error in stage [{stage.value}]: {err}"
            self._log("ERROR", error_msg)
            logs.append(error_msg)

            result = StageResult(
                stage=stage,
                success=False,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                error_message=str(err),
                logs=logs,
            )
            context.record_stage_result(result)
            return result

    # --- Operational Stage Implementations ---

    def run_preprocessing(self, context: CycleContext) -> StageResult:
        """Stage 2: Execute domain decomposition and initial data ingestion preprocessing."""

        def action(ctx: CycleContext) -> tuple[list[Path], dict[str, Any]]:
            prep_file = ctx.work_dir / "preprocessed_data.bin"
            prep_file.write_bytes(b"ACF PREPROCESSED GRID DATA")
            metrics = {"grid_points": 1000000, "domain": ctx.model_name, "simulated": True}
            return [prep_file], metrics

        return self._execute_stage(context, WorkflowStage.PREPROCESSING, action)

    def run_observation_check(self, context: CycleContext) -> StageResult:
        """Stage 3: Check availability and quality of meteorological observations."""

        def action(ctx: CycleContext) -> tuple[list[Path], dict[str, Any]]:
            obs_file = ctx.work_dir / "obs_check.json"
            obs_file.write_text(
                '{"radiosonde": "OK", "radar": "OK", "satellite": "OK"}',
                encoding="utf-8",
            )
            metrics = {"obs_count": 45000, "valid_ratio": 0.998, "simulated": True}
            return [obs_file], metrics

        return self._execute_stage(context, WorkflowStage.OBSERVATION_CHECK, action)

    def run_assimilation(self, context: CycleContext) -> StageResult:
        """Stage 4: Execute 3D-Var / 4D-Var atmospheric data assimilation."""

        def action(ctx: CycleContext) -> tuple[list[Path], dict[str, Any]]:
            assim_file = ctx.work_dir / "anal_assim.grib"
            assim_file.write_text("ASSIMILATION_ANALYSIS_FIELD", encoding="utf-8")
            metrics = {"innovations_rms": 0.12, "iterations": 40, "simulated": True}
            return [assim_file], metrics

        return self._execute_stage(context, WorkflowStage.ASSIMILATION, action)

    def run_surfex(self, context: CycleContext) -> StageResult:
        """Stage 5: Execute SURFEX surface scheme preparation and coupling."""

        def action(ctx: CycleContext) -> tuple[list[Path], dict[str, Any]]:
            surfex_file = ctx.work_dir / "surfex_out.fa"
            surfex_file.write_text("SURFEX_SURFACE_STATE", encoding="utf-8")
            metrics = {
                "soil_temperature_k": 288.15,
                "sea_surface_temp_k": 289.0,
                "simulated": True,
            }
            return [surfex_file], metrics

        return self._execute_stage(context, WorkflowStage.SURFEX, action)

    def run_prep(self, context: CycleContext) -> StageResult:
        """Stage 6: Prepare model initial conditions and lateral boundary conditions."""

        def action(ctx: CycleContext) -> tuple[list[Path], dict[str, Any]]:
            lbc_file = ctx.work_dir / "lbc_coupling.grib"
            lbc_file.write_text("LATERAL_BOUNDARY_CONDITIONS", encoding="utf-8")
            metrics = {"lbc_frames": 24, "coupling_interval_hours": 1, "simulated": True}
            return [lbc_file], metrics

        return self._execute_stage(context, WorkflowStage.PREP, action)

    def run_model(self, context: CycleContext) -> StageResult:
        """Stage 7: Execute main numerical weather prediction model core (AROME/ALADIN)."""

        def action(ctx: CycleContext) -> tuple[list[Path], dict[str, Any]]:
            model_out = ctx.work_dir / "forecast_raw.fa"
            model_out.write_text("MODEL_FORECAST_RAW_OUTPUT", encoding="utf-8")
            metrics = {
                "timestep_seconds": 50,
                "cores_used": ctx.config.num_cores,
                "forecast_hours": ctx.forecast_length,
                "simulated": True,
            }
            return [model_out], metrics

        return self._execute_stage(context, WorkflowStage.MODEL_RUN, action)

    def post_processing(self, context: CycleContext) -> StageResult:
        """Stage 8: Execute post-processing (FULLPOS parameter conversion)."""

        def action(ctx: CycleContext) -> tuple[list[Path], dict[str, Any]]:
            post_out = ctx.work_dir / "postproc_output.grib2"
            post_out.write_text("POSTPROCESSED_GRIB2_FIELDS", encoding="utf-8")
            metrics = {"fields_processed": 150, "levels": 90, "simulated": True}
            return [post_out], metrics

        return self._execute_stage(context, WorkflowStage.POST_PROCESSING, action)

    def generate_products(self, context: CycleContext) -> StageResult:
        """Stage 9: Generate operational weather products and chart outputs."""

        def action(ctx: CycleContext) -> tuple[list[Path], dict[str, Any]]:
            product_file = ctx.work_dir / "weather_products.tar.gz"
            product_file.write_text("OPERATIONAL_PRODUCTS_PACKAGE", encoding="utf-8")
            metrics = {"maps_generated": 48, "formats": ["GRIB2", "NetCDF4"], "simulated": True}
            return [product_file], metrics

        return self._execute_stage(context, WorkflowStage.PRODUCT_GENERATION, action)

    def run_quality_control(self, context: CycleContext) -> StageResult:
        """Stage 10: Run operational quality control and physical consistency checks."""

        def action(ctx: CycleContext) -> tuple[list[Path], dict[str, Any]]:
            qc_file = ctx.work_dir / "qc_report.json"
            qc_file.write_text('{"status": "PASSED", "anomalies": 0}', encoding="utf-8")
            metrics = {"min_pressure_hpa": 980.5, "max_wind_speed_ms": 42.1, "simulated": True}
            return [qc_file], metrics

        return self._execute_stage(context, WorkflowStage.QUALITY_CONTROL, action)

    def archive_results(self, context: CycleContext) -> StageResult:
        """Stage 11: Transfer operational outputs and logs to long-term storage/archive."""

        def action(ctx: CycleContext) -> tuple[list[Path], dict[str, Any]]:
            arch_dir = ctx.config.archive_dir / ctx.workflow_id
            arch_dir.mkdir(parents=True, exist_ok=True)
            arch_file = arch_dir / "cycle_archive.tar"
            arch_file.write_text("ARCHIVED_CYCLE_DATA", encoding="utf-8")
            metrics = {"archive_path": str(arch_file), "size_bytes": arch_file.stat().st_size, "simulated": True}
            return [arch_file], metrics

        return self._execute_stage(context, WorkflowStage.ARCHIVING, action)

    def cleanup(self, context: CycleContext) -> StageResult:
        """Stage 12: Clean up temporary work directory and scratch files."""

        def action(ctx: CycleContext) -> tuple[list[Path], dict[str, Any]]:
            cleanup_log = ctx.work_dir / "cleanup.log"
            cleanup_log.write_text("CLEANUP_SUCCESSFUL", encoding="utf-8")
            metrics = {"freed_mb": 250.0, "simulated": True}
            return [cleanup_log], metrics

        return self._execute_stage(context, WorkflowStage.CLEANUP, action)

    # --- Main Sequential Orchestrator ---

    def execute(
        self,
        model_name: str = "AROME",
        cycle: ForecastCycle | str = ForecastCycle.UTC_00,
        forecast_length: str = "24h",
        config: WorkflowConfig | dict[str, Any] | None = None,
    ) -> ExecutionSummary:
        """Execute complete operational forecasting workflow sequentially. Stops on first failure."""
        start_time = time.time()
        if not self.initialized or config is not None:
            self.initialize(config)

        context = self.prepare_cycle(cycle=cycle, model_name=model_name, forecast_length=forecast_length)

        stages_to_run: list[tuple[WorkflowStage, Callable[[CycleContext], StageResult]]] = [
            (
                WorkflowStage.INITIALIZATION,
                lambda ctx: self._execute_stage(
                    ctx,
                    WorkflowStage.INITIALIZATION,
                    lambda c: ([], {"status": "INITIALIZED"}),
                ),
            ),
            (WorkflowStage.PREPROCESSING, self.run_preprocessing),
            (WorkflowStage.OBSERVATION_CHECK, self.run_observation_check),
            (WorkflowStage.ASSIMILATION, self.run_assimilation),
            (WorkflowStage.SURFEX, self.run_surfex),
            (WorkflowStage.PREP, self.run_prep),
            (WorkflowStage.MODEL_RUN, self.run_model),
            (WorkflowStage.POST_PROCESSING, self.post_processing),
            (WorkflowStage.PRODUCT_GENERATION, self.generate_products),
            (WorkflowStage.QUALITY_CONTROL, self.run_quality_control),
            (WorkflowStage.ARCHIVING, self.archive_results),
            (WorkflowStage.CLEANUP, self.cleanup),
        ]

        failed_stage: WorkflowStage | None = None
        status = "SUCCESS"

        for stage, stage_func in stages_to_run:
            self._log("INFO", f"Executing stage [{stage.value}]...")
            result = stage_func(context)

            if not result.success:
                failed_stage = stage
                status = "FAILED"
                self._log(
                    "ERROR",
                    f"Workflow execution halted: Stage [{stage.value}] failed. Error: {result.error_message}",
                )
                break

        end_time = time.time()
        total_duration = end_time - start_time

        summary = ExecutionSummary(
            workflow_id=context.workflow_id,
            job_id=context.workflow_id,
            model_name=model_name,
            cycle=context.cycle,
            status=status,
            start_time=start_time,
            end_time=end_time,
            total_duration_seconds=total_duration,
            completed_stages=context.completed_stages,
            failed_stage=failed_stage,
            stage_results={k: v.to_dict() for k, v in context.stage_results.items()},
            metrics={
                "total_stages": len(stages_to_run),
                "completed_count": len(context.completed_stages),
            },
        )

        self._log(
            "INFO" if status == "SUCCESS" else "ERROR",
            f"Workflow {context.workflow_id} finished with status '{status}' in {total_duration:.2f}s",
        )
        return summary

    # --- Backward Compatibility Methods for HPC Connector and Tests ---

    def run_arome_forecast(self, cycle: str = "00UTC", forecast_length: str = "24h") -> dict[str, Any]:
        """Orchestrate AROME operational forecast cycle."""
        summary = self.execute(model_name="AROME", cycle=cycle, forecast_length=forecast_length)
        res = summary.to_dict()
        res["status"] = summary.status
        return res

    def run_aladin_forecast(self, cycle: str = "00UTC", forecast_length: str = "72h") -> dict[str, Any]:
        """Orchestrate ALADIN operational forecast cycle."""
        summary = self.execute(model_name="ALADIN", cycle=cycle, forecast_length=forecast_length)
        res = summary.to_dict()
        res["status"] = summary.status
        return res
