"""
Event: the Prompt Maître ACF v2.0's section 12-13 weather event contract + real lifecycle.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from acf.core.contracts.provenance import Provenance
from acf.core.contracts.uncertainty import UncertaintyInfo

#: Prompt Maître section 13's exact lifecycle diagram:
#:   DETECTED -> ANALYZED -> CONFIRMED -> VERIFIED -> CERTIFIED -> PUBLISHED
#:   DETECTED -> REJECTED
#: Any transition not listed here is illegal - Event.transition_to()
#: enforces this, a status field alone would let a caller skip straight
#: from DETECTED to CERTIFIED.
_LEGAL_TRANSITIONS: dict[str, set[str]] = {
    "DETECTED": {"ANALYZED", "REJECTED"},
    "ANALYZED": {"CONFIRMED"},
    "CONFIRMED": {"VERIFIED"},
    "VERIFIED": {"CERTIFIED"},
    "CERTIFIED": {"PUBLISHED"},
    "PUBLISHED": set(),
    "REJECTED": set(),
}

TERMINAL_STATUSES = frozenset({"PUBLISHED", "REJECTED"})


class IllegalEventTransitionError(ValueError):
    """Raised by Event.transition_to() for any status change not in _LEGAL_TRANSITIONS."""


@dataclass
class Event:
    """
    A real weather event object with an enforced lifecycle.

    Field names match the Prompt Maître's section 12 list exactly,
    plus `status` (the section 13 lifecycle state, not in the original
    field list but needed to make the lifecycle real rather than
    aspirational).

    Parameters
    ----------
    event_id : str
        Defaults to a real generated UUID4 if not supplied.
    type : str
        e.g. "strong_wind", "fog" - see events.detectors for what ACF
        can genuinely detect today (see package docstring for the
        honest list of what is NOT built).
    geometry : dict
        Real location, e.g. {"lat": 36.7, "lon": 3.0} for a point
        detection, or {"lat_min":..., "lat_max":..., "lon_min":...,
        "lon_max":...} for an area.
    start_time, end_time : datetime
        end_time is None for an ongoing/instantaneous detection.
    intensity : float
        Detector-specific real value (e.g. wind speed in m/s for a
        StrongWindEvent) - not a normalized [0,1] score, see each
        detector's own docstring for units.
    probability, confidence : float
        Both in [0, 1].
    supporting_parameters : dict[str, float]
        The real input values that triggered detection (e.g.
        {"wind_speed_m_s": 24.3}) - so a caller can see exactly why,
        not just that.
    supporting_models : tuple[str, ...]
        Which model(s) the detection is based on, e.g. ("ARPEGE",).
    observations : tuple[str, ...]
        Real observation identifiers that corroborate this event, if
        any - empty by default (no fabricated corroboration).
    uncertainty : UncertaintyInfo
        Reused from acf.core.contracts - defaults to "not_assessed".
    provenance : Provenance, optional
        Reused from acf.core.contracts.
    status : str
        Defaults to "DETECTED" - every event starts there; use
        transition_to() to advance it, never set .status directly if
        you want the lifecycle enforced.
    """

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    geometry: dict[str, float] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    intensity: float = 0.0
    probability: float = 0.0
    confidence: float = 0.0
    supporting_parameters: dict[str, float] = field(default_factory=dict)
    supporting_models: tuple[str, ...] = ()
    observations: tuple[str, ...] = ()
    uncertainty: UncertaintyInfo = field(default_factory=UncertaintyInfo)
    provenance: Provenance | None = None
    status: str = "DETECTED"

    def __post_init__(self) -> None:
        if not (0.0 <= self.probability <= 1.0):
            raise ValueError(f"probability must be in [0, 1], got {self.probability}")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence must be in [0, 1], got {self.confidence}")
        if self.status not in _LEGAL_TRANSITIONS:
            raise ValueError(f"status must be one of {sorted(_LEGAL_TRANSITIONS)}, got {self.status!r}")

    def transition_to(self, new_status: str) -> None:
        """
        Advance this event's lifecycle status - only along a real edge
        of the section 13 diagram.

        Raises
        ------
        IllegalEventTransitionError
            If `new_status` is not a legal transition from the current
            status (e.g. DETECTED -> CERTIFIED directly, or any
            transition out of a terminal status).
        """
        legal = _LEGAL_TRANSITIONS[self.status]
        if new_status not in legal:
            raise IllegalEventTransitionError(
                f"Cannot transition from {self.status!r} to {new_status!r} - "
                f"legal next status(es) from {self.status!r}: {sorted(legal) or 'none (terminal)'}"
            )
        self.status = new_status

    def is_terminal(self) -> bool:
        """True if this event's status has no further legal transitions (PUBLISHED or REJECTED)."""
        return self.status in TERMINAL_STATUSES
