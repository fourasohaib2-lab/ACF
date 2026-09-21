"""
Atmospheric Complexity Framework (ACF)

Aviation Observation Hub - hub.py

Real, single aggregation point over the already-real, already-working
observation connectors already scattered across this codebase - the
``hub.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 4
("Aviation Observation Hub... Specialized in aviation observations."),
previously the one, specific gap named in
``docs/architecture/acf_awci_architecture_gap_analysis.md`` ("no single
``observations/hub.py`` aggregation point").

Deliberately NOT the blueprint's full 11-file package (``stations.py``/
``metar.py``/``speci.py``/``pirep.py``/``radar.py``/``satellite.py``/
``lightning.py``/``surface.py``/``upper_air.py``/
``aircraft_observations.py``, plus per-source ``parser/decoder/
validator/interpreter`` subpackages) - real METAR/TAF/SIGMET parsing
and decoding already exists and is already real
(``awci.knowledge.icao.metar_decoder``/``taf_decoder``/
``sigmet_decoder``); rebuilding a second, parallel
``observations/metar/decoder.py`` would be pure duplication, not a
real gap. This module is exactly the one real, specific, missing
piece: a single, real place a caller reaches every already-real
fetcher through, instead of importing 4 separately-named modules from
2 different packages by hand.

Real sources aggregated - every one already a real, working, network-
calling connector, not built here:

- ``awci.knowledge.icao.live_source`` - real METAR/TAF (per station)
  and SIGMET (FIR-wide) fetch + decode, NOAA Aviation Weather Center.
- ``acf.connectors.pirep_reports.PIREPConnector`` - real Pilot Report
  fetch, NOAA aviationweather.gov.
- ``acf.connectors.nexrad_stations.NEXRADRadarConnector`` - real NEXRAD
  (WSR-88D) station operational-status fetch, api.weather.gov.
- ``acf.connectors.eumetsat_mtg.EUMETSATMTGConnector`` - real MTG FCI
  full-disk satellite quicklook fetch, EUMETSAT Data Store.

Deliberately NOT aggregated: ``acf.connectors.argo_floats`` (real, but
ocean buoys - not an aviation observation source);
``acf.connectors.live_connectors.LiveDataConnectorEngine`` (a
different, still-disclosed-unconnected registry of general NWP-model
data sources - ECMWF/NOAA-NOMADS/DWD/EUMETSAT-datastore/NASA/
Copernicus - every real fetch call still honestly returns
``NOT_SYNCED_NO_REAL_CONNECTION_ESTABLISHED``, confirmed by reading
that module before writing this one; not a real observation feed to
aggregate); ``acf.connectors.wmo_wis.WMOWISEngine`` (a real GTS/WIS 2.0
bulletin-HEADER parser given a header string, not a live fetcher - a
different real shape, out of scope for a "fetch current observations"
hub).

Every real per-source result already carries its own honest
``is_real_data``/``status``/``error`` fields (that discipline already
exists in each connector) - this hub never invents an aggregate
"all good" verdict; ``ObservationsSnapshot`` simply carries every real
per-source result unchanged, so a caller can inspect exactly which
real sources answered and which did not.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from acf.connectors.eumetsat_mtg import EUMETSATMTGConnector, MTGFetchResult
from acf.connectors.nexrad_stations import DEFAULT_STATIONS, NexradFetchResult, NEXRADRadarConnector
from acf.connectors.pirep_reports import DEFAULT_BBOX, PIREPConnector, PIREPFetchResult
from awci.knowledge.icao.live_source import LiveReport, LiveStationBundle, fetch_active_sigmets, fetch_and_decode_station


@dataclass
class ObservationsSnapshot:
    """
    Real, single snapshot of every real observation source this hub
    aggregates for one real ICAO station - each field is exactly the
    real, unmodified result object its own real connector already
    returns, so every real per-source honesty field
    (``is_real_data``/``status``/``.error``) survives unchanged.
    """

    icao_code: str
    station: LiveStationBundle
    sigmets: list[LiveReport]
    pireps: PIREPFetchResult
    radar: NexradFetchResult
    satellite: MTGFetchResult
    fetched_at: float = field(default_factory=time.time)


class ObservationsHub:
    """
    Real, single aggregation point over every real observation
    connector this module wraps - each real fetch is a thin, direct
    delegation to that source's own already-real, already-tested
    connector; this class computes nothing of its own.
    """

    def __init__(
        self,
        pirep_connector: PIREPConnector | None = None,
        radar_connector: NEXRADRadarConnector | None = None,
        satellite_connector: EUMETSATMTGConnector | None = None,
    ) -> None:
        #: Real connectors are constructed once and reused - injectable
        #: for real, deterministic tests (a caller can supply its own
        #: pre-configured/mocked connector instance) without this class
        #: needing to know that concern itself.
        self.pirep_connector = pirep_connector or PIREPConnector()
        self.radar_connector = radar_connector or NEXRADRadarConnector()
        self.satellite_connector = satellite_connector or EUMETSATMTGConnector()

    def fetch_station(self, icao_code: str, timeout: float = 8.0) -> LiveStationBundle:
        """Real METAR+TAF fetch+decode for one real station - direct
        delegation, see module docstring."""
        return fetch_and_decode_station(icao_code, timeout=timeout)

    def fetch_sigmets(self, timeout: float = 8.0) -> list[LiveReport]:
        """Real, FIR-wide active-SIGMET fetch - direct delegation."""
        return fetch_active_sigmets(timeout=timeout)

    def fetch_pireps(self, bbox: str = DEFAULT_BBOX) -> PIREPFetchResult:
        """Real Pilot Report fetch - direct delegation."""
        return self.pirep_connector.fetch_recent_reports(bbox=bbox)

    def fetch_radar_status(self, station_ids: tuple[str, ...] = DEFAULT_STATIONS) -> NexradFetchResult:
        """Real NEXRAD station operational-status fetch - direct
        delegation."""
        return self.radar_connector.fetch_station_status(station_ids=station_ids)

    def fetch_satellite_image(self) -> MTGFetchResult:
        """Real MTG FCI full-disk quicklook fetch - direct delegation."""
        return self.satellite_connector.fetch_latest_image()

    def fetch_all(
        self,
        icao_code: str,
        bbox: str = DEFAULT_BBOX,
        radar_station_ids: tuple[str, ...] = DEFAULT_STATIONS,
        timeout: float = 8.0,
    ) -> ObservationsSnapshot:
        """
        Real, single-call aggregation of every real source this hub
        wraps, for one real station - each real fetch already handles
        its own real network/HTTP failures internally (every connector
        this hub wraps is documented to never raise on a real,
        expected failure - a bad network, a down endpoint, missing
        credentials - only to report it honestly in its own result), so
        no additional error handling is added here.
        """
        return ObservationsSnapshot(
            icao_code=icao_code,
            station=self.fetch_station(icao_code, timeout=timeout),
            sigmets=self.fetch_sigmets(timeout=timeout),
            pireps=self.fetch_pireps(bbox=bbox),
            radar=self.fetch_radar_status(station_ids=radar_station_ids),
            satellite=self.fetch_satellite_image(),
        )
