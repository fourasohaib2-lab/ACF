"""QualityInfo: real quality-control status (Prompt Maître ACF v2.0, section 91)."""

from dataclasses import dataclass, field

#: Prompt Maître section 4's own pipeline framing ("PASS ----- WARNING ----- FAIL").
VALID_STATUSES = ("NOT_ASSESSED", "PASS", "WARNING", "FAIL")


@dataclass
class QualityInfo:
    """
    Quality-control outcome for a Dataset.

    Defaults to NOT_ASSESSED, never PASS - a Dataset nobody has run QC
    on must say so honestly, not silently claim to have passed.
    """

    status: str = "NOT_ASSESSED"
    flags: list[str] = field(default_factory=list)
    #: Fraction of expected data actually present, in [0, 1] - None if unknown.
    completeness_fraction: float | None = None

    def __post_init__(self) -> None:
        if self.status not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}, got {self.status!r}")
        if self.completeness_fraction is not None and not (0.0 <= self.completeness_fraction <= 1.0):
            raise ValueError(f"completeness_fraction must be in [0, 1], got {self.completeness_fraction}")
