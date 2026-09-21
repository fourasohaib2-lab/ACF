"""Regression guard for Phase 8 of the AWCI separate-package migration
(2026-09-21, "continue automatiquement pour les 22 modules un par un" -
see docs/architecture/acf_awci_architecture_gap_analysis.md's own
"§2i" section).

The largest single phase: 21 remaining real modules from acf.awci
moved in one batch, split across 5 target packages based on their
real dependency graph and role (not name similarity alone):
- awci.airport/ (new): airport.py
- awci.comparison/ (new): multi_model_fusion.py, regridding.py
- awci.data/: model_import.py, model_import_cross_section.py,
  model_import_evolution.py
- awci.hazards/: terrain_elevation.py
- awci.complexity/: the other 14 (calibration, config_loader,
  diagnostic_registry, execution_report, forecaster_validation,
  input_adapter, metar_verification, method_comparison, path_sampling,
  pipeline, result, run_report, validation_cases, workstation_fields)

acf.awci.<module> is now a thin re-export for every one of the 21.
This locks in that every old import path still resolves to the exact
same real object as the new one.
"""

from __future__ import annotations

import importlib

import pytest

# Modules without their own __all__ - checked via "every public name matches".
_SIMPLE_REEXPORT_MODULES = [
    ("airport", "awci.airport.airport"),
    ("calibration", "awci.complexity.calibration"),
    ("config_loader", "awci.complexity.config_loader"),
    ("diagnostic_registry", "awci.complexity.diagnostic_registry"),
    ("execution_report", "awci.complexity.execution_report"),
    ("forecaster_validation", "awci.complexity.forecaster_validation"),
    ("input_adapter", "awci.complexity.input_adapter"),
    ("metar_verification", "awci.complexity.metar_verification"),
    ("method_comparison", "awci.complexity.method_comparison"),
    ("multi_model_fusion", "awci.comparison.multi_model_fusion"),
    ("path_sampling", "awci.complexity.path_sampling"),
    ("pipeline", "awci.complexity.pipeline"),
    ("result", "awci.complexity.result"),
    ("run_report", "awci.complexity.run_report"),
    ("terrain_elevation", "awci.hazards.terrain_elevation"),
    ("validation_cases", "awci.complexity.validation_cases"),
    ("workstation_fields", "awci.complexity.workstation_fields"),
]

# Modules with a real __all__ - checked against that explicit list, since
# `import *` deliberately excludes anything not in __all__ (by design, not
# a migration artifact).
_ALL_RESTRICTED_MODULES = [
    ("model_import", "awci.data.model_import"),
    ("model_import_cross_section", "awci.data.model_import_cross_section"),
    ("model_import_evolution", "awci.data.model_import_evolution"),
]


@pytest.mark.parametrize(("module_name", "new_path"), _SIMPLE_REEXPORT_MODULES)
def test_simple_reexport_modules_are_identical(module_name, new_path):
    old = importlib.import_module(f"acf.awci.{module_name}")
    new = importlib.import_module(new_path)

    new_public_names = [name for name in vars(new) if not name.startswith("_")]
    assert new_public_names, f"{new_path} exports nothing real to check"
    for name in new_public_names:
        if name == "annotations":
            continue
        assert hasattr(old, name), f"acf.awci.{module_name} is missing real re-export {name!r}"
        assert getattr(old, name) is getattr(new, name), (
            f"acf.awci.{module_name}.{name} is not the same real object as {new_path}.{name} "
            "- the re-export is stale or duplicated"
        )


@pytest.mark.parametrize(("module_name", "new_path"), _ALL_RESTRICTED_MODULES)
def test_all_restricted_modules_reexport_their_real_public_api(module_name, new_path):
    old = importlib.import_module(f"acf.awci.{module_name}")
    new = importlib.import_module(new_path)

    assert new.__all__, f"{new_path} has an empty __all__"
    for name in new.__all__:
        assert hasattr(old, name), f"acf.awci.{module_name} is missing real re-export {name!r}"
        assert getattr(old, name) is getattr(new, name), (
            f"acf.awci.{module_name}.{name} is not the same real object as {new_path}.{name} "
            "- the re-export is stale or duplicated"
        )


def test_regridding_shim_also_reexports_the_private_helpers_its_own_whitebox_tests_need():
    """test_regridding.py imports _cell_edges_latitude/_natural_edges
    by name - real internal helpers exercised directly by a real
    whitebox test of the conservative-regridding math. `import *`
    alone never re-exports underscore names, so the shim adds these
    two explicitly - this locks in that decision."""
    from acf.awci.regridding import _cell_edges_latitude, _natural_edges
    from awci.comparison.regridding import _cell_edges_latitude as new_edges
    from awci.comparison.regridding import _natural_edges as new_natural

    assert _cell_edges_latitude is new_edges
    assert _natural_edges is new_natural


def test_new_packages_created_this_phase_are_real_top_level_reachable():
    import awci.airport
    import awci.comparison

    assert awci.airport.__name__ == "awci.airport"
    assert awci.comparison.__name__ == "awci.comparison"


def test_cross_package_hazard_dependents_reach_the_moved_modules_correctly():
    """cat_turbulence.py (Phase 1, awci.hazards) depends on
    workstation_fields.py (this phase, awci.complexity) and
    microburst.py (Phase 1) depends on normalizer.py (Phase 2,
    awci.complexity) - both cross-package references found and fixed
    during this phase; locks in they resolve to the real objects."""
    import awci.hazards.cat_turbulence as cat_module
    import awci.hazards.microburst as microburst_module
    from awci.complexity.normalizer import Normalizer
    from awci.complexity.workstation_fields import real_grid_spacing_m

    assert cat_module.real_grid_spacing_m is real_grid_spacing_m
    assert microburst_module.Normalizer is Normalizer
