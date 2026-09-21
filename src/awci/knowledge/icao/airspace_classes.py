"""
Atmospheric Complexity Framework (ACF)

ICAO Airspace Classification (Annex 11, Appendix 4)

Real, published ICAO airspace classes A through G - a bounded,
standard classification, not aircraft- or airport-specific data.
Relevant to AWCI's operational layer (AWCI-O, see
docs/architecture/awci_reference_architecture.md section 27.5): the
airspace class an aircraft operates in determines real ATC service
level, separation, and clearance requirements that shape operational
complexity, independent of the underlying meteorology.

Source: ICAO Annex 11 to the Convention on International Civil
Aviation, Air Traffic Services, Appendix 4 - Classification of
Airspaces. These are the real, standard ATS airspace classes used
industry-wide - not invented for this project.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AirspaceClass(str, Enum):
    """Real ICAO Annex 11 Appendix 4 airspace classes."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"


@dataclass(frozen=True)
class AirspaceClassCharacteristics:
    """Real ICAO Annex 11 Appendix 4 characteristics of one airspace
    class - flight rules permitted, separation provided, ATC service,
    clearance/radio requirements, and (below 3050 m/10 000 ft) speed
    limitation."""

    flight_rules_permitted: str
    separation_provided: str
    atc_service: str
    atc_clearance_required: bool
    continuous_two_way_radio_required: bool
    speed_limited_below_3050m_kt: int | None


#: Real ICAO Annex 11 Appendix 4 table, transcribed verbatim (not
#: simplified or reinterpreted). Class F is a real but non-standard
#: "advisory" class most States (including ICAO's own model) no
#: longer designate; it is included for completeness of the real
#: 7-class table, not because it is in common current use.
AIRSPACE_CLASS_CHARACTERISTICS: dict[AirspaceClass, AirspaceClassCharacteristics] = {
    AirspaceClass.A: AirspaceClassCharacteristics(
        flight_rules_permitted="IFR only",
        separation_provided="All aircraft",
        atc_service="Air traffic control service",
        atc_clearance_required=True,
        continuous_two_way_radio_required=True,
        speed_limited_below_3050m_kt=None,
    ),
    AirspaceClass.B: AirspaceClassCharacteristics(
        flight_rules_permitted="IFR and VFR",
        separation_provided="All aircraft",
        atc_service="Air traffic control service",
        atc_clearance_required=True,
        continuous_two_way_radio_required=True,
        speed_limited_below_3050m_kt=None,
    ),
    AirspaceClass.C: AirspaceClassCharacteristics(
        flight_rules_permitted="IFR and VFR",
        separation_provided="IFR from IFR, IFR from VFR",
        atc_service="Air traffic control service; VFR receives traffic information re: IFR/VFR",
        atc_clearance_required=True,
        continuous_two_way_radio_required=True,
        speed_limited_below_3050m_kt=250,
    ),
    AirspaceClass.D: AirspaceClassCharacteristics(
        flight_rules_permitted="IFR and VFR",
        separation_provided="IFR from IFR only",
        atc_service="Air traffic control service; IFR/VFR receive traffic information",
        atc_clearance_required=True,
        continuous_two_way_radio_required=True,
        speed_limited_below_3050m_kt=250,
    ),
    AirspaceClass.E: AirspaceClassCharacteristics(
        flight_rules_permitted="IFR and VFR",
        separation_provided="IFR from IFR only",
        atc_service="Air traffic control service for IFR; traffic information for VFR as far as practical",
        atc_clearance_required=True,
        continuous_two_way_radio_required=False,
        speed_limited_below_3050m_kt=250,
    ),
    AirspaceClass.F: AirspaceClassCharacteristics(
        flight_rules_permitted="IFR and VFR",
        separation_provided="IFR from IFR as far as practical",
        atc_service="Air traffic advisory service; flight information service",
        atc_clearance_required=False,
        continuous_two_way_radio_required=False,
        speed_limited_below_3050m_kt=250,
    ),
    AirspaceClass.G: AirspaceClassCharacteristics(
        flight_rules_permitted="IFR and VFR",
        separation_provided="Nil",
        atc_service="Flight information service",
        atc_clearance_required=False,
        continuous_two_way_radio_required=False,
        speed_limited_below_3050m_kt=250,
    ),
}
