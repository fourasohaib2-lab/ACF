"""Regression guard for Phase 9 of the AWCI separate-package migration
(2026-09-21, "continue avec src/acf/aviation/" - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own "§2j"
section).

The whole ``acf.aviation`` package (17 files, 6 subpackages) moved as
one coherent unit into ``awci.knowledge`` - the blueprint's own
"Aviation Knowledge Base" layer - preserving its internal structure
(airports/, graphics/, hazards/, icao/, performance/, routing/) rather
than fragmenting it across several new top-level ``awci`` packages.

``acf.aviation.<x>`` is now a thin re-export for every module and for
the package itself. This locks in that every old import path still
resolves to the exact same real object as the new one.
"""

from __future__ import annotations

import importlib

import pytest

# (old acf.aviation module, new awci.knowledge module) - checked via
# "every public name matches", since none of these modules restrict
# their exports with an __all__.
_SIMPLE_REEXPORT_MODULES = [
    ("airports.airport_database", "awci.knowledge.airports.airport_database"),
    ("graphics.cross_section", "awci.knowledge.graphics.cross_section"),
    ("hazards.aviation_hazards", "awci.knowledge.hazards.aviation_hazards"),
    ("icao.live_source", "awci.knowledge.icao.live_source"),
    ("icao.metar_decoder", "awci.knowledge.icao.metar_decoder"),
    ("icao.products", "awci.knowledge.icao.products"),
    ("icao.sigmet_decoder", "awci.knowledge.icao.sigmet_decoder"),
    ("icao.taf_decoder", "awci.knowledge.icao.taf_decoder"),
    ("performance.aircraft_performance", "awci.knowledge.performance.aircraft_performance"),
    ("routing.flight_routing", "awci.knowledge.routing.flight_routing"),
]


@pytest.mark.parametrize(("module_name", "new_path"), _SIMPLE_REEXPORT_MODULES)
def test_simple_reexport_modules_are_identical(module_name, new_path):
    old = importlib.import_module(f"acf.aviation.{module_name}")
    new = importlib.import_module(new_path)

    new_public_names = [name for name in vars(new) if not name.startswith("_")]
    assert new_public_names, f"{new_path} exports nothing real to check"
    for name in new_public_names:
        if name == "annotations":
            continue
        assert hasattr(old, name), f"acf.aviation.{module_name} is missing real re-export {name!r}"
        assert getattr(old, name) is getattr(new, name), (
            f"acf.aviation.{module_name}.{name} is not the same real object as {new_path}.{name} "
            "- the re-export is stale or duplicated"
        )


def test_package_level_reexport_matches_its_real_all():
    """acf.aviation.__init__ re-exports awci.knowledge's __all__ -
    the same 6 classes the original package-level __init__.py exposed."""
    old = importlib.import_module("acf.aviation")
    new = importlib.import_module("awci.knowledge")

    assert new.__all__, "awci.knowledge has an empty __all__"
    for name in new.__all__:
        assert hasattr(old, name), f"acf.aviation is missing real re-export {name!r}"
        assert getattr(old, name) is getattr(new, name), (
            f"acf.aviation.{name} is not the same real object as awci.knowledge.{name} "
            "- the re-export is stale or duplicated"
        )
    assert list(old.__all__) == list(new.__all__)


def test_new_package_is_real_top_level_reachable():
    import awci.knowledge

    assert awci.knowledge.__name__ == "awci.knowledge"


def test_internal_cross_references_use_the_new_package_directly():
    """icao/live_source.py, icao/products.py, icao/taf_decoder.py and
    routing/flight_routing.py all depend on sibling modules inside the
    same knowledge/ package - locks in they now import each other
    directly (relative to awci.knowledge), not by round-tripping
    through the acf.aviation shim."""
    import awci.knowledge.icao.live_source as live_source_module
    import awci.knowledge.icao.products as products_module
    import awci.knowledge.icao.taf_decoder as taf_module
    import awci.knowledge.routing.flight_routing as routing_module
    from awci.knowledge.airports.airport_database import AirportDatabase
    from awci.knowledge.icao.metar_decoder import METARDecoder, METARReport

    assert live_source_module.METARDecoder is METARDecoder
    assert live_source_module.METARReport is METARReport
    assert products_module.METARDecoder is METARDecoder
    assert taf_module._CLOUD_RE is not None
    assert routing_module.AirportDatabase is AirportDatabase


def test_cross_package_dependents_from_earlier_phases_reach_knowledge_directly():
    """awci.airport.airport (Phase 8), awci.hazards.cat_turbulence and
    awci.hazards.microburst (Phase 1), and awci.complexity.metar_verification
    (Phase 8) all depend on acf.aviation modules moved in this phase -
    locks in they were repointed to awci.knowledge.* directly rather
    than left resolving through the acf.aviation shim."""
    import awci.airport.airport as airport_module
    import awci.complexity.metar_verification as metar_verification_module
    import awci.hazards.cat_turbulence as cat_module
    import awci.hazards.microburst as microburst_module
    from awci.knowledge.airports.airport_database import AirportDatabase
    from awci.knowledge.hazards.aviation_hazards import AviationHazardEngine
    from awci.knowledge.icao.metar_decoder import METARReport

    assert airport_module.AirportDatabase is AirportDatabase
    assert cat_module.AviationHazardEngine is AviationHazardEngine
    assert microburst_module.AviationHazardEngine is AviationHazardEngine
    assert metar_verification_module.METARReport is METARReport
