"""
Atmospheric Complexity Framework (ACF)

AWCI Data Connectors (``src/awci/data/connectors/``)

Migrated 2026-09-21 (item 10 of "on les attaque toutes un par un" -
see ``docs/architecture/acf_awci_architecture_gap_analysis.md``) from
``acf.connectors``. Real, physically moved: ``pirep_reports.py`` (real
NOAA Aviation Weather Center PIREP connector), ``nexrad_stations.py``
(real NEXRAD radar station connector), ``eumetsat_mtg.py`` (real
EUMETSAT MTG FCI connector) - the 3 real ``acf.connectors`` modules
already reused by ``awci.observations.hub.ObservationsHub``, i.e. the
ones already established as genuinely aviation/AWCI-relevant.
``acf.connectors.<x>`` is kept as a real backward-compatible
re-export for all 3.

Deliberately NOT migrated: ``argo_floats.py`` (ocean buoy data - not
aviation, already excluded from ``ObservationsHub`` for the same
reason); ``wmo_wis.py`` (a generic WMO GTS/WIS bulletin-header parser
covering all WMO data types, not aviation-specific, and already
disclosed as not a live fetcher); ``live_connectors.py``
(``LiveDataConnectorEngine`` - a generic, disclosed-unconnected NWP
model-data registry spanning ECMWF/NOAA/DWD/EUMETSAT/NASA/Copernicus,
not aviation-specific). These 3 remain real, general-purpose ACF
connectors under ``acf.connectors``, not part of AWCI's own data
layer.

``docs/architecture/awci_reference_architecture.md`` section on
``awci/data/connectors/`` additionally names ``acf.py``/``grib.py``/
``fa.py``/``lfa.py``/``netcdf.py``/``metar.py``/``speci.py``/
``taf.py``/``sigmet.py``/``airmet.py``/``radar.py``/``satellite.py``/
``lightning.py``/``notam.py`` - a file-format/product-per-file layout
different from this codebase's real network-connector-per-source
layout. METAR/TAF/SIGMET decoding already exists as real code under
``awci.knowledge.icao`` (moved from ``acf.aviation.icao`` in Phase 9);
GRIB/FA/LFA/NetCDF model-file ingestion already exists as real code
under ``awci.data.archive_field``/``model_import*``; AIRMET/NOTAM/
lightning connectors do not exist anywhere in this codebase and are
not fabricated here.
"""

from __future__ import annotations
