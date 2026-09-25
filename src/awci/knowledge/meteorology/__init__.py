"""
Atmospheric Complexity Framework (ACF)

WMO Meteorological Terminology Package (Aviation Knowledge Base)

New subpackage (2026-09-21, at explicit user request) matching the
blueprint's own ``awci/knowledge/meteorology/`` layer (see
``docs/architecture/awci_reference_architecture.md`` section 2) -
real, standard WMO meteorological classifications used by aviation
(starting with cloud genera/étages), distinct from the ICAO-specific
content in ``awci.knowledge.icao``.
"""

from awci.knowledge.meteorology.clouds import CloudEtage, CloudGenus, CLOUD_GENUS_ETAGE

__all__ = [
    "CLOUD_GENUS_ETAGE",
    "CloudEtage",
    "CloudGenus",
]
