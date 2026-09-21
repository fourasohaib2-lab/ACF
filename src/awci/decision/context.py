"""
Atmospheric Complexity Framework (ACF)

AWCI Decision Support - Operational Context

Real, minimal carrier for "what point/time/level is this decision
support view about" - the ``context.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 13. Holds
only real, caller-supplied values; never infers or fabricates a
location/time/level of its own.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from acf.science.encyclopedia.aerodynamics.isa_atmosphere import calculate_isa_pressure_altitude
from awci.knowledge.performance.altimetry import FlightLevel


@dataclass(frozen=True)
class DecisionContext:
    """
    Real operational context for one decision-support assessment.

    Parameters
    ----------
    latitude, longitude : float
        Real point of interest (degrees) this assessment applies to.
    pressure_hpa : float
        Real pressure level (hPa) - the same real quantity
        ``awci.dashboard.awci_map_panel.AWCIMapPanel``'s own "FLIGHT
        LEVEL" info box and ``flight_level_hpa`` parameter already use.
        Must be > 0 (see ``flight_level`` below).
    generated_at : datetime
        Real wall-clock UTC timestamp this context was built - honestly
        labeled as that, never implied to be a forecast valid time
        (same disclosure convention already established by
        ``AWCIMapPanel``'s own "RENDERED" info box).
    """

    latitude: float
    longitude: float
    pressure_hpa: float
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def flight_level(self) -> FlightLevel:
        """
        Real ICAO flight level derived from ``pressure_hpa`` via the
        real, standard ISA pressure-altitude formula (ICAO Doc 7488) -
        the exact same real physics
        ``awci.dashboard.awci_map_panel.pressure_to_flight_level_ft()``
        computes, reused here via its own real, already-implemented,
        algebraically-equivalent source
        (``acf.science.encyclopedia.aerodynamics.isa_atmosphere.
        calculate_isa_pressure_altitude()``) rather than re-derived, and
        without pulling that GUI module's own PySide6/matplotlib/
        cartopy dependencies into this headless package (see this
        package's own ``__init__.py`` docstring).
        """
        altitude_m = calculate_isa_pressure_altitude(self.pressure_hpa * 100.0)
        altitude_ft = altitude_m / 0.3048
        return FlightLevel(int(round(altitude_ft / 100.0)))
