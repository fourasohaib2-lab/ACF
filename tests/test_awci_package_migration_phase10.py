"""Regression guard for Phase 10 of the AWCI separate-package migration
(2026-09-21, "continue avec le tableau de bord GUI" - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own "§2k"
section).

The real AWCI dashboard - 29 ``awci_*.py`` modules under
``acf.gui.dashboard`` (map, alerts, hazards, cross-section, vertical
profile, situation panel, messages, execution report, and the
top-level ``AWCIDashboard``/``AWCIDashboardWindow``) - moved as a
whole into a new ``awci.dashboard`` package, the blueprint's own
"application layer above everything else".

``acf.gui.dashboard.awci_<x>`` is now a thin re-export for every
module. This locks in that every old import path still resolves to
the exact same real object as the new one, including the handful of
private names several real whitebox tests import directly.
"""

from __future__ import annotations

import importlib

import pytest

_MODULES = [
    "awci_alert_history",
    "awci_alerts_panel",
    "awci_colors",
    "awci_component_detail",
    "awci_cross_section",
    "awci_dashboard",
    "awci_decomposition",
    "awci_evolution_chart",
    "awci_execution_report_dialog",
    "awci_footer",
    "awci_footer_summary",
    "awci_gauge",
    "awci_hazard_row",
    "awci_map_panel",
    "awci_messages_panel",
    "awci_model_spread_chart",
    "awci_radar",
    "awci_risk_summary",
    "awci_route_chart",
    "awci_sidebar",
    "awci_situation_panel",
    "awci_stats_bar",
    "awci_synthetic_field",
    "awci_timeline",
    "awci_toast",
    "awci_topbar",
    "awci_vertical_profile",
    "awci_volume_3d",
    "awci_window",
]

_PRIVATE_EXTRAS = {
    "awci_dashboard": [
        "_FLIGHT_LEVEL_SELECTOR_OPTIONS_HPA",
        "_POINT_OF_INTEREST",
        "_ALL_VERTICAL_PROFILE_LEVELS_HPA",
        "_AIRPORTS",
        "_REGIONAL_ROUTE",
        "_ModelConsensusWorker",
        "_REGIONAL_CITY_LABELS",
        "_ModelDisagreementFieldWorker",
        "_ModelVerticalProfilesWorker",
    ],
    "awci_synthetic_field": ["_synthetic_inputs"],
    "awci_topbar": ["_ElidingLabel"],
    "awci_cross_section": ["_hpa_to_ft"],
    "awci_radar": ["_AXES"],
}


@pytest.mark.parametrize("module_name", _MODULES)
def test_dashboard_modules_are_identical(module_name):
    old = importlib.import_module(f"acf.gui.dashboard.{module_name}")
    new = importlib.import_module(f"awci.dashboard.{module_name}")

    new_public_names = [name for name in vars(new) if not name.startswith("_")]
    assert new_public_names, f"awci.dashboard.{module_name} exports nothing real to check"
    for name in new_public_names:
        if name == "annotations":
            continue
        assert hasattr(old, name), f"acf.gui.dashboard.{module_name} is missing real re-export {name!r}"
        assert getattr(old, name) is getattr(new, name), (
            f"acf.gui.dashboard.{module_name}.{name} is not the same real object as "
            f"awci.dashboard.{module_name}.{name} - the re-export is stale or duplicated"
        )


@pytest.mark.parametrize(
    ("module_name", "private_name"),
    [(mod, name) for mod, names in _PRIVATE_EXTRAS.items() for name in names],
)
def test_dashboard_shims_reexport_the_private_names_their_own_whitebox_tests_need(module_name, private_name):
    """Several real GUI tests import an underscore-prefixed constant or
    class directly from the old acf.gui.dashboard.awci_* path (e.g.
    _AIRPORTS, _ModelConsensusWorker, _ElidingLabel) - `import *` alone
    never re-exports those by design, so each shim adds them
    explicitly. This locks in that decision for all 13 private names
    across the 5 modules that need it."""
    old = importlib.import_module(f"acf.gui.dashboard.{module_name}")
    new = importlib.import_module(f"awci.dashboard.{module_name}")

    assert hasattr(old, private_name), f"acf.gui.dashboard.{module_name} is missing private re-export {private_name!r}"
    assert getattr(old, private_name) is getattr(new, private_name)


def test_new_package_is_real_top_level_reachable():
    import awci.dashboard

    assert awci.dashboard.__name__ == "awci.dashboard"


def test_internal_cross_references_use_the_new_package_directly():
    """awci_dashboard.py imports ~20 sibling dashboard modules directly;
    locks in they resolve through awci.dashboard.* now, not by
    round-tripping through the acf.gui.dashboard shim."""
    import awci.dashboard.awci_alerts_panel as alerts_module
    import awci.dashboard.awci_dashboard as dashboard_module
    from awci.dashboard.awci_alerts_panel import AWCIAlertsDialog
    from awci.dashboard.awci_map_panel import AWCIMapPanel

    assert dashboard_module.AWCIAlertsDialog is AWCIAlertsDialog
    assert dashboard_module.AWCIMapPanel is AWCIMapPanel
    assert alerts_module.AWCIAlertsDialog is AWCIAlertsDialog


def test_cross_package_references_to_already_migrated_awci_code_are_direct():
    """awci_component_detail.py, awci_dashboard.py, awci_synthetic_field.py
    and others depend on already-migrated awci.complexity/awci.hazards/
    awci.data modules (previously reached via the acf.awci shim) and on
    awci.knowledge.icao (previously acf.aviation.icao) - locks in these
    are now direct cross-package imports within the awci top-level tree."""
    import awci.dashboard.awci_component_detail as component_detail_module
    import awci.dashboard.awci_dashboard as dashboard_module
    import awci.dashboard.awci_synthetic_field as synthetic_field_module
    from awci.complexity.calculator import AWCICalculator
    from awci.complexity.diagnostic_registry import DIAGNOSTIC_REGISTRY
    from awci.complexity.weights import WeightsManager

    assert component_detail_module.DIAGNOSTIC_REGISTRY is DIAGNOSTIC_REGISTRY
    assert component_detail_module.WeightsManager is WeightsManager
    assert dashboard_module.AWCICalculator is AWCICalculator
    assert synthetic_field_module.AWCICalculator is AWCICalculator
