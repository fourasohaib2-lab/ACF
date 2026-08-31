"""
Tests for ACF-018 Dependency Graph Optimization & Architecture Hardening
"""

import importlib


def test_canonical_imports_clean():
    mod_params = importlib.import_module("acf.parameters")
    mod_importers = importlib.import_module("acf.importers")
    mod_maps = importlib.import_module("acf.maps")
    assert mod_params is not None
    assert mod_importers is not None
    assert mod_maps is not None


def test_legacy_imports_clean():
    mod_io = importlib.import_module("acf.io")
    mod_vis = importlib.import_module("acf.visualization")
    assert mod_io is not None
    assert mod_vis is not None


def test_maps_no_longer_depends_on_visualization():
    import sys

    # Clear cached modules to test clean import graph
    for mod in list(sys.modules.keys()):
        if mod.startswith("acf.visualization"):
            del sys.modules[mod]

    # Import acf.maps and ensure acf.visualization is not pulled in
    importlib.import_module("acf.maps.map_engine")
    importlib.import_module("acf.maps.visualization_manager")
    importlib.import_module("acf.maps.data_renderer")

    assert "acf.visualization.renderer" not in sys.modules
    assert "acf.visualization.layer_manager" not in sys.modules


def test_search_and_aliases_no_circular_import():
    from acf.parameters.aliases import ParameterAliases
    from acf.parameters.search import ParameterSearch

    aliases = ParameterAliases()
    aliases.add("t2m", "TMP")
    assert aliases.resolve("t2m") == "TMP"

    from acf.parameters.registry import ParameterRegistry

    registry = ParameterRegistry()
    search = ParameterSearch(registry)
    assert search is not None
