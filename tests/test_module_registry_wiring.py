"""
Tests for acf.gui.esoc.module_registry.ModuleRegistry's own real
class-wiring correctness (added 2026-09-04, "continue" - a systemic
bug found via a broad audit: 19 of this registry's 25
_safe_import_register() calls named a class that genuinely does not
exist at the given path, and the old fallback silently substituted the
bare, empty package module for is_connected()'s own real check,
reporting these as "connected" when nothing real had ever been
instantiated - see module_registry.py's own module docstring for the
full disclosure).

ModuleRegistry() takes ~2s to construct (it really initializes an
HPCConnectionManager, which really attempts an SSH probe) - built once
per test module via a session-scoped fixture rather than once per
test.
"""

import types

import pytest

from acf.gui.esoc.module_registry import ModuleRegistry

#: The 15 registrations found broken and fixed this closure - each
#: must now resolve to a REAL instance of a REAL class, not the old
#: silently-substituted bare module.
_FIXED_REGISTRATIONS: dict[str, str] = {
    "data_assimilation": "EarthAnalysisStateVector",
    "digital_twin": "DigitalTwinEngine",
    "ai_expert": "EarthSystemExpert",
    "monitoring": "MonitoringRegistry",
    "catalog": "CatalogManager",
    "plugins": "PluginManager",
    "forecast": "ForecastEngine",
    "hydrology": "HydrologyReasoningEngine",
    "air_quality": "AirQualityReasoningEngine",
    "production_dashboard": "DashboardManager",
    "visualization": "AIForecastDashboard",
    "planetary_limits": "PlanetaryBoundariesSimulator",
    "aerosols_dust": "CloudAerosolEngine",
    "volcanoes": "VolcanicPhysicsEngine",
    "reports_generator": "BriefingGenerator",
}

#: The 4 registrations with no single real class anywhere that
#: unambiguously represents "the" engine for that whole domain - must
#: now honestly report as NOT connected (None), never a fabricated
#: "connected" bare-module stand-in.
_HONESTLY_UNCONNECTED = ("earth_physics", "space_weather", "geoengineering", "geology")


@pytest.fixture(scope="module")
def registry():
    return ModuleRegistry()


def test_all_15_fixed_registrations_resolve_to_their_real_named_class(registry):
    for key, expected_class_name in _FIXED_REGISTRATIONS.items():
        instance = registry.get_module(key)
        assert instance is not None, f"{key} should be connected to a real instance"
        assert type(instance).__name__ == expected_class_name, (
            f"{key} resolved to {type(instance).__name__!r}, expected {expected_class_name!r}"
        )


def test_the_4_genuinely_unresolvable_domains_are_honestly_not_connected(registry):
    """These 4 named a class that never existed and has no single real
    replacement (each domain is a real package of many independent
    engines, not one orchestrator) - must be None, not the old
    fabricated "connected to a bare module" outcome."""
    for key in _HONESTLY_UNCONNECTED:
        assert registry.is_connected(key) is False
        assert registry.get_module(key) is None


def test_no_registered_module_is_a_bare_package_module_object(registry):
    """Direct regression guard for the root-cause bug: nothing in
    self.modules should ever be a raw `types.ModuleType` - either a
    real instantiated class, or honestly None."""
    for key, instance in registry.modules.items():
        assert not isinstance(instance, types.ModuleType), (
            f"{key} is a bare module object ({instance!r}) - _safe_import_register()'s "
            "fallback bug has regressed"
        )


def test_system_status_summary_connected_count_matches_is_connected(registry):
    summary = registry.get_system_status_summary()
    real_connected_count = sum(1 for k in registry.modules if registry.is_connected(k))
    assert summary["connected_count"] == real_connected_count
    assert summary["connected_count"] >= 40  # 44 measured at the time this test was written


def test_safe_import_register_logs_a_warning_not_a_swallowed_debug_line(registry, caplog):
    """Real regression guard: a missing class must be loud (WARNING),
    not silently swallowed at DEBUG as it used to be - see
    _safe_import_register()'s own NOTE (correction)."""
    import logging

    with caplog.at_level(logging.WARNING, logger="acf.gui.esoc.module_registry"):
        registry._safe_import_register("_test_missing_class_key", "acf.gui.esoc.module_registry", "NoSuchClass")

    assert registry.modules["_test_missing_class_key"] is None
    assert any("does not exist" in record.message for record in caplog.records)


def test_safe_import_register_honestly_reports_a_construction_failure(registry, caplog):
    """A real class that exists but whose constructor raises must also
    honestly resolve to None, not propagate the exception or silently
    substitute the bare module."""
    import logging

    class _AlwaysRaisesOnInit:
        def __init__(self):
            raise RuntimeError("real construction failure")

    import acf.gui.esoc.module_registry as module_registry_module

    setattr(module_registry_module, "_TestAlwaysRaisesOnInit", _AlwaysRaisesOnInit)
    try:
        with caplog.at_level(logging.WARNING, logger="acf.gui.esoc.module_registry"):
            registry._safe_import_register(
                "_test_construction_failure_key", "acf.gui.esoc.module_registry", "_TestAlwaysRaisesOnInit"
            )
        assert registry.modules["_test_construction_failure_key"] is None
        assert any("construction failed" in record.message for record in caplog.records)
    finally:
        delattr(module_registry_module, "_TestAlwaysRaisesOnInit")
