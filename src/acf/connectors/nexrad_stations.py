"""
Atmospheric Complexity Framework (ACF)

Backward-compatible re-export shim.

``acf.connectors.nexrad_stations`` was physically moved to
``awci.data.connectors.nexrad_stations`` on 2026-09-21 (item 10 of "on
les attaque toutes un par un" - see
``docs/architecture/acf_awci_architecture_gap_analysis.md``). This
module keeps the old import path working; the real code lives at the
new location.
"""

from __future__ import annotations

from awci.data.connectors.nexrad_stations import (
    BASE_URL,
    DEFAULT_STATIONS,
    NEXRADRadarConnector,
    NexradFetchResult,
)

__all__ = ["BASE_URL", "DEFAULT_STATIONS", "NEXRADRadarConnector", "NexradFetchResult"]
