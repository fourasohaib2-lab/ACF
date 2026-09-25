"""
Atmospheric Complexity Framework (ACF)

Backward-compatible re-export shim.

``acf.connectors.eumetsat_mtg`` was physically moved to
``awci.data.connectors.eumetsat_mtg`` on 2026-09-21 (item 10 of "on
les attaque toutes un par un" - see
``docs/architecture/acf_awci_architecture_gap_analysis.md``). This
module keeps the old import path working; the real code lives at the
new location.
"""

from __future__ import annotations

from awci.data.connectors.eumetsat_mtg import (
    MTG_FCI_HIGH_RESOLUTION,
    MTG_FCI_NORMAL_RESOLUTION,
    MTG_SATELLITE_HEIGHT_M,
    MTG_SUBSATELLITE_LONGITUDE_DEG,
    SEARCH_URL,
    TOKEN_URL,
    EUMETSATMTGConnector,
    MTGFetchResult,
)

__all__ = [
    "EUMETSATMTGConnector",
    "MTGFetchResult",
    "MTG_FCI_HIGH_RESOLUTION",
    "MTG_FCI_NORMAL_RESOLUTION",
    "MTG_SATELLITE_HEIGHT_M",
    "MTG_SUBSATELLITE_LONGITUDE_DEG",
    "SEARCH_URL",
    "TOKEN_URL",
]
