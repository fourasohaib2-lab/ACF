"""
Atmospheric Complexity Framework (ACF) - Universal NWP Base Model (ACF-NWP-001)

Common abstract interface inherited by all atmospheric models:
ARPEGE, AROME, ALADIN, WRF, ICON, OpenIFS, IFS, FV3, MPAS, GFS, ECMWF.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseWeatherModel(ABC):
    """
    Abstract base class defining the universal operational lifecycle for NWP models.
    """

    name: str = "Unknown"
    supported_extensions: tuple = ()

    @abstractmethod
    def detect(self, dataset: Any) -> bool:
        """Detects if dataset matches model signature."""

    @abstractmethod
    def variables(self) -> list[str]:
        """Returns physical variables provided by model."""

    @abstractmethod
    def levels(self) -> list[Any]:
        """Returns vertical levels definition."""

    @abstractmethod
    def projection(self) -> str:
        """Returns map projection metadata."""

    # Extended Universal NWP Lifecycle API (ACF-NWP-001)
    #
    # NOTE (correction): these default implementations used to
    # unconditionally claim a successful lifecycle transition
    # ("PREPARED"/"RUNNING"/"RESTARTED"/True) regardless of `config`
    # and with no real dynamic-core solver, scheduler, or checkpoint
    # backend connected. verify() in particular used to unconditionally
    # return a PERFECT score (rmse=0.0, bias=0.0, mae=0.0, acc=1.0) -
    # the most dangerous fabrication here, since it implies a model
    # verified with zero error against real observations that were
    # never actually compared. None of the four concrete subclasses
    # (ARPEGEIngestionAdapter, AROMEIngestionAdapter,
    # ALADINIngestionAdapter, ERA5Model) override any of these methods
    # (verified via grep), so every one of them previously inherited
    # this fabricated behavior verbatim, with no real caller or test
    # coverage anywhere (verified). Left as base-class defaults for
    # subclasses that don't wire in a real backend, now honest about
    # having none connected rather than claiming success/perfection.

    def prepare(self, config: dict[str, Any]) -> dict[str, Any]:
        """Prepares boundary and initial conditions."""
        return {"status": "NOT_PREPARED_NO_BACKEND_CONNECTED", "model": self.name}

    def configure(self, domain: str, resolution: float, forecast_hours: int) -> dict[str, Any]:
        """Configures grid domain, resolution, and forecast length."""
        return {"domain": domain, "resolution": resolution, "forecast_hours": forecast_hours}

    def run(self) -> dict[str, Any]:
        """Executes model dynamic core solver."""
        return {"status": "NOT_RUNNING_NO_SOLVER_CONNECTED", "model": self.name}

    def restart(self, checkpoint_step: int) -> dict[str, Any]:
        """Restarts model from a specified checkpoint."""
        return {"status": "NOT_RESTARTED_NO_BACKEND_CONNECTED", "checkpoint_step": checkpoint_step}

    def stop(self) -> bool:
        """Gracefully terminates model run."""
        return False

    def resume(self) -> bool:
        """Resumes paused model run."""
        return False

    def collect_outputs(self, target_dir: str) -> list[str]:
        """Collects generated forecast output files."""
        return []

    # ------------------------------------------------------ Model Adapter
    # Protocol (added 2026-09-02, user's "Prompt Maître ACF v2.0",
    # section 5). reports/ACF_MASTER_AUDIT_v2.md found AROMEIngestionAdapter/
    # ALADINIngestionAdapter/ARPEGEIngestionAdapter/ERA5Model each real, but
    # with DIFFERENT method names for the same real logic
    # (read_arome_file/read_aladin_file/read_arpege_file) - forcing any
    # caller that wants to read a file regardless of model into exactly
    # the "if model == 'AROME': ..." branching the master spec explicitly
    # warns against. The methods below give every subclass one uniform
    # entry point per real capability, delegating to whatever each
    # subclass's own real logic already does - detect()/levels() are
    # aliased (identify()/vertical_levels()), read()/metadata()/
    # coordinates() require the concrete subclass to actually have real
    # file-reading logic connected (raises honestly if not, per this
    # class's own established convention above), capabilities() is a real
    # introspection report (not fabricated), normalize() genuinely
    # attempts acf.normalization's real CF crosswalk and honestly reports
    # what it could and couldn't map - no invented mapping table.

    def identify(self, dataset: Any) -> bool:
        """Model Adapter Protocol name for detect() - same real logic, not a second implementation."""
        return self.detect(dataset)

    def vertical_levels(self) -> list[Any]:
        """Model Adapter Protocol name for levels() - same real logic, not a second implementation."""
        return self.levels()

    def read(self, filepath: Any) -> dict[str, Any]:
        """
        Model Adapter Protocol entry point for reading a real dataset
        file. No generic implementation here - a concrete subclass with
        real file-reading logic must override this (see
        AROMEIngestionAdapter.read() etc., which delegate to their own
        pre-existing read_<model>_file() method).
        """
        raise NotImplementedError(f"{self.name} has no real file-reading backend connected")

    def metadata(self) -> dict[str, Any]:
        """
        Real metadata from the file at self.filepath, via read(). Needs
        a real filepath already associated with this adapter instance -
        raises honestly if none is set, rather than returning an empty
        placeholder dict.
        """
        filepath = getattr(self, "filepath", None)
        if filepath is None:
            raise NotImplementedError(
                f"{self.name}.metadata() needs a real file - construct this adapter with a "
                f"filepath, or call read(filepath) directly instead"
            )
        return dict(self.read(filepath)["metadata"])

    def coordinates(self) -> dict[str, Any]:
        """Real geometry/coordinate metadata from the file at self.filepath, via read(). Same requirement as metadata()."""
        filepath = getattr(self, "filepath", None)
        if filepath is None:
            raise NotImplementedError(
                f"{self.name}.coordinates() needs a real file - construct this adapter with a "
                f"filepath, or call read(filepath) directly instead"
            )
        return dict(self.read(filepath)["geometry"])

    def forecast_times(self) -> list[Any]:
        """No adapter in this project has real forecast-cycle-time discovery logic connected today - honestly refuses rather than guessing a cycle schedule."""
        raise NotImplementedError(f"{self.name} has no real forecast-cycle-time discovery logic connected")

    def capabilities(self) -> dict[str, Any]:
        """
        Real, computed report of what THIS adapter instance actually
        supports - via genuine introspection (does this subclass
        override read()?), not a fabricated "SUPPORTED" claim.
        """
        levels = self.levels()
        return {
            "name": self.name,
            "supported_extensions": list(self.supported_extensions),
            "variable_count": len(self.variables()),
            "level_count": len(levels) if isinstance(levels, list) else None,
            "projection": self.projection(),
            "has_real_read_backend": type(self).read is not BaseWeatherModel.read,
            "has_real_run_backend": type(self).run is not BaseWeatherModel.run,
            "has_real_verify_backend": type(self).verify is not BaseWeatherModel.verify,
        }

    def normalize(self) -> dict[str, Any]:
        """
        Attempt to map each of self.variables() to a real CF
        standard_name via acf.normalization.variable_names.
        to_cf_standard_name(source="ecmwf") - honestly reports which
        variables mapped and which didn't, rather than inventing a
        crosswalk for names it doesn't recognize (e.g. AROME's FA-format
        internal field names like "S090TEMPERATURE", which have no real
        entry in resources/standards/ecmwf/parameters.json today).
        """
        from acf.normalization.variable_names import to_cf_standard_name

        mapped: dict[str, dict[str, str]] = {}
        unmapped: list[str] = []
        for var in self.variables():
            try:
                mapped[var] = to_cf_standard_name(var, source="ecmwf")
            except ValueError:
                unmapped.append(var)
        return {"mapped": mapped, "unmapped": unmapped}

    def verify(self) -> dict[str, Any]:
        """Computes verification metrics against observations.

        NOTE (correction - safety-relevant): this used to
        unconditionally return a PERFECT score (rmse=0.0, bias=0.0,
        mae=0.0, acc=1.0) regardless of any real observations ever
        being compared - the most misleading form of fabrication,
        since a perfect score reads as verified excellence rather than
        "nothing was computed". Real verification metrics require a
        real observation dataset to compare against; none is connected
        here, so this honestly refuses to claim a score rather than
        silently reporting perfection.
        """
        raise NotImplementedError(
            f"verify() for model '{self.name}' needs a real observation dataset to compare against - "
            "none is connected. Previously returned a hard-coded fake perfect score "
            "(rmse=0.0, bias=0.0, mae=0.0, acc=1.0); removed rather than left silently wrong."
        )
