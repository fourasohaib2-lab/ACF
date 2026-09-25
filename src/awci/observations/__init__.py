"""
Atmospheric Complexity Framework (ACF)

Aviation Observation Hub (``src/awci/observations/``)

Real, single aggregation point over already-real observation
connectors - see ``hub.py``'s own docstring for the full scope
disclosure (what is aggregated, what is deliberately not, and why).
Only ``hub.py`` is built - the blueprint's own full 11-file package
(``stations.py``/``metar.py``/``speci.py``/``pirep.py``/``radar.py``/
``satellite.py``/``lightning.py``/``surface.py``/``upper_air.py``/
``aircraft_observations.py``, plus per-source subpackages) is not,
since real METAR/TAF/SIGMET/PIREP/radar/satellite fetching and
decoding already exists elsewhere in this codebase - honestly
disclosed, not fabricated as built.
"""

from __future__ import annotations

from awci.observations.hub import ObservationsHub, ObservationsSnapshot

__all__ = ["ObservationsHub", "ObservationsSnapshot"]
