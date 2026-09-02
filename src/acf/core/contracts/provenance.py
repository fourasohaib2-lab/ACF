"""Provenance: real reproducibility metadata (Prompt Maître ACF v2.0, section 38 - "INPUT VERSION + CODE VERSION + CONFIG VERSION + SCIENCE VERSION + MODEL RUN = REPRODUCIBLE RESULT")."""

from dataclasses import dataclass, field
from datetime import UTC, datetime


def _now_utc() -> datetime:
    return datetime.now(UTC)


@dataclass
class Provenance:
    """
    What produced a Dataset, and how to reproduce it.

    Every field is a plain string/timestamp a real caller can fill in
    from what it actually knows (e.g. a git commit hash, a solver
    class name, a config file path) - this class does not compute or
    guess any of them itself.
    """

    #: What generated the data, e.g. "CoupledEarthSolver",
    #: "AWCICalculator", "ModelConsensusEngine".
    generator: str
    #: Free-form algorithm/model identifier, e.g. "ARPEGE" for a
    #: MODEL_CONFIGS entry, or "AWCICalculator" for a complexity score.
    algorithm_version: str = "unknown"
    #: ACF package version this was produced under, if known.
    science_version: str = "unknown"
    #: Path or identifier of the configuration used, if any.
    config_version: str = "unknown"
    #: Real wall-clock time this Dataset was constructed.
    created_at: datetime = field(default_factory=_now_utc)
    #: Free-form notes - e.g. honest_limitation strings already
    #: produced by acf.awci.spatial_field/vertical_field/temporal_field.
    notes: str = ""

    def is_complete(self) -> bool:
        """True only if every version field was actually supplied (not left at its 'unknown' default) - a real completeness check, not just 'this object exists'."""
        return "unknown" not in (self.algorithm_version, self.science_version, self.config_version)
