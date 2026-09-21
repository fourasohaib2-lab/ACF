"""Regression guard for item 10 of "on les attaque toutes un par un"
(2026-09-21 - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own "§2x"
section): the real, aviation-relevant subset of ``acf.connectors``
(``pirep_reports.py``, ``nexrad_stations.py``, ``eumetsat_mtg.py`` -
already reused by ``awci.observations.hub.ObservationsHub``) moved to
``awci.data.connectors``.

``argo_floats.py`` (ocean, not aviation), ``wmo_wis.py`` (generic
GTS/WIS bulletin-header parser) and ``live_connectors.py`` (generic,
disclosed-unconnected NWP-model registry) deliberately stay under
``acf.connectors`` - not aviation-specific, so out of scope for
``awci.data.connectors``.

``acf.connectors.<x>`` is now a thin re-export for each of the 3
moved modules. This locks in that every old import path still resolves
to the exact same real object as the new one.
"""

from __future__ import annotations

import importlib

import pytest

# (old acf.connectors module, new awci.data.connectors module, the
# shim's own __all__ - explicit, since these modules also import
# stdlib/third-party names like `time`/`dataclass`/`requests` at
# top-of-file that are not part of the real public API to check).
_SIMPLE_REEXPORT_MODULES = [
    ("pirep_reports", "awci.data.connectors.pirep_reports", ("BASE_URL", "DEFAULT_BBOX", "PIREPConnector", "PIREPFetchResult")),
    (
        "nexrad_stations",
        "awci.data.connectors.nexrad_stations",
        ("BASE_URL", "DEFAULT_STATIONS", "NEXRADRadarConnector", "NexradFetchResult"),
    ),
    (
        "eumetsat_mtg",
        "awci.data.connectors.eumetsat_mtg",
        (
            "EUMETSATMTGConnector",
            "MTGFetchResult",
            "MTG_FCI_HIGH_RESOLUTION",
            "MTG_FCI_NORMAL_RESOLUTION",
            "MTG_SATELLITE_HEIGHT_M",
            "MTG_SUBSATELLITE_LONGITUDE_DEG",
            "SEARCH_URL",
            "TOKEN_URL",
        ),
    ),
]


@pytest.mark.parametrize(("module_name", "new_path", "public_names"), _SIMPLE_REEXPORT_MODULES)
def test_simple_reexport_modules_are_identical(module_name, new_path, public_names):
    old = importlib.import_module(f"acf.connectors.{module_name}")
    new = importlib.import_module(new_path)

    for name in public_names:
        assert hasattr(new, name), f"{new_path} is missing real attribute {name!r}"
        assert hasattr(old, name), f"acf.connectors.{module_name} is missing real re-export {name!r}"
        assert getattr(old, name) is getattr(new, name), (
            f"acf.connectors.{module_name}.{name} is not the same real object as {new_path}.{name} "
            "- the re-export is stale or duplicated"
        )


def test_new_package_is_real_top_level_reachable():
    import awci.data.connectors

    assert awci.data.connectors.__name__ == "awci.data.connectors"


def test_not_aviation_specific_connectors_were_deliberately_left_in_place():
    """argo_floats/wmo_wis/live_connectors are real, but not
    aviation-specific - they must remain real modules under
    acf.connectors, not thin shims pointing at awci.data.connectors
    (which has no such modules)."""
    import acf.connectors.argo_floats as argo_module
    import acf.connectors.live_connectors as live_module
    import acf.connectors.wmo_wis as wis_module

    assert hasattr(argo_module, "ArgoFloatsConnector")
    assert hasattr(live_module, "LiveDataConnectorEngine")
    assert hasattr(wis_module, "WMOWISEngine")

    import importlib.util

    assert importlib.util.find_spec("awci.data.connectors.argo_floats") is None
    assert importlib.util.find_spec("awci.data.connectors.live_connectors") is None
    assert importlib.util.find_spec("awci.data.connectors.wmo_wis") is None


def test_cross_package_dependents_reach_the_new_location_directly():
    """awci.observations.hub (built in this same "on les attaque"
    sequence) and acf.gui.map.mtg_basemap both depend on the moved
    connectors - locks in they were repointed to
    awci.data.connectors.* directly rather than left resolving through
    the acf.connectors shim."""
    import acf.gui.map.mtg_basemap as mtg_basemap_module
    import awci.observations.hub as hub_module
    from awci.data.connectors.eumetsat_mtg import EUMETSATMTGConnector
    from awci.data.connectors.nexrad_stations import NEXRADRadarConnector
    from awci.data.connectors.pirep_reports import PIREPConnector

    assert hub_module.EUMETSATMTGConnector is EUMETSATMTGConnector
    assert hub_module.NEXRADRadarConnector is NEXRADRadarConnector
    assert hub_module.PIREPConnector is PIREPConnector
    assert mtg_basemap_module.EUMETSATMTGConnector is EUMETSATMTGConnector


def test_moved_connectors_are_importable_with_no_circular_dependency():
    """Fresh-process-style sanity check: importing all 3 new modules
    together, plus their old shims, must not raise."""
    import acf.connectors.eumetsat_mtg  # noqa: F401
    import acf.connectors.nexrad_stations  # noqa: F401
    import acf.connectors.pirep_reports  # noqa: F401
    import awci.data.connectors.eumetsat_mtg  # noqa: F401
    import awci.data.connectors.nexrad_stations  # noqa: F401
    import awci.data.connectors.pirep_reports  # noqa: F401
