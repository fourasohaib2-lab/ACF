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
