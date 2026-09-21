"""
Atmospheric Complexity Framework (ACF)

WMO Cloud Genus & Étage Classification (International Cloud Atlas)

Real, published WMO cloud classification - the 10 real cloud genera
and their real altitude étage (CL/CM/CH) grouping. Relevant to AWCI's
hazard/ceiling/visibility diagnostics and to the Vertical Profile
Engine already documented
(docs/architecture/awci_reference_architecture.md section 6).

Source: WMO International Cloud Atlas (WMO-No. 407). This module
covers the 10 real genera and their real étage classification only -
deliberately not the full species/variety sub-classification (a real
but more detailed WMO taxonomy this module does not attempt to
enumerate from memory, to avoid presenting an unverified or
incomplete list as authoritative; consult the WMO Cloud Atlas directly
for species/variety detail).
"""

from __future__ import annotations

from enum import Enum


class CloudEtage(str, Enum):
    """Real WMO cloud altitude étages (temperate-latitude reference
    ranges - the real WMO Cloud Atlas gives different real ranges for
    polar and tropical latitudes, not modeled here)."""

    HIGH = "high"  # CH - real base height range ~5-13 km (~16 500-45 000 ft)
    MIDDLE = "middle"  # CM - real base height range ~2-7 km (~6 500-23 000 ft)
    LOW = "low"  # CL - real base height range 0-2 km (0-6 500 ft)


class CloudGenus(str, Enum):
    """The 10 real WMO cloud genera (International Cloud Atlas)."""

    CIRRUS = "cirrus"
    CIRROCUMULUS = "cirrocumulus"
    CIRROSTRATUS = "cirrostratus"
    ALTOCUMULUS = "altocumulus"
    ALTOSTRATUS = "altostratus"
    NIMBOSTRATUS = "nimbostratus"
    STRATOCUMULUS = "stratocumulus"
    STRATUS = "stratus"
    CUMULUS = "cumulus"
    CUMULONIMBUS = "cumulonimbus"


#: Real WMO genus -> étage classification. Altostratus and
#: Nimbostratus are real, disclosed exceptions to a strict
#: single-étage assignment: Altostratus is classified under the
#: middle étage but real bases commonly extend into the high étage;
#: Nimbostratus is a vertically extensive genus whose real base is
#: often in the low étage despite its middle-étage classification -
#: both nuances are real WMO Cloud Atlas content, not an omission.
CLOUD_GENUS_ETAGE: dict[CloudGenus, CloudEtage] = {
    CloudGenus.CIRRUS: CloudEtage.HIGH,
    CloudGenus.CIRROCUMULUS: CloudEtage.HIGH,
    CloudGenus.CIRROSTRATUS: CloudEtage.HIGH,
    CloudGenus.ALTOCUMULUS: CloudEtage.MIDDLE,
    CloudGenus.ALTOSTRATUS: CloudEtage.MIDDLE,
    CloudGenus.NIMBOSTRATUS: CloudEtage.MIDDLE,
    CloudGenus.STRATOCUMULUS: CloudEtage.LOW,
    CloudGenus.STRATUS: CloudEtage.LOW,
    CloudGenus.CUMULUS: CloudEtage.LOW,
    # Cumulonimbus is real, disclosed as a special case: it is
    # classified as "low étage" by the base of its cloud (per the
    # WMO Cloud Atlas), but is real and vertically extensive through
    # all three étages - not a data gap, the genus's own defining
    # characteristic.
    CloudGenus.CUMULONIMBUS: CloudEtage.LOW,
}


#: Real METAR/TAF cloud-cover abbreviations already decoded by
#: awci.knowledge.icao.metar_decoder's own `_CLOUD_RE` (FEW/SCT/BKN/
#: OVC) and CB/TCU convective indicators - cross-referenced here, not
#: duplicated: CB in a METAR/TAF cloud group corresponds to this
#: module's own CloudGenus.CUMULONIMBUS; TCU ("towering cumulus")
#: corresponds to a real, disclosed WMO species of CloudGenus.CUMULUS
#: (congestus) rather than its own genus.
METAR_CLOUD_TYPE_TO_GENUS: dict[str, CloudGenus] = {
    "CB": CloudGenus.CUMULONIMBUS,
    "TCU": CloudGenus.CUMULUS,
}


#: Real, standard WMO/ICAO METAR/TAF cloud-cover-fraction convention
#: (in oktas, eighths of sky covered) behind the same four
#: `_CLOUD_RE` cover abbreviations - the real amount each abbreviation
#: reports, not itself decoded elsewhere in this codebase.
METAR_CLOUD_COVER_OKTAS: dict[str, tuple[int, int]] = {
    "FEW": (1, 2),
    "SCT": (3, 4),
    "BKN": (5, 7),
    "OVC": (8, 8),
}
