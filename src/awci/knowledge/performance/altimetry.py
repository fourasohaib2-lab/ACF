"""
Atmospheric Complexity Framework (ACF)

ICAO Altimetry System (Annex 2 / PANS-OPS / PANS-ATM Semi-Circular Rule)

Real, published ICAO altimetry conventions - the standard pressure
setting, the flight level concept, and the semi-circular cruising
level rule. Relevant to the Vertical Profile Engine already documented
(docs/architecture/awci_reference_architecture.md section 6) and to
AWCI-O's operational layer (section 27.5): the flight level a real
aircraft is assigned depends on real ICAO rules, not an arbitrary
altitude.

Source: ICAO Annex 2, Rules of the Air, and PANS-ATM (Doc 4444)
Appendix 3 - Tables of Cruising Levels. These are the real, standard
conventions used industry-wide - not invented for this project.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Real ICAO standard atmosphere pressure setting (Annex 2), used as
#: the altimeter reference above the transition altitude - the same
#: real value already used for ISA calculations in
#: AircraftPerformanceEngine.isa_atmosphere() (acf.awci's own
#: `p0 = 101325.0` Pa), expressed here in the two real units altimeters
#: are actually set in.
STANDARD_PRESSURE_SETTING_HPA = 1013.25
STANDARD_PRESSURE_SETTING_INHG = 29.92


@dataclass(frozen=True)
class FlightLevel:
    """A real ICAO flight level - pressure altitude (referenced to the
    standard 1013.25 hPa setting) in hundreds of feet, e.g. FL350 =
    35 000 ft on the standard setting. Only usable at or above the real
    transition altitude/level for the airspace in question (see
    `is_valid_ifr_cruising_level` for the real semi-circular rule that
    additionally governs which flight levels are assignable for IFR
    cruising)."""

    value: int

    def __str__(self) -> str:
        return f"FL{self.value:03d}"

    @property
    def altitude_ft(self) -> int:
        return self.value * 100


def is_valid_ifr_cruising_level(flight_level: int, magnetic_track_deg: float) -> bool:
    """Real ICAO PANS-ATM (Doc 4444) Appendix 3 semi-circular cruising
    level rule for IFR flight above the transition altitude: odd
    flight levels (FL010, FL030, FL050, ... in 2000 ft steps below
    FL290, then 4000 ft steps above per RVSM) for magnetic tracks
    000-179 degrees, even flight levels for magnetic tracks 180-359
    degrees.

    This function checks only the real odd/even-vs-track-direction
    rule; it does not itself validate RVSM 4000 ft spacing above
    FL290, which is a separate, real ICAO convention not modeled here.
    """
    if not (0.0 <= magnetic_track_deg < 360.0):
        raise ValueError("magnetic_track_deg must be in [0, 360)")

    is_odd_level = (flight_level // 10) % 2 == 1
    eastbound = magnetic_track_deg < 180.0
    return is_odd_level == eastbound
